"""Cleaning module for text data preprocessing.

This module provides classes and functions for cleaning and preprocessing
parallel text datasets for machine translation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from rich.logging import RichHandler

from mtcleanse.cleaning.clean import TextCleaner
from mtcleanse.cleaning.config import CleaningConfig
from mtcleanse.cleaning.filters import (
    BasicCleaningFilter,
    DomainOutlierFilter,
    Filter,
    LengthOutlierFilter,
    QualityFilter,
)
from mtcleanse.cleaning.kiwi_filter import KiwiQualityFilter
from mtcleanse.cleaning.stats import CleaningStats

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("mtcleanse")


class ParallelTextCleaner(TextCleaner):
    """Main user-facing class for cleaning parallel text datasets.

    This class provides a high-level interface for cleaning parallel text datasets,
    with support for reading from and writing to files.

    Example:
        >>> cleaner = ParallelTextCleaner()
        >>> cleaner.clean_file(
        ...     source_file="source.txt",
        ...     target_file="target.txt",
        ...     output_source="clean_source.txt",
        ...     output_target="clean_target.txt",
        ...     stats_output="stats.json"
        ... )
    """

    def clean_file(
        self,
        source_file: Union[str, Path],
        target_file: Union[str, Path],
        output_source: Union[str, Path],
        output_target: Union[str, Path],
        stats_output: Optional[Union[str, Path]] = None,
        filtered_source: Optional[Union[str, Path]] = None,
        filtered_target: Optional[Union[str, Path]] = None,
        html_report: Optional[Union[str, Path]] = None,
    ) -> Tuple[int, int]:
        """Clean parallel text files and save results.

        Args:
            source_file: Path to source language file
            target_file: Path to target language file
            output_source: Path to save cleaned source texts
            output_target: Path to save cleaned target texts
            stats_output: Optional path to save cleaning statistics as JSON
            filtered_source: Optional path to save filtered source texts
            filtered_target: Optional path to save filtered target texts
            html_report: Optional path to save HTML report

        Returns:
            Tuple of (original_count, cleaned_count)
        """
        # Read input files
        logger.info(f"Reading source texts from: {source_file}")
        with open(source_file, "r", encoding="utf-8") as f:
            source_texts = [line.strip() for line in f]

        logger.info(f"Reading target texts from: {target_file}")
        with open(target_file, "r", encoding="utf-8") as f:
            target_texts = [line.strip() for line in f]

        # Clean the texts
        cleaned_source, cleaned_target = self.clean_texts(
            source_texts, target_texts
        )

        # Save cleaned texts
        logger.info(f"Saving cleaned source texts to: {output_source}")
        Path(output_source).parent.mkdir(parents=True, exist_ok=True)
        with open(output_source, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_source))

        logger.info(f"Saving cleaned target texts to: {output_target}")
        Path(output_target).parent.mkdir(parents=True, exist_ok=True)
        with open(output_target, "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_target))

        # Save filtered texts if requested
        if filtered_source and filtered_target:
            # Get filtered texts (those that were removed)
            filtered_src = [
                text
                for text in source_texts
                if text not in set(cleaned_source)
            ]
            filtered_tgt = [
                text
                for text in target_texts
                if text not in set(cleaned_target)
            ]

            logger.info(f"Saving filtered source texts to: {filtered_source}")
            Path(filtered_source).parent.mkdir(parents=True, exist_ok=True)
            with open(filtered_source, "w", encoding="utf-8") as f:
                f.write("\n".join(filtered_src))

            logger.info(f"Saving filtered target texts to: {filtered_target}")
            Path(filtered_target).parent.mkdir(parents=True, exist_ok=True)
            with open(filtered_target, "w", encoding="utf-8") as f:
                f.write("\n".join(filtered_tgt))

        # Save statistics if requested
        if stats_output:
            self.stats.save_to_json(stats_output)

        # Generate HTML report if requested
        if html_report:
            self.stats.save_to_html(html_report)

        return len(source_texts), len(cleaned_source)

    def clean_texts(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Clean parallel texts.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (cleaned_source_texts, cleaned_target_texts)
        """
        return super().clean_parallel_texts(source_texts, target_texts)

    def get_stats(self) -> Dict:
        """Get statistics from the latest cleaning operation."""
        return self.stats.to_dict()


# Export public classes and functions
__all__ = [
    "TextCleaner",
    "ParallelTextCleaner",
    "CleaningConfig",
    "CleaningStats",
    "KiwiQualityFilter",
    "Filter",
    "BasicCleaningFilter",
    "LengthOutlierFilter",
    "DomainOutlierFilter",
    "QualityFilter",
]
