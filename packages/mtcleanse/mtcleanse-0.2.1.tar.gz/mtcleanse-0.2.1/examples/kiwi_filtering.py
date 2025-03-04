#!/usr/bin/env python3
"""Minimal example demonstrating CometKiwi quality filtering for parallel corpora."""

import json
from pathlib import Path

from mtcleanse.cleaning import CleaningConfig, ParallelTextCleaner
from mtcleanse.utils import get_console

console = get_console()

# Input/output paths
input_file = "filtered_biomedical.json"
output_dir = Path("cleaned")
output_dir.mkdir(exist_ok=True)

# Load data
console.print("[bold]Loading data[/]")
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)
source_texts = [item["source"] for item in data]
target_texts = [item["target"] for item in data]
console.print(f"Loaded {len(source_texts)} translation pairs")

# Configure and run quality filtering
console.print("[bold]Running quality filtering[/]")
config = CleaningConfig(
    # Disable other filters
    min_chars=1,
    max_chars=100000,
    min_words=1,
    max_words=100000,
    enable_domain_filtering=False,
    # Enable only quality filtering
    enable_quality_filtering=True,
    quality_threshold=0.5
)

cleaner = ParallelTextCleaner(config)

# Create temporary files for input
source_input = output_dir / "temp_source.txt"
target_input = output_dir / "temp_target.txt"
source_output = output_dir / "filtered.src"
target_output = output_dir / "filtered.tgt"

# Write input texts to files
with open(source_input, "w", encoding="utf-8") as f:
    f.write("\n".join(source_texts))
with open(target_input, "w", encoding="utf-8") as f:
    f.write("\n".join(target_texts))

# Use clean_file instead, which supports HTML report generation
original_count, cleaned_count = cleaner.clean_file(
    source_file=str(source_input),
    target_file=str(target_input),
    output_source=str(source_output),
    output_target=str(target_output),
    html_report=str(output_dir / "report.html")  # Add HTML report here
)

# Clean up temporary files
source_input.unlink()
target_input.unlink()

# Print summary
console.print("\n[bold green]Filtering completed![/]")
console.print(f"Original pairs: {original_count}")
console.print(f"Filtered pairs: {cleaned_count}")
console.print(f"Reduction: {(1 - cleaned_count/original_count)*100:.1f}%")
console.print(f"\nOutput files saved to:\n{source_output}\n{target_output}")
console.print(f"HTML report saved to: {output_dir / 'report.html'}")
