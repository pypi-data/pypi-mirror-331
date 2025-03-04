#!/usr/bin/env python3
"""Example of creating and using a custom filter with the modular filter system."""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List, Tuple

from mtcleanse.cleaning import CleaningConfig, Filter, ParallelTextCleaner, TextCleaner
from mtcleanse.cleaning.stats import CleaningStats
from mtcleanse.utils import configure_logging, get_console

# Configure logging
logger = configure_logging(level="INFO")
console = get_console()


class ProfanityFilter(Filter):
    """Custom filter that removes text pairs containing profanity."""

    def __init__(self, config: CleaningConfig, stats: CleaningStats):
        """Initialize the filter.

        Args:
            config: Cleaning configuration
            stats: Statistics collector
        """
        super().__init__(config, stats)

        # Add custom attributes to store statistics
        self.stats.profanity_filtered = 0
        self.stats.filtered_samples.profanity_samples = []

        # Define a simple list of profanity words to filter
        # In a real application, you would use a more comprehensive list
        self.profanity_words = [
            "damn",
            "hell",
            "crap",
            "ass",
            "shit",
            "fuck",
            "bitch",
            # Add other words as needed
        ]

        # Compile a regex pattern for efficient matching
        pattern = r"\b(" + "|".join(self.profanity_words) + r")\b"
        self.profanity_pattern = re.compile(pattern, re.IGNORECASE)

    def filter_pairs(
        self, source_texts: List[str], target_texts: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Filter out text pairs containing profanity.

        Args:
            source_texts: List of source language texts
            target_texts: List of target language texts

        Returns:
            Tuple of (filtered_source_texts, filtered_target_texts)
        """
        if not source_texts:  # No texts to filter
            return [], []

        logger.info(f"Applying profanity filter on {len(source_texts)} pairs...")

        filtered_source = []
        filtered_target = []
        filtered_count = 0

        for src, tgt in zip(source_texts, target_texts):
            # Check if either source or target contains profanity
            if self.profanity_pattern.search(src) or self.profanity_pattern.search(tgt):
                # Store sample for analysis
                if len(self.stats.filtered_samples.profanity_samples) < 5:
                    self.stats.filtered_samples.profanity_samples.append((src, tgt))
                filtered_count += 1
                continue

            # If no profanity is found, keep the pair
            filtered_source.append(src)
            filtered_target.append(tgt)

        # Update statistics
        self.stats.profanity_filtered = filtered_count

        logger.info(f"Filtered {filtered_count} pairs containing profanity")
        return filtered_source, filtered_target


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Example of using a custom profanity filter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--source", "-s", required=True, help="Path to source language file"
    )
    parser.add_argument(
        "--target", "-t", required=True, help="Path to target language file"
    )
    parser.add_argument(
        "--output-dir", "-o", default="cleaned", help="Directory to save cleaned files"
    )

    return parser.parse_args()


def main():
    """Run the example."""
    args = parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get base filenames
    source_path = Path(args.source)
    target_path = Path(args.target)

    # Create output paths
    output_source = output_dir / f"profanity_clean_{source_path.name}"
    output_target = output_dir / f"profanity_clean_{target_path.name}"
    stats_output = output_dir / "profanity_stats.json"
    filtered_source = output_dir / f"profanity_filtered_{source_path.name}"
    filtered_target = output_dir / f"profanity_filtered_{target_path.name}"

    # Create configuration
    config = CleaningConfig(
        min_chars=3,  # Minimal cleaning settings
        max_chars=1000,
        min_words=1,
        max_words=100,
    )

    # Create a cleaner with default filters
    cleaner = TextCleaner(config)

    # Add our custom profanity filter to the chain
    profanity_filter = ProfanityFilter(config, cleaner.stats)
    cleaner.filters.append(profanity_filter)

    console.print("[bold]Reading input files[/]")

    # Clean the files
    original_count, cleaned_count = cleaner.clean_file(
        source_file=args.source,
        target_file=args.target,
        output_source=output_source,
        output_target=output_target,
        stats_output=stats_output,
        filtered_source=filtered_source,
        filtered_target=filtered_target,
    )

    # Print summary
    console.print("\n[bold green]Cleaning completed successfully![/]")
    console.print(f"Original pairs: {original_count}")
    console.print(f"Cleaned pairs: {cleaned_count}")
    console.print(f"Filtered pairs: {original_count - cleaned_count}")
    console.print(f"Profanity filtered: {cleaner.stats.profanity_filtered}")

    if original_count > 0:
        reduction = (original_count - cleaned_count) / original_count * 100
        console.print(f"Reduction: {reduction:.2f}%")

    console.print("\n[bold]Output files:[/]")
    console.print(f"Cleaned source: {output_source}")
    console.print(f"Cleaned target: {output_target}")
    console.print(f"Statistics: {stats_output}")
    console.print(f"Filtered source: {filtered_source}")
    console.print(f"Filtered target: {filtered_target}")

    # Show samples of profanity-filtered pairs
    if (
        hasattr(cleaner.stats.filtered_samples, "profanity_samples")
        and cleaner.stats.filtered_samples.profanity_samples
    ):
        console.print("\n[bold red]Examples of profanity-filtered pairs:[/]")
        for i, (src, tgt) in enumerate(
            cleaner.stats.filtered_samples.profanity_samples, 1
        ):
            console.print(f"Example {i}:")
            console.print(f"  Source: {src}")
            console.print(f"  Target: {tgt}")
            console.print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
