# MTCleanse: Machine Translation Corpus Cleaning

[![PyPI version](https://badge.fury.io/py/mtcleanse.svg)](https://badge.fury.io/py/mtcleanse)
[![Python versions](https://img.shields.io/pypi/pyversions/mtcleanse.svg)](https://pypi.org/project/mtcleanse/)

MTCleanse is a powerful, state-of-the-art toolkit designed for cleaning and preprocessing parallel corpora to be used for neural machine translation (NMT) systems. Built for researchers, language technologists, and MT practitioners, it addresses the critical "garbage in, garbage out" problem that plagues many translation models.

By systematically removing noise, detecting misalignments, filtering problematic sentence pairs, and handling outliers, MTCleanse significantly improves the quality of training data, leading to more accurate, robust, and reliable translation models.

## Features

- Clean parallel text datasets with configurable parameters
- Remove noise such as URLs, emails, and control characters
- Filter texts based on length constraints
- Detect and remove statistical outliers
- Domain-based filtering using sentence embeddings
- Export cleaned data in various formats (text files, JSON)
- Comprehensive statistics on the cleaning process

## Installation

```bash
pip install mtcleanse
```

Or install from source:

```bash
git clone https://github.com/yourusername/mtcleanse.git
cd mtcleanse
pip install -e .
```

## Quick Start

```python
from mtcleanse.cleaning import ParallelTextCleaner

# Initialize with default settings
cleaner = ParallelTextCleaner()

# Clean parallel text files
cleaner.clean_files(
    source_file="source.en",
    target_file="target.fr",
    output_source="clean_source.en",
    output_target="clean_target.fr"
)

# Or clean text directly
source_texts = ["Hello world", "This is a test"]
target_texts = ["Bonjour le monde", "C'est un test"]
clean_source, clean_target = cleaner.clean_texts(source_texts, target_texts)
```

## Command Line Interface

MTCleanse also provides a command-line interface:

```bash
mtcleanse-clean --source source.en --target target.fr --output-source clean_source.en --output-target clean_target.fr
```

## Configuration

You can customize the cleaning process with various parameters:

```python
cleaner = ParallelTextCleaner({
    "min_chars": 10,
    "max_chars": 500,
    "min_words": 3,
    "max_words": 50,
    "enable_domain_filtering": True,
    "domain_contamination": 0.2
})

# This method returns the cleaned data and the statistics
clean_source, clean_target, stats = cleaner.clean_texts(
    source_texts=["Hello world", "This is a test"],
    target_texts=["Bonjour le monde", "C'est un test"]
)

# This method saves the cleaned data to disk and generates an HTML report
cleaner.clean_file(
    source_file="source.en",
    target_file="target.fr",
    output_source="clean_source.en",
    output_target="clean_target.fr",
    html_report="report.html"
)
```

## Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/yourusername/mtcleanse.git
cd mtcleanse

# Install in development mode with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest tests/ --cov=mtcleanse
```

## License

[MIT](https://opensource.org/licenses/MIT)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
