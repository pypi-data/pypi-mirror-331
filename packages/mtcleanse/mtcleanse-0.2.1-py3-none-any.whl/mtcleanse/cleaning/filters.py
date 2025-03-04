"""Filter implementations for parallel text cleaning.

This module provides base classes and implementations for various filtering strategies
that can be applied to parallel text datasets.
"""

import logging
import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest

from mtcleanse.cleaning.config import CleaningConfig
from mtcleanse.cleaning.stats import CleaningStats

# Configure logging
logger = logging.getLogger("mtcleanse")


class Filter(ABC):
    """Base abstract class for all filters.

    All filters must implement the filter_pairs method which applies
    the filtering logic and returns the filtered texts.
    """

    def __init__(self, config: CleaningConfig, stats: CleaningStats):
        """Initialize the filter with the given configuration and stats collector.

        Args:
            config: Configuration for the filter
            stats: Statistics collector to update
        """
        self.config = config
        self.stats = stats

    @abstractmethod
    def filter_pairs(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Filter the given text pairs based on the implemented logic.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (filtered_source_texts, filtered_target_texts)
        """


class BasicCleaningFilter(Filter):
    """Filter for basic text cleaning operations like removing URLs, control chars, etc."""

    def __init__(self, config: CleaningConfig, stats: CleaningStats):
        """Initialize the filter with configuration.

        Args:
            config: Configuration for cleaning
            stats: Statistics collector
        """
        super().__init__(config, stats)
        # Compile regex patterns
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        self.email_pattern = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        self.control_char_pattern = re.compile(r"[\x00-\x1F\x7F-\x9F]")

    def _clean_single_text(self, text: str) -> Tuple[str, Dict[str, bool]]:
        """Clean a single text by applying various cleaning operations.

        Args:
            text: Text to clean

        Returns:
            Tuple of (cleaned_text, flags) where flags is a dictionary
            indicating which conditions were met
        """
        # Initialize flags
        flags = {
            "too_short": False,
            "too_long": False,
            "empty": False,
        }

        # Handle empty text
        if not text or text.isspace():
            flags["empty"] = True
            return "", flags

        # Apply regex-based cleanings first
        if self.config.remove_urls:
            text = self.url_pattern.sub(" ", text)

        if self.config.remove_emails:
            text = self.email_pattern.sub(" ", text)

        if self.config.remove_control_chars:
            text = self.control_char_pattern.sub(" ", text)

        # Apply character-level transformations
        if self.config.normalize_unicode:
            text = unicodedata.normalize("NFC", text)

        if self.config.lowercase:
            text = text.lower()

        # Handle whitespace last (after other substitutions might have added spaces)
        if self.config.remove_extra_whitespace:
            text = " ".join(text.split())

        # Check for empty text after cleaning
        if not text or text.isspace():
            flags["empty"] = True
            return "", flags

        # Check length constraints
        if len(text) < self.config.min_chars:
            flags["too_short"] = True
        elif len(text) > self.config.max_chars:
            flags["too_long"] = True

        return text, flags

    def filter_pairs(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Apply basic cleaning to text pairs.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (filtered_source_texts, filtered_target_texts)
        """
        if len(source_texts) != len(target_texts):
            raise ValueError(
                "Source and target texts must have the same length"
            )

        filtered_source = []
        filtered_target = []

        for src, tgt in zip(source_texts, target_texts):
            # Store original texts for sample logging
            orig_src, orig_tgt = src, tgt

            # Apply basic cleaning to both
            src_clean, src_flags = self._clean_single_text(src)
            tgt_clean, tgt_flags = self._clean_single_text(tgt)

            # Update statistics and store samples based on flags
            if src_flags["empty"] or tgt_flags["empty"]:
                self.stats.empty_after_cleaning += 1
                if len(self.stats.filtered_samples.empty_samples) < 5:
                    self.stats.filtered_samples.empty_samples.append(
                        (orig_src, orig_tgt)
                    )
                continue

            if src_flags["too_short"] or tgt_flags["too_short"]:
                self.stats.too_short += 1
                if len(self.stats.filtered_samples.too_short_samples) < 5:
                    self.stats.filtered_samples.too_short_samples.append(
                        (orig_src, orig_tgt)
                    )
                continue

            if src_flags["too_long"] or tgt_flags["too_long"]:
                self.stats.too_long += 1
                if len(self.stats.filtered_samples.too_long_samples) < 5:
                    self.stats.filtered_samples.too_long_samples.append(
                        (orig_src, orig_tgt)
                    )
                continue

            # Check word counts
            src_words = len(src_clean.split())
            tgt_words = len(tgt_clean.split())

            if not (
                self.config.min_words <= src_words <= self.config.max_words
                and self.config.min_words <= tgt_words <= self.config.max_words
            ):
                self.stats.word_count_filtered += 1
                if len(self.stats.filtered_samples.word_count_samples) < 5:
                    self.stats.filtered_samples.word_count_samples.append(
                        (orig_src, orig_tgt)
                    )
                continue

            filtered_source.append(src_clean)
            filtered_target.append(tgt_clean)

        return filtered_source, filtered_target


class LengthOutlierFilter(Filter):
    """Filter pairs based on statistical analysis of text lengths."""

    def filter_pairs(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Filter out length outliers using statistical methods.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (filtered_source_texts, filtered_target_texts)
        """
        if not source_texts:  # No texts to filter
            return [], []

        logger.info(
            f"Performing statistical outlier detection on {len(source_texts)} pairs..."
        )

        # Extract features (lengths of source and target texts)
        src_lengths = np.array([len(text) for text in source_texts])
        tgt_lengths = np.array([len(text) for text in target_texts])

        # Calculate and store length statistics
        self.stats.length_stats = {
            "source": {
                "mean": float(src_lengths.mean()),
                "std": float(src_lengths.std()),
                "min": int(src_lengths.min()),
                "max": int(src_lengths.max()),
                "median": float(np.median(src_lengths)),
                "percentiles": {
                    "25": float(np.percentile(src_lengths, 25)),
                    "75": float(np.percentile(src_lengths, 75)),
                },
            },
            "target": {
                "mean": float(tgt_lengths.mean()),
                "std": float(tgt_lengths.std()),
                "min": int(tgt_lengths.min()),
                "max": int(tgt_lengths.max()),
                "median": float(np.median(tgt_lengths)),
                "percentiles": {
                    "25": float(np.percentile(tgt_lengths, 25)),
                    "75": float(np.percentile(tgt_lengths, 75)),
                },
            },
        }

        # Calculate length ratio and its log (for better numerical properties)
        # Add a small constant to avoid division by zero
        length_ratio = (src_lengths + 1) / (tgt_lengths + 1)
        log_length_ratio = np.log(length_ratio)

        # Create features for outlier detection
        # Use both absolute lengths and ratio between them
        features = np.column_stack(
            [
                src_lengths,
                tgt_lengths,
                log_length_ratio,
            ]
        )

        # Initialize and fit isolation forest
        iso_forest = IsolationForest(
            contamination=self.config.contamination,
            random_state=self.config.random_state,
        )

        # Predict returns 1 for inliers and -1 for outliers
        predictions = iso_forest.fit_predict(features)

        # Store samples of length outliers
        outlier_indices = np.where(predictions == -1)[0]
        for idx in outlier_indices[:5]:  # Store up to 5 examples
            self.stats.filtered_samples.length_outliers_samples.append(
                (source_texts[idx], target_texts[idx])
            )

        # Update statistics
        self.stats.length_outliers = np.sum(predictions == -1)

        # Filter texts based on predictions
        filtered_source = []
        filtered_target = []

        for i, (src, tgt, pred) in enumerate(
            zip(source_texts, target_texts, predictions)
        ):
            if pred == 1:  # Keep inliers
                filtered_source.append(src)
                filtered_target.append(tgt)

        return filtered_source, filtered_target


class DomainOutlierFilter(Filter):
    """Filter pairs based on domain analysis using sentence embeddings."""

    def __init__(self, config: CleaningConfig, stats: CleaningStats):
        """Initialize the filter.

        Args:
            config: Configuration for domain filtering
            stats: Statistics collector
        """
        super().__init__(config, stats)
        # Initialize sentence transformer if domain filtering is enabled
        self.sentence_transformer = None
        if self.config.enable_domain_filtering:
            logger.info(
                f"Loading sentence transformer model: {self.config.embedding_model}"
            )
            self.sentence_transformer = SentenceTransformer(
                self.config.embedding_model
            )
            self.sentence_transformer.to(self.config.device)

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts using batched processing.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            Array of embeddings
        """
        if not texts:
            return np.array([])

        embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i : i + self.config.batch_size]
            with torch.no_grad():
                batch_embeddings = self.sentence_transformer.encode(
                    batch,
                    convert_to_numpy=True,
                    device=self.config.device,
                    show_progress_bar=False,
                )
            embeddings.append(batch_embeddings)
        return np.vstack(embeddings) if embeddings else np.array([])

    def filter_pairs(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Filter out domain outliers using sentence embeddings and isolation forest.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (filtered_source_texts, filtered_target_texts)
        """
        if not self.config.enable_domain_filtering or not source_texts:
            return source_texts, target_texts  # Skip filtering

        logger.info(
            f"Performing domain filtering on {len(source_texts)} pairs..."
        )

        # Generate embeddings for source and target texts
        source_embeddings = self._get_embeddings(source_texts)
        target_embeddings = self._get_embeddings(target_texts)

        if len(source_embeddings) == 0 or len(target_embeddings) == 0:
            return (
                source_texts,
                target_texts,
            )  # Skip filtering if embeddings could not be generated

        # Concatenate source and target embeddings for joint analysis
        combined_embeddings = np.concatenate(
            [source_embeddings, target_embeddings], axis=1
        )

        # Initialize and fit isolation forest
        iso_forest = IsolationForest(
            contamination=self.config.domain_contamination,
            random_state=self.config.random_state,
        )

        # Predict returns 1 for inliers and -1 for outliers
        predictions = iso_forest.fit_predict(combined_embeddings)

        # Store samples of domain outliers
        outlier_indices = np.where(predictions == -1)[0]
        for idx in outlier_indices[:5]:  # Store up to 5 examples
            self.stats.filtered_samples.domain_outliers_samples.append(
                (source_texts[idx], target_texts[idx])
            )

        # Update statistics
        self.stats.domain_outliers = np.sum(predictions == -1)

        # Filter texts based on predictions
        filtered_source = []
        filtered_target = []

        for i, (src, tgt, pred) in enumerate(
            zip(source_texts, target_texts, predictions)
        ):
            if pred == 1:  # Keep inliers
                filtered_source.append(src)
                filtered_target.append(tgt)

        return filtered_source, filtered_target


# Import after defining the classes to avoid circular imports
try:
    from mtcleanse.cleaning.kiwi_filter import KiwiQualityFilter
except ImportError:
    logger.warning(
        "CometKiwi quality filter not available. Install 'unbabel-comet' package to enable it."
    )
    KiwiQualityFilter = None


class QualityFilter(Filter):
    """Filter pairs based on translation quality estimation."""

    def __init__(self, config: CleaningConfig, stats: CleaningStats):
        """Initialize the filter.

        Args:
            config: Configuration for quality filtering
            stats: Statistics collector
        """
        super().__init__(config, stats)
        # Initialize quality filter if quality filtering is enabled
        self.quality_filter = None
        if (
            self.config.enable_quality_filtering
            and KiwiQualityFilter is not None
        ):
            logger.info(
                f"Initializing CometKiwi quality filter with model: {self.config.quality_model}"
            )
            self.quality_filter = KiwiQualityFilter(
                model_name=self.config.quality_model,
                threshold=self.config.quality_threshold,
                batch_size=self.config.quality_batch_size,
                device=self.config.device,
            )

    def filter_pairs(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Filter out low-quality translations.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (filtered_source_texts, filtered_target_texts)
        """
        if (
            not self.config.enable_quality_filtering
            or self.quality_filter is None
            or not source_texts
        ):
            return source_texts, target_texts  # Skip filtering

        logger.info(
            f"Performing quality filtering on {len(source_texts)} pairs..."
        )

        # Score and filter the pairs
        (
            cleaned_src,
            cleaned_tgt,
            filtered_src,
            filtered_tgt,
            quality_scores,
        ) = self.quality_filter.filter_pairs(
            source_texts,
            target_texts,
            source_lang=self.config.source_lang,
            target_lang=self.config.target_lang,
        )

        # Store quality filtering statistics
        if quality_scores:
            quality_stats = self.quality_filter.get_stats(quality_scores)
            self.stats.quality_stats = quality_stats

            # Store samples of filtered (low-quality) pairs
            # Store up to 5 examples of filtered pairs
            for idx in range(min(5, len(filtered_src))):
                self.stats.filtered_samples.quality_filtered_samples.append(
                    (filtered_src[idx], filtered_tgt[idx])
                )

            # Update statistics
            self.stats.quality_filtered = len(filtered_src)

        return cleaned_src, cleaned_tgt
