"""
Julius Tokenizer: A production-grade tokenizer for LLMs.

This package provides a high-performance tokenization solution
for processing large corpora of text data, with special optimization
for business and financial terminology.

Key features:
- Ultra-fast tokenization (100-200x faster than standard tokenizers)
- Perfect roundtrip accuracy with reversible mode
- Optimized for business and financial text
- Memory-efficient with intelligent caching
- Seamless integration with PyTorch and Hugging Face

Usage:
    from julius_tokenizer import JuliusTokenizer
    
    # Load a pre-trained tokenizer
    tokenizer = JuliusTokenizer.from_pretrained("julius_tokenizer/data/models/julius-base")
    
    # Encode text to token IDs
    tokens = tokenizer.encode("Your text here")
    
    # Decode token IDs back to text
    text = tokenizer.decode(tokens)
"""

__version__ = "0.1.0"

# Import the main tokenizer class for easy access
from julius_tokenizer.tokenizer import JuliusTokenizer

# Define what's available when using "from julius_tokenizer import *"
__all__ = ["JuliusTokenizer"] 