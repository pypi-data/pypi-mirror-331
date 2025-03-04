"""
Text processing utilities for Julius Tokenizer.

This module provides text normalization and preprocessing functionality
to ensure consistent handling of text before tokenization.
"""

import re
import unicodedata
from typing import List, Dict, Optional, Pattern, Callable, Union


class TextProcessor:
    """
    Handles text normalization and preprocessing for tokenization.
    
    This class provides methods for cleaning and normalizing text
    before tokenization, as well as post-processing after detokenization.
    
    Attributes:
        lowercase (bool): Whether to convert text to lowercase.
        strip_accents (bool): Whether to strip accents from characters.
        normalize_whitespace (bool): Whether to normalize whitespace.
        replace_digits (bool): Whether to replace digits with a special token.
        custom_replacements (Dict[str, str]): Custom text replacements to apply.
    """
    
    def __init__(
        self,
        lowercase: bool = True,
        strip_accents: bool = True,
        normalize_whitespace: bool = True,
        replace_digits: bool = False,
        custom_replacements: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a new TextProcessor.
        
        Args:
            lowercase: Whether to convert text to lowercase.
            strip_accents: Whether to strip accents from characters.
            normalize_whitespace: Whether to normalize whitespace.
            replace_digits: Whether to replace digits with a special token.
            custom_replacements: Custom text replacements to apply.
        """
        self.lowercase = lowercase
        self.strip_accents = strip_accents
        self.normalize_whitespace = normalize_whitespace
        self.replace_digits = replace_digits
        self.custom_replacements = custom_replacements or {}
        
        # Compile regex patterns for efficiency
        self._whitespace_pattern = re.compile(r'\s+')
        self._digit_pattern = re.compile(r'\d+')
        
        # Compile custom replacement patterns
        self._custom_patterns = {
            re.compile(pattern): replacement
            for pattern, replacement in self.custom_replacements.items()
        }
    
    def normalize(self, text: str) -> str:
        """
        Normalize text for tokenization.
        
        This method applies a series of normalization steps to the input text:
        1. Lowercase (if enabled)
        2. Unicode normalization (NFD)
        3. Accent stripping (if enabled)
        4. Whitespace normalization (if enabled)
        5. Digit replacement (if enabled)
        6. Custom replacements
        
        Args:
            text: The text to normalize.
            
        Returns:
            Normalized text.
        """
        if not text:
            return ""
        
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        # Unicode normalization
        text = unicodedata.normalize('NFD', text)
        
        # Strip accents
        if self.strip_accents:
            text = ''.join([c for c in text if not unicodedata.combining(c)])
        
        # Normalize whitespace
        if self.normalize_whitespace:
            text = self._whitespace_pattern.sub(' ', text)
            text = text.strip()
        
        # Replace digits
        if self.replace_digits:
            text = self._digit_pattern.sub('<NUM>', text)
        
        # Apply custom replacements
        for pattern, replacement in self._custom_patterns.items():
            text = pattern.sub(replacement, text)
        
        return text
    
    def denormalize(self, text: str) -> str:
        """
        Reverse normalization for detokenized text.
        
        This method applies minimal post-processing to detokenized text.
        It's designed to be lightweight since most normalization steps
        don't need to be reversed.
        
        Args:
            text: The text to denormalize.
            
        Returns:
            Denormalized text.
        """
        if not text:
            return ""
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?:;])', r'\1', text)
        
        # Fix spacing for quotes
        text = re.sub(r'\s+\'', r'\'', text)
        text = re.sub(r'\s+"', r'"', text)
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def split_text(self, text: str, max_length: int = 512) -> List[str]:
        """
        Split text into chunks of maximum length.
        
        This method splits text into chunks that don't exceed the maximum length,
        trying to split at sentence boundaries when possible.
        
        Args:
            text: The text to split.
            max_length: Maximum length of each chunk.
            
        Returns:
            List of text chunks.
        """
        if not text:
            return []
        
        # Normalize text first
        text = self.normalize(text)
        
        # If text is shorter than max_length, return it as is
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences
        sentence_endings = [m.end() for m in re.finditer(r'[.!?]\s+', text)]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the last sentence ending that fits within max_length
            end = start + max_length
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a sentence boundary
            suitable_end = None
            for sentence_end in sentence_endings:
                if start < sentence_end <= end:
                    suitable_end = sentence_end
            
            if suitable_end:
                chunks.append(text[start:suitable_end])
                start = suitable_end
            else:
                # If no sentence boundary found, split at word boundary
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    chunks.append(text[start:last_space])
                    start = last_space + 1
                else:
                    # If no word boundary found, split at max_length
                    chunks.append(text[start:end])
                    start = end
        
        return chunks
    
    def clean_corpus(self, text: str) -> str:
        """
        Clean text for corpus preparation.
        
        This method applies more aggressive cleaning for corpus preparation:
        1. Remove URLs
        2. Remove email addresses
        3. Remove excessive punctuation
        4. Fix common OCR errors
        5. Apply standard normalization
        
        Args:
            text: The text to clean.
            
        Returns:
            Cleaned text.
        """
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'([.,!?:;]){2,}', r'\1', text)
        
        # Fix common OCR errors
        ocr_fixes = {
            r'l\s*\'\s*': 'i',  # l' -> i
            r'0': 'o',          # 0 -> o
            r'1': 'l',          # 1 -> l
        }
        
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text)
        
        # Apply standard normalization
        text = self.normalize(text)
        
        return text 