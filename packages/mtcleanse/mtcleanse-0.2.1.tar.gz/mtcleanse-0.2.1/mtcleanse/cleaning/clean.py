"""Core module for cleaning parallel text datasets."""

import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from mtcleanse.cleaning.config import CleaningConfig
from mtcleanse.cleaning.filters import (
    BasicCleaningFilter,
    DomainOutlierFilter,
    LengthOutlierFilter,
    QualityFilter,
)
from mtcleanse.cleaning.stats import CleaningStats

# Configure logging
logger = logging.getLogger("mtcleanse")


class TextCleaner:
    """Class for cleaning text data with various options.

    This class provides methods for cleaning parallel text datasets,
    including filtering by length, removing noise, and detecting outliers.
    """

    def __init__(self, config: Optional[CleaningConfig] = None):
        """Initialize the cleaner with given configuration.

        Args:
            config: Configuration for the cleaning process
        """
        self.config = config or CleaningConfig()
        self.stats = CleaningStats()

        # Initialize filters
        self._initialize_filters()

    def _initialize_filters(self):
        """Initialize the filter chain."""
        self.filters = []

        # Basic cleaning filter (always included)
        self.filters.append(BasicCleaningFilter(self.config, self.stats))

        # Length outlier filter (always included)
        self.filters.append(LengthOutlierFilter(self.config, self.stats))

        # Domain outlier filter (optional)
        if self.config.enable_domain_filtering:
            self.filters.append(DomainOutlierFilter(self.config, self.stats))

        # Quality filter (optional)
        if self.config.enable_quality_filtering:
            self.filters.append(QualityFilter(self.config, self.stats))

    def clean_parallel_texts(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Clean parallel texts and return filtered versions.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (cleaned source texts, cleaned target texts)
        """
        if len(source_texts) != len(target_texts):
            raise ValueError(
                "Source and target texts must have the same length"
            )

        # Reset statistics
        self.stats = CleaningStats()
        self.stats.total_pairs = len(source_texts)
        self.stats.min_chars = self.config.min_chars
        self.stats.max_chars = self.config.max_chars

        # Re-initialize filters with new stats object
        self._initialize_filters()

        logger.info(
            f"Starting cleaning process for {len(source_texts)} text pairs..."
        )

        # Apply each filter in sequence
        filtered_source, filtered_target = source_texts, target_texts

        for filter_obj in self.filters:
            # Check if we have any texts left to filter
            if not filtered_source:
                logger.warning(
                    f"All texts were filtered out before applying {filter_obj.__class__.__name__}"
                )
                break

            logger.info(f"Applying filter: {filter_obj.__class__.__name__}")
            filtered_source, filtered_target = filter_obj.filter_pairs(
                filtered_source, filtered_target
            )

        # Update final count
        self.stats.final_pairs = len(filtered_source)

        # Log statistics
        self.stats.log_stats()

        return filtered_source, filtered_target

    def clean_file(
        self,
        source_file: str,
        target_file: str,
        output_source: str,
        output_target: str,
        stats_output: Optional[str] = None,
        filtered_source: Optional[str] = None,
        filtered_target: Optional[str] = None,
        json_output: Optional[str] = None,
        instruction: Optional[str] = None,
    ) -> Tuple[int, int]:
        """Clean parallel text files and save results.

        Args:
            source_file: Path to source language file
            target_file: Path to target language file
            output_source: Path to save cleaned source texts
            output_target: Path to save cleaned target texts
            stats_output: Path to save cleaning statistics
            filtered_source: Path to save filtered source texts
            filtered_target: Path to save filtered target texts
            json_output: Path to save data in JSON format
            instruction: Instruction to include in JSON output

        Returns:
            Tuple of (original count, cleaned count)
        """
        logger.info(f"Loading source text from: {source_file}")
        with open(source_file, "r", encoding="utf-8") as f:
            source_texts = [line.strip() for line in f]

        logger.info(f"Loading target text from: {target_file}")
        with open(target_file, "r", encoding="utf-8") as f:
            target_texts = [line.strip() for line in f]

        if len(source_texts) != len(target_texts):
            raise ValueError(
                f"Source and target files have different line counts: "
                f"{len(source_texts)} vs {len(target_texts)}"
            )

        original_count = len(source_texts)
        logger.info(f"Loaded {original_count} text pairs")

        # Clean the texts
        cleaned_source, cleaned_target = self.clean_parallel_texts(
            source_texts, target_texts
        )

        cleaned_count = len(cleaned_source)
        logger.info(f"Cleaned texts: {cleaned_count} pairs remaining")

        # Save cleaned texts
        logger.info(f"Saving cleaned source texts to: {output_source}")
        Path(output_source).parent.mkdir(parents=True, exist_ok=True)
        with open(output_source, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_source))

        logger.info(f"Saving cleaned target texts to: {output_target}")
        Path(output_target).parent.mkdir(parents=True, exist_ok=True)
        with open(output_target, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_target))

        # Save statistics if requested
        if stats_output:
            self.stats.save_to_json(stats_output)

        # Save filtered texts if requested
        if filtered_source and filtered_target:
            # Create a set of indices that were kept
            original_indices = set(range(original_count))
            kept_indices = set()

            # Create a mapping from cleaned texts back to original indices
            for i, (src, tgt) in enumerate(zip(source_texts, target_texts)):
                for j, (clean_src, clean_tgt) in enumerate(
                    zip(cleaned_source, cleaned_target)
                ):
                    if clean_src == src and clean_tgt == tgt:
                        kept_indices.add(i)
                        break

            # Get indices that were filtered out
            filtered_indices = original_indices - kept_indices

            # Get the filtered texts
            filtered_src_texts = [source_texts[i] for i in filtered_indices]
            filtered_tgt_texts = [target_texts[i] for i in filtered_indices]

            # Save filtered texts
            logger.info(f"Saving filtered source texts to: {filtered_source}")
            Path(filtered_source).parent.mkdir(parents=True, exist_ok=True)
            with open(filtered_source, "w", encoding="utf-8") as f:
                f.write("\n".join(filtered_src_texts))

            logger.info(f"Saving filtered target texts to: {filtered_target}")
            Path(filtered_target).parent.mkdir(parents=True, exist_ok=True)
            with open(filtered_target, "w", encoding="utf-8") as f:
                f.write("\n".join(filtered_tgt_texts))

        # Export data to JSON if requested
        if json_output:
            logger.info(f"Saving JSON output to: {json_output}")
            Path(json_output).parent.mkdir(parents=True, exist_ok=True)

            json_data = []
            for src, tgt in zip(cleaned_source, cleaned_target):
                item = {"source": src, "target": tgt}
                if instruction:
                    item["instruction"] = instruction
                json_data.append(item)

            with open(json_output, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

        return original_count, cleaned_count
