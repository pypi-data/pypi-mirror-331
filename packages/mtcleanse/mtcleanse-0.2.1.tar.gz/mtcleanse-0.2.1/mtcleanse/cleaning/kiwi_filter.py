"""Quality filtering using the Unbabel CometKiwi model.

This module provides a class for estimating the quality of translations
without reference translations using Unbabel's CometKiwi model.
"""

import logging
import statistics
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

# Handle ImportError gracefully
try:
    from comet import download_model, load_from_checkpoint
except ImportError:
    download_model = None
    load_from_checkpoint = None

logger = logging.getLogger("mtcleanse")


class KiwiQualityFilter:
    """Quality filter using Unbabel's CometKiwi model for reference-less quality estimation.

    This class uses CometKiwi to estimate the quality of translations without
    reference translations, using the source text and hypothesis (translation) only.

    The model outputs scores in the range [0, 1], with higher scores indicating better quality.
    """

    def __init__(
        self,
        model_name: str = "Unbabel/wmt22-cometkiwi-da",
        threshold: float = 0.5,
        batch_size: int = 8,
        device: Optional[str] = None,
    ):
        """Initialize the KiwiQualityFilter.

        Args:
            model_name: Name of the CometKiwi model to use
            threshold: Quality threshold (0-1, higher = better quality)
            batch_size: Batch size for processing
            device: Device to run the model on ('cpu' or 'cuda')

        Raises:
            ImportError: If the 'comet' package is not installed
        """
        self.model_name = model_name
        self.threshold = threshold
        self.batch_size = batch_size

        if download_model is None or load_from_checkpoint is None:
            raise ImportError(
                "The 'comet' package is required for quality filtering. "
                "Please install it with 'pip install unbabel-comet>=2.0.0'."
            )

        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Model will be loaded on first use
        self._model = None

    def _load_model(self):
        """Load the CometKiwi model if not already loaded."""
        if self._model is None:
            logger.info(
                f"Loading CometKiwi model '{self.model_name}' on {self.device}..."
            )

            # Download the model checkpoint
            model_path = download_model(self.model_name)

            # Load the model
            self._model = load_from_checkpoint(model_path)
            self._model.to(self.device)
            self._model.eval()

            logger.info("CometKiwi model loaded successfully.")

    def score_pairs(
        self,
        sources: List[str],
        translations: List[str],
        source_lang: str = "en",
        target_lang: str = "xx",
    ) -> List[float]:
        """Score translation pairs using the CometKiwi model.

        Args:
            sources: List of source texts
            translations: List of translation texts
            source_lang: Source language code
            target_lang: Target language code ('xx' for auto-detection)

        Returns:
            List of quality scores (0-1, higher = better quality)
        """
        # Ensure model is loaded
        self._load_model()

        # Prepare data in the format expected by CometKiwi
        model_input = [
            {
                "src": src,
                "mt": tgt,
                "src_lang": source_lang,
                "tgt_lang": target_lang,
            }
            for src, tgt in zip(sources, translations)
        ]

        # Score all pairs at once
        logger.info(f"Scoring {len(model_input)} translation pairs...")
        with torch.no_grad():
            scores = self._model.predict(model_input)

        logger.info(f"Raw scores type: {type(scores)}")
        if isinstance(scores, dict):
            logger.info(f"Score keys: {scores.keys()}")

        # Extract and convert scores to floats
        # Different CometKiwi models might have different output formats
        if isinstance(scores, dict):
            if "scores" in scores:  # Try 'scores' first
                scores = scores["scores"]
            elif "score" in scores:  # Then try 'score'
                scores = scores["score"]
            else:
                logger.error(f"Unexpected score format. Keys: {scores.keys()}")
                raise ValueError("Could not find scores in model output")

        # Ensure we have a list
        if torch.is_tensor(scores):
            scores = scores.cpu().numpy().tolist()
        elif isinstance(scores, np.ndarray):
            scores = scores.tolist()

        # Convert all scores to float
        try:
            scores = [float(s) for s in scores]
        except (TypeError, ValueError) as e:
            logger.error(
                f"Failed to convert scores to float. Score examples: {scores[:5]}"
            )
            raise

        if len(scores) != len(sources):
            logger.error(
                f"Got {len(scores)} scores but expected {len(sources)}"
            )
            raise ValueError(
                f"Number of scores ({len(scores)}) doesn't match number of inputs ({len(sources)})"
            )

        logger.info(f"Scored {len(scores)} translation pairs.")
        return scores

    def filter_pairs(
        self,
        sources: List[str],
        translations: List[str],
        source_lang: str = "en",
        target_lang: str = "xx",
    ) -> Tuple[List[str], List[str], List[str], List[str], List[float]]:
        """Filter translation pairs based on quality scores.

        Args:
            sources: List of source texts
            translations: List of translation texts
            source_lang: Source language code
            target_lang: Target language code ('xx' for auto-detection)

        Returns:
            Tuple of (cleaned sources, cleaned translations,
                     filtered sources, filtered translations, all scores)
        """
        # Score all pairs
        scores = self.score_pairs(
            sources, translations, source_lang, target_lang
        )

        # Filter based on threshold
        cleaned_sources = []
        cleaned_translations = []
        filtered_sources = []
        filtered_translations = []

        for src, tgt, score in zip(sources, translations, scores):
            if score >= self.threshold:
                cleaned_sources.append(src)
                cleaned_translations.append(tgt)
            else:
                filtered_sources.append(src)
                filtered_translations.append(tgt)

        # Log results
        logger.info(
            f"Quality filtering: kept {len(cleaned_sources)}/{len(sources)} "
            f"({len(cleaned_sources)/len(sources)*100:.1f}%) pairs. "
            f"Filtered {len(filtered_sources)} pairs."
        )

        return (
            cleaned_sources,
            cleaned_translations,
            filtered_sources,
            filtered_translations,
            scores,
        )

    def get_stats(self, scores: List[float]) -> Dict:
        """Calculate statistics for quality scores.

        Args:
            scores: List of quality scores

        Returns:
            Dictionary with score statistics
        """
        if not scores:
            return {
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std": 0.0,
                "percentiles": {
                    "25": 0.0,
                    "75": 0.0,
                },
                "below_threshold": 0,
                "above_threshold": 0,
            }

        # Calculate statistics
        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        min_score = min(scores)
        max_score = max(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0

        # Calculate percentiles
        scores_np = np.array(scores)
        p25 = np.percentile(scores_np, 25)
        p75 = np.percentile(scores_np, 75)

        # Count items below/above threshold
        below = sum(1 for s in scores if s < self.threshold)
        above = len(scores) - below

        return {
            "mean": mean_score,
            "median": median_score,
            "min": min_score,
            "max": max_score,
            "std": std_score,
            "percentiles": {
                "25": float(p25),
                "75": float(p75),
            },
            "below_threshold": below,
            "above_threshold": above,
        }
