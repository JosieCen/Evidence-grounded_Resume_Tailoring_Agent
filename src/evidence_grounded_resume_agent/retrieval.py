from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Protocol, Sequence

from .models import Claim, Match, Requirement
from .tools import expand_tokens, tokenize


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class TextEmbedder(Protocol):
    """Minimal embedding contract used by semantic retrieval."""

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        ...


class SentenceTransformerEmbedder:
    """Lazy Sentence Transformers adapter.

    The dependency is optional so the default lexical demo remains lightweight.
    """

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                'Embedding retrieval requires the optional dependency. '
                'Install it with: pip install -e ".[embedding]"'
            ) from exc
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [[float(value) for value in vector] for vector in vectors]


@dataclass(frozen=True)
class RetrievalConfig:
    mode: str = "lexical"
    top_k: int = 3
    lexical_weight: float = 0.35
    semantic_weight: float = 0.65
    min_semantic_score: float = 0.28
    strong_semantic_score: float = 0.55
    min_hybrid_score: float = 0.20
    strong_hybrid_score: float = 0.45

    def __post_init__(self) -> None:
        if self.mode not in {"lexical", "embedding", "hybrid"}:
            raise ValueError(f"Unsupported retrieval mode: {self.mode}")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if self.mode == "hybrid" and not math.isclose(
            self.lexical_weight + self.semantic_weight, 1.0, abs_tol=1e-6
        ):
            raise ValueError("Hybrid lexical_weight + semantic_weight must equal 1.0")


def _claim_search_text(claim: Claim) -> str:
    return " ".join([claim.text, *claim.tags])


def _lexical_features(requirement: Requirement, claim: Claim) -> tuple[float, list[str]]:
    req_tokens = expand_tokens(requirement.tokens)
    claim_tokens = expand_tokens(tokenize(_claim_search_text(claim)))
    overlap = sorted(req_tokens.intersection(claim_tokens))
    if not overlap:
        return 0.0, []
    denominator = max(3, min(len(req_tokens), 10))
    return min(1.0, len(overlap) / denominator), overlap


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding vectors must have the same dimension")
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return max(0.0, min(1.0, numerator / (left_norm * right_norm)))


def _semantic_scores(
    requirements: list[Requirement],
    claims: dict[str, Claim],
    embedder: TextEmbedder,
) -> dict[tuple[str, str], float]:
    claim_items = list(claims.items())
    texts = [item.text for item in requirements] + [_claim_search_text(claim) for _, claim in claim_items]
    vectors = embedder.encode(texts)
    if len(vectors) != len(texts):
        raise ValueError("Embedder returned a different number of vectors than input texts")

    req_vectors = vectors[: len(requirements)]
    claim_vectors = vectors[len(requirements) :]
    scores: dict[tuple[str, str], float] = {}
    for req_index, requirement in enumerate(requirements):
        for claim_index, (claim_id, _) in enumerate(claim_items):
            scores[(requirement.id, claim_id)] = cosine_similarity(
                req_vectors[req_index], claim_vectors[claim_index]
            )
    return scores


def match_requirements(
    requirements: list[Requirement],
    claims: dict[str, Claim],
    *,
    config: RetrievalConfig | None = None,
    embedder: TextEmbedder | None = None,
) -> list[Match]:
    """Rank authorized claims for each requirement using lexical, embedding, or hybrid retrieval."""

    config = config or RetrievalConfig()
    if config.mode in {"embedding", "hybrid"} and embedder is None:
        raise ValueError(f"Retrieval mode '{config.mode}' requires an embedder")

    semantic = (
        _semantic_scores(requirements, claims, embedder)
        if embedder is not None and config.mode in {"embedding", "hybrid"}
        else {}
    )

    matches: list[Match] = []
    for requirement in requirements:
        ranked: list[dict[str, object]] = []
        for claim_id, claim in claims.items():
            lexical_score, overlap = _lexical_features(requirement, claim)
            semantic_score = semantic.get((requirement.id, claim_id), 0.0)

            if config.mode == "lexical":
                combined_score = lexical_score
                include = lexical_score > 0
            elif config.mode == "embedding":
                combined_score = semantic_score
                include = semantic_score >= config.min_semantic_score
            else:
                combined_score = (
                    config.lexical_weight * lexical_score
                    + config.semantic_weight * semantic_score
                )
                include = combined_score >= config.min_hybrid_score and (
                    lexical_score > 0 or semantic_score >= config.min_semantic_score
                )

            if not include:
                continue
            ranked.append(
                {
                    "claim_id": claim_id,
                    "lexical_score": round(lexical_score, 4),
                    "semantic_score": round(semantic_score, 4),
                    "combined_score": round(combined_score, 4),
                    "overlap_tokens": overlap,
                }
            )

        ranked.sort(
            key=lambda item: (
                -float(item["combined_score"]),
                -float(item["semantic_score"]),
                -float(item["lexical_score"]),
                str(item["claim_id"]),
            )
        )
        selected = ranked[: config.top_k]

        if not selected:
            level = "GAP"
        else:
            top = selected[0]
            if config.mode == "lexical":
                is_strong = float(top["lexical_score"]) >= 0.45 or len(top["overlap_tokens"]) >= 3
            elif config.mode == "embedding":
                is_strong = float(top["semantic_score"]) >= config.strong_semantic_score
            else:
                is_strong = float(top["combined_score"]) >= config.strong_hybrid_score
            level = "STRONG_MATCH" if is_strong else "PARTIAL_MATCH"

        matches.append(
            Match(
                requirement_id=requirement.id,
                requirement_text=requirement.text,
                match_level=level,
                source_claim_ids=[str(item["claim_id"]) for item in selected],
                overlap_tokens=list(selected[0]["overlap_tokens"]) if selected else [],
                retrieval_mode=config.mode,
                top_score=float(selected[0]["combined_score"]) if selected else 0.0,
                candidate_scores=[dict(item) for item in selected],
            )
        )
    return matches
