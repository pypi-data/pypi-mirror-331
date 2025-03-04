"""
Vocabulary management for Julius Tokenizer.

This module provides a Vocabulary class for managing the mapping between
tokens and their IDs, including special token handling. The Vocabulary class
is a core component of the tokenizer, responsible for maintaining the
dictionary of tokens and their corresponding IDs.

Key features:
- Bidirectional mapping between tokens and IDs
- Special token handling
- Loading and saving vocabulary to files
- Integration with HuggingFace tokenizers
"""

from typing import Dict, List, Optional, Set, Union, Any
import json
import os
from pathlib import Path


class Vocabulary:
    """
    Manages the vocabulary for the tokenizer.
    
    This class handles the mapping between tokens and their IDs,
    including special tokens and out-of-vocabulary handling.
    
    Attributes:
        size (int): Size of the vocabulary.
        token_to_id_map (Dict[str, int]): Mapping from tokens to their IDs.
        id_to_token_map (Dict[int, str]): Mapping from IDs to their tokens.
        special_tokens (Dict[str, int]): Mapping of special token strings to their IDs.
    """
    
    def __init__(
        self,
        size: int = 50000,
        special_tokens: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize a new Vocabulary.
        
        Args:
            size: Maximum size of the vocabulary.
            special_tokens: Dictionary mapping special token strings to their IDs.
                If None, default special tokens will be used.
        """
        self.size = size
        
        # Initialize with default special tokens if none provided
        # Special tokens are essential for the tokenizer to handle
        # padding, beginning/end of sequence, unknown tokens, and masking
        if special_tokens is None:
            self.special_tokens = {
                "<pad>": 0,  # Padding token
                "<s>": 1,    # Start of sequence token
                "</s>": 2,   # End of sequence token
                "<unk>": 3,  # Unknown token for OOV words
                "<mask>": 4, # Mask token for masked language modeling
            }
        else:
            self.special_tokens = special_tokens
        
        # Initialize token-to-id and id-to-token mappings
        # These bidirectional mappings allow for efficient conversion
        # between tokens and their IDs in both directions
        self.token_to_id_map: Dict[str, int] = {}
        self.id_to_token_map: Dict[int, str] = {}
        
        # Add special tokens to the mappings
        # Special tokens are always added first to ensure they have
        # consistent IDs across different vocabulary instances
        for token, token_id in self.special_tokens.items():
            self.token_to_id_map[token] = token_id
            self.id_to_token_map[token_id] = token
    
    @classmethod
    def from_tokenizer(cls, tokenizer: Any) -> "Vocabulary":
        """
        Create a Vocabulary from a HuggingFace tokenizer.
        
        This factory method allows for easy conversion from a HuggingFace
        tokenizer's vocabulary to a Julius Vocabulary instance, facilitating
        interoperability with the HuggingFace ecosystem.
        
        Args:
            tokenizer: A HuggingFace tokenizer instance.
            
        Returns:
            A Vocabulary instance initialized with the tokenizer's vocabulary.
        """
        # Get the vocabulary from the tokenizer
        # HuggingFace tokenizers provide a get_vocab method that returns
        # a dictionary mapping tokens to their IDs
        hf_vocab = tokenizer.get_vocab()
        
        # Create a new Vocabulary instance
        vocab = cls(size=len(hf_vocab))
        
        # Update the mappings with the HuggingFace tokenizer's vocabulary
        # This replaces the default mappings with those from the tokenizer
        vocab.token_to_id_map = hf_vocab
        vocab.id_to_token_map = {v: k for k, v in hf_vocab.items()}
        
        # Update special tokens from the HuggingFace tokenizer
        # This ensures that special tokens have consistent IDs
        for token in ["<pad>", "<s>", "</s>", "<unk>", "<mask>"]:
            if token in hf_vocab:
                vocab.special_tokens[token] = hf_vocab[token]
        
        # Update size to match the actual vocabulary size
        vocab.size = len(vocab.token_to_id_map)
        
        return vocab
    
    @classmethod
    def from_file(cls, vocab_file: str) -> "Vocabulary":
        """
        Load a vocabulary from a file.
        
        This factory method allows for loading a previously saved vocabulary
        from a JSON file, enabling persistence and sharing of vocabularies.
        
        Args:
            vocab_file: Path to the vocabulary file (JSON format).
            
        Returns:
            A Vocabulary instance initialized with the contents of the file.
        """
        # Load the vocabulary data from the JSON file
        with open(vocab_file, "r", encoding="utf-8") as f:
            vocab_data = json.load(f)
        
        # Create a new Vocabulary instance with the loaded parameters
        vocab = cls(
            size=vocab_data.get("size", 50000),
            special_tokens=vocab_data.get("special_tokens"),
        )
        
        # Update the mappings with the loaded data
        # Convert string keys to integers for id_to_token_map
        vocab.token_to_id_map = {k: int(v) for k, v in vocab_data.get("token_to_id", {}).items()}
        vocab.id_to_token_map = {int(k): v for k, v in vocab_data.get("id_to_token", {}).items()}
        
        return vocab
    
    def save(self, vocab_file: str):
        """
        Save the vocabulary to a file.
        
        This method serializes the vocabulary to a JSON file, allowing it
        to be persisted and later loaded using the from_file method.
        
        Args:
            vocab_file: Path to save the vocabulary to (JSON format).
        """
        # Prepare the vocabulary data for serialization
        vocab_data = {
            "size": self.size,
            "special_tokens": self.special_tokens,
            "token_to_id": self.token_to_id_map,
            "id_to_token": self.id_to_token_map,
        }
        
        # Write the data to a JSON file
        with open(vocab_file, "w", encoding="utf-8") as f:
            json.dump(vocab_data, f, indent=2)
    
    def add_tokens(self, tokens: List[str]) -> int:
        """
        Add tokens to the vocabulary.
        
        This method adds new tokens to the vocabulary, assigning them
        sequential IDs. It respects the maximum vocabulary size and
        avoids adding duplicate tokens.
        
        Args:
            tokens: List of tokens to add to the vocabulary.
            
        Returns:
            Number of tokens successfully added to the vocabulary.
        """
        added = 0
        
        for token in tokens:
            # Only add tokens that aren't already in the vocabulary
            if token not in self.token_to_id_map:
                # Only add if we haven't reached the maximum size
                if len(self.token_to_id_map) < self.size:
                    # Assign the next available ID to the token
                    token_id = len(self.token_to_id_map)
                    self.token_to_id_map[token] = token_id
                    self.id_to_token_map[token_id] = token
                    added += 1
        
        return added
    
    def token_to_id(self, token: str) -> int:
        """
        Convert a token to its ID.
        
        This method looks up the ID for a given token. If the token is not
        in the vocabulary, it returns the ID for the unknown token.
        
        Args:
            token: The token to convert to an ID.
            
        Returns:
            The ID of the token, or the unknown token ID if not found.
        """
        # Return the ID for the token, or the unknown token ID if not found
        # The default unknown token ID is 3 if not specified in special_tokens
        return self.token_to_id_map.get(token, self.special_tokens.get("<unk>", 3))
    
    def id_to_token(self, token_id: int) -> str:
        """
        Convert a token ID to its string representation.
        
        This method looks up the token for a given ID. If the ID is not
        in the vocabulary, it returns the unknown token.
        
        Args:
            token_id: The token ID to convert to a token.
            
        Returns:
            The string representation of the token, or the unknown token if not found.
        """
        # Return the token for the ID, or the unknown token if not found
        return self.id_to_token_map.get(token_id, "<unk>")
    
    def __len__(self) -> int:
        """
        Get the size of the vocabulary.
        
        This method returns the current size of the vocabulary, which may be
        less than the maximum size if the vocabulary is not full.
        
        Returns:
            The current size of the vocabulary (number of tokens).
        """
        return len(self.token_to_id_map)
    
    def __contains__(self, token: str) -> bool:
        """
        Check if a token is in the vocabulary.
        
        This method allows for using the 'in' operator to check if a token
        is present in the vocabulary.
        
        Args:
            token: The token to check for.
            
        Returns:
            True if the token is in the vocabulary, False otherwise.
        """
        return token in self.token_to_id_map 