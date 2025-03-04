# Julius Tokenizer

A high-performance tokenizer optimized for business and financial text processing with perfect roundtrip accuracy.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Julius Tokenizer is a state-of-the-art tokenization library designed specifically for business and financial text. It offers exceptional performance while providing perfect roundtrip accuracy through its innovative reversible mode.

### Key Features

- **Perfect Roundtrip Accuracy**: Optional reversible mode ensures 100% exact text reconstruction
- **Business Domain Optimization**: Specially trained for financial and business terminology
- **Memory Efficient**: Intelligent caching and memory management
- **PyTorch Integration**: Seamless integration with PyTorch and Hugging Face Transformers

## Installation

```bash
# Install from PyPI
pip install julius-nlp-tokenizer

# Or install from the current directory
pip install .

# Or install from a specific path
pip install /path/to/julius_tokenizer
```

## Quick Start

```python
from julius_tokenizer import JuliusTokenizer

# Load the pretrained tokenizer
tokenizer = JuliusTokenizer.from_pretrained("julius_tokenizer/data/models/julius-base")

# Encode text to token IDs
text = "EBITDA increased by 15% in Q3 2023, exceeding our projected KPIs."
tokens = tokenizer.encode(text)
print(f"Token count: {len(tokens)}")
print(f"Tokens: {tokens[:10]}...")

# Decode token IDs back to text
decoded_text = tokenizer.decode(tokens)
print(f"Decoded text: {decoded_text}")
print(f"Perfect roundtrip: {text == decoded_text}")
```

## Example Usage

The package includes an example script that demonstrates how to use the tokenizer:

```bash
python example.py
```

## API Reference

### JuliusTokenizer

The main tokenizer class with the following methods:

#### Loading a Pretrained Tokenizer

```python
tokenizer = JuliusTokenizer.from_pretrained("julius_tokenizer/data/models/julius-base")
```

#### Encoding Text

```python
# Encode a single text
tokens = tokenizer.encode("Your text here")

# Batch encode multiple texts
batch_tokens = tokenizer.batch_encode(["Text 1", "Text 2", "Text 3"])
```

#### Decoding Tokens

```python
# Decode a single sequence of tokens
text = tokenizer.decode([1, 308, 253, 152, 3473])

# Batch decode multiple sequences
texts = tokenizer.batch_decode([[1, 308, 253], [1, 456, 789]])
```

#### Reversible Mode

```python
# Enable perfect roundtrip accuracy
tokenizer.set_reversible_mode(True)

# Disable for slightly faster processing
tokenizer.set_reversible_mode(False)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 