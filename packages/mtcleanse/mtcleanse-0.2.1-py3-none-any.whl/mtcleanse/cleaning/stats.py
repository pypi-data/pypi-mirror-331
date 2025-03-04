"""Module for tracking and reporting text cleaning statistics."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import numpy as np

from mtcleanse.cleaning.report import generate_html_report

# Configure logging
logger = logging.getLogger("mtcleanse")


def convert_to_serializable(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization.

    Args:
        obj: Object to convert

    Returns:
        Serializable version of the object
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {
            key: convert_to_serializable(value) for key, value in obj.items()
        }
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    return round(obj, 2) if isinstance(obj, float) else obj


@dataclass
class FilteredSamples:
    """Container for sample text pairs that were filtered out.

    This class stores examples of text pairs that were filtered out
    for various reasons, which can be useful for analysis.

    Attributes:
        empty_samples: Pairs that were empty after cleaning
        too_short_samples: Pairs that were too short
        too_long_samples: Pairs that were too long
        word_count_samples: Pairs filtered by word count
        length_outliers_samples: Pairs identified as length outliers
        domain_outliers_samples: Pairs identified as domain outliers
        quality_filtered_samples: Pairs filtered by quality estimation
    """

    empty_samples: List[Tuple[str, str]] = field(default_factory=list)
    too_short_samples: List[Tuple[str, str]] = field(default_factory=list)
    too_long_samples: List[Tuple[str, str]] = field(default_factory=list)
    word_count_samples: List[Tuple[str, str]] = field(default_factory=list)
    length_outliers_samples: List[Tuple[str, str]] = field(default_factory=list)
    domain_outliers_samples: List[Tuple[str, str]] = field(default_factory=list)
    quality_filtered_samples: List[Tuple[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert samples to dictionary format.

        Returns:
            Dictionary of filtered samples
        """
        return {
            "empty_samples": self.empty_samples,
            "too_short_samples": self.too_short_samples,
            "too_long_samples": self.too_long_samples,
            "word_count_samples": self.word_count_samples,
            "length_outliers_samples": self.length_outliers_samples,
            "domain_outliers_samples": self.domain_outliers_samples,
            "quality_filtered_samples": self.quality_filtered_samples,
        }


@dataclass
class CleaningStats:
    """Statistics for each cleaning step.

    This class tracks statistics about the cleaning process, including
    counts of filtered texts and reasons for filtering.

    Attributes:
        total_pairs: Total number of text pairs processed
        empty_after_cleaning: Number of pairs that were empty after cleaning
        too_short: Number of pairs that were too short
        too_long: Number of pairs that were too long
        word_count_filtered: Number of pairs filtered by word count
        length_outliers: Number of pairs identified as length outliers
        domain_outliers: Number of pairs identified as domain outliers
        quality_filtered: Number of pairs filtered by quality estimation
        final_pairs: Number of pairs remaining after cleaning
        min_chars: Minimum character count used for filtering
        max_chars: Maximum character count used for filtering
        length_stats: Statistics about text lengths
        quality_stats: Statistics about quality scores
        filtered_samples: Examples of filtered text pairs
    """

    total_pairs: int = 0
    empty_after_cleaning: int = 0
    too_short: int = 0
    too_long: int = 0
    word_count_filtered: int = 0
    length_outliers: int = 0
    domain_outliers: int = 0
    quality_filtered: int = 0
    final_pairs: int = 0
    min_chars: int = 0
    max_chars: int = 0
    length_stats: Dict = field(default_factory=dict)
    quality_stats: Dict = field(default_factory=dict)
    filtered_samples: FilteredSamples = field(default_factory=FilteredSamples)

    def to_dict(self) -> Dict:
        """Convert stats to dictionary format for JSON export.

        Returns:
            Dictionary of cleaning statistics
        """
        stats_dict = {
            "total_pairs": int(self.total_pairs),
            "empty_after_cleaning": int(self.empty_after_cleaning),
            "too_short": int(self.too_short),
            "too_long": int(self.too_long),
            "word_count_filtered": int(self.word_count_filtered),
            "length_outliers": int(self.length_outliers),
            "domain_outliers": int(self.domain_outliers),
            "quality_filtered": int(self.quality_filtered),
            "final_pairs": int(self.final_pairs),
            "min_chars": int(self.min_chars),
            "max_chars": int(self.max_chars),
            "length_stats": self.length_stats,
            "quality_stats": self.quality_stats,
            "filtered_samples": self.filtered_samples.to_dict(),
        }

        # Calculate reduction percentage if there were any pairs
        if self.total_pairs > 0:
            stats_dict["reduction_percentage"] = float(
                (self.total_pairs - self.final_pairs) / self.total_pairs * 100
            )
        else:
            stats_dict["reduction_percentage"] = 0.0

        return stats_dict

    def save_to_json(self, output_path: str) -> None:
        """Save statistics to a JSON file.

        Args:
            output_path: Path to save the statistics to
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Cleaning statistics saved to: {output_path}")

    def save_to_html(self, output_path: str) -> None:
        """Save statistics to an HTML report.

        Args:
            output_path: Path to save the HTML report to
        """
        generate_html_report(self.to_dict(), output_path)
        logger.info(f"HTML report saved to: {output_path}")

    def log_stats(self) -> None:
        """Log the cleaning statistics."""
        logger.info("Cleaning Statistics:")
        logger.info(f"Total pairs processed: {self.total_pairs}")
        logger.info(
            f"Pairs empty after basic cleaning: {self.empty_after_cleaning}"
        )
        logger.info(
            f"Pairs too short (<{self.min_chars} chars): {self.too_short}"
        )
        logger.info(
            f"Pairs too long (>{self.max_chars} chars): {self.too_long}"
        )
        logger.info(
            f"Pairs filtered by word count: {self.word_count_filtered}"
        )
        logger.info(
            f"Pairs identified as length outliers: {self.length_outliers}"
        )
        logger.info(
            f"Pairs identified as domain outliers: {self.domain_outliers}"
        )
        logger.info(
            f"Pairs filtered by quality estimation: {self.quality_filtered}"
        )
        logger.info(f"Final pairs remaining: {self.final_pairs}")

        if self.total_pairs > 0:
            reduction = (
                (self.total_pairs - self.final_pairs) / self.total_pairs * 100
            )
            logger.info(f"Total reduction: {reduction:.2f}%")
        else:
            logger.info("Total reduction: 0.00%")
