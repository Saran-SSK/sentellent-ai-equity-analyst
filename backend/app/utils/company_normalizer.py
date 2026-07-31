"""
Helper for converting company identifiers to canonical representation.

This module provides functions to normalize company names to their canonical
ticker symbol representation before ingestion into Qdrant.
"""

from __future__ import annotations

import re
import string
from pathlib import Path

import yaml


# Path to the company aliases configuration file
_ALIASES_FILE = Path(__file__).parent / "company_aliases.yaml"

# Cache for loaded aliases
_COMPANY_ALIAS_MAP: dict[str, str] = {}


def _load_aliases() -> dict[str, str]:
    """Load company aliases from the YAML configuration file."""
    global _COMPANY_ALIAS_MAP
    
    if _COMPANY_ALIAS_MAP:
        return _COMPANY_ALIAS_MAP
    
    if not _ALIASES_FILE.exists():
        # Return empty dict if file doesn't exist
        return {}
    
    try:
        with open(_ALIASES_FILE, "r") as f:
            aliases = yaml.safe_load(f) or {}
        
        # Normalize keys to lowercase for case-insensitive lookup
        _COMPANY_ALIAS_MAP = {
            _normalize_alias(key): str(value).upper()
            for key, value in aliases.items()
            if value and str(value).upper() != "N/A"
        }
        
        return _COMPANY_ALIAS_MAP
    except Exception as e:
        # If loading fails, return empty dict
        print(f"Warning: Failed to load company aliases: {e}")
        return {}


def _normalize_alias(alias: str) -> str:
    """
    Normalize an alias for lookup.
    
    This function:
    1. Strips leading/trailing whitespace
    2. Converts to lowercase
    3. Removes punctuation (except &)
    4. Collapses multiple spaces to single space
    
    Args:
        alias: Company alias to normalize
        
    Returns:
        Normalized alias string
    """
    if not alias:
        return ""
    
    # Strip whitespace
    normalized = alias.strip()
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Remove punctuation (keep & for common company name patterns like "Johnson & Johnson")
    # Remove: , ; : ' " ( ) [ ] { } < > / \ | @ # $ % ^ * + = ? ! ` ~ .
    punctuation_to_remove = string.punctuation.replace("&", "")
    normalized = normalized.translate(str.maketrans("", "", punctuation_to_remove))
    
    # Collapse multiple spaces to single space
    normalized = re.sub(r"\s+", " ", normalized)
    
    return normalized


def _is_valid_ticker_format(company: str) -> bool:
    """
    Check if a string looks like a valid ticker symbol.
    
    Valid ticker symbols:
    - Letters only (A-Z)
    - Length 1-6 characters
    - Uppercase
    
    Args:
        company: Company identifier to check
        
    Returns:
        True if it looks like a ticker symbol, False otherwise
    """
    if not company:
        return False
    
    # Check length (1-6 characters)
    if len(company) < 1 or len(company) > 6:
        return False
    
    # Check if all uppercase letters
    return company.isupper() and company.isalpha()


def to_canonical_company_id(company: str) -> str:
    """
    Convert a company identifier to its canonical ticker symbol representation.
    
    This function:
    1. Validates input is not empty
    2. Checks if it's already a valid ticker format (returns as-is if yes)
    3. Normalizes the alias (whitespace, punctuation, case)
    4. Looks up in alias map
    5. Returns the canonical ticker symbol if found
    6. Otherwise validates and returns uppercase if it looks like a ticker
    7. Raises ValueError for unknown company names
    
    Args:
        company: Company name or ticker symbol (e.g., "Apple", "AAPL")
        
    Returns:
        Canonical ticker symbol (e.g., "AAPL")
        
    Raises:
        ValueError: If company is empty or unknown
        
    Examples:
        >>> to_canonical_company_id("Apple")
        'AAPL'
        >>> to_canonical_company_id("apple")
        'AAPL'
        >>> to_canonical_company_id("Apple Inc.")
        'AAPL'
        >>> to_canonical_company_id("AAPL")
        'AAPL'
        >>> to_canonical_company_id("MSFT")
        'MSFT'
        >>> to_canonical_company_id("  Apple  ")
        'AAPL'
    """
    if not company or not company.strip():
        raise ValueError("Company identifier cannot be empty or None")
    
    # Strip whitespace
    company_stripped = company.strip()
    
    # Normalize the alias for lookup FIRST (before checking ticker format)
    # This allows "APPLE" to be resolved to "AAPL" even though it looks like a ticker
    normalized_alias = _normalize_alias(company_stripped)
    
    # Load aliases and look up
    aliases = _load_aliases()
    canonical = aliases.get(normalized_alias)
    
    if canonical:
        return canonical
    
    # If not in alias map, check if it's already a valid ticker format
    if _is_valid_ticker_format(company_stripped):
        return company_stripped
    
    # If not in map and not a valid ticker, check if uppercase version looks like a ticker
    company_upper = company_stripped.upper()
    
    if _is_valid_ticker_format(company_upper):
        return company_upper
    
    # Unknown company - raise descriptive error
    raise ValueError(
        f"Unknown company identifier: '{company}'. "
        f"Please add an alias mapping in company_aliases.yaml or provide a valid ticker symbol. "
        f"Valid ticker symbols are 1-6 uppercase letters (e.g., AAPL, MSFT, GOOGL)."
    )


def add_company_alias(alias: str, canonical_ticker: str) -> None:
    """
    Add a new company alias mapping to the in-memory cache.
    
    Note: This only adds to the runtime cache. To persist, edit company_aliases.yaml.
    
    Args:
        alias: Company name alias (e.g., "Apple Inc")
        canonical_ticker: Canonical ticker symbol (e.g., "AAPL")
        
    Raises:
        ValueError: If alias or canonical_ticker is empty
    """
    if not alias or not alias.strip():
        raise ValueError("Alias cannot be empty")
    
    if not canonical_ticker or not canonical_ticker.strip():
        raise ValueError("Canonical ticker cannot be empty")
    
    if not _is_valid_ticker_format(canonical_ticker.strip().upper()):
        raise ValueError(
            f"Invalid ticker format: '{canonical_ticker}'. "
            f"Ticker symbols must be 1-6 uppercase letters."
        )
    
    # Load aliases first
    _load_aliases()
    
    # Add to cache
    normalized_alias = _normalize_alias(alias)
    _COMPANY_ALIAS_MAP[normalized_alias] = canonical_ticker.strip().upper()


def reload_aliases() -> None:
    """
    Reload company aliases from the configuration file.
    
    This is useful if the YAML file has been modified at runtime.
    """
    global _COMPANY_ALIAS_MAP
    _COMPANY_ALIAS_MAP = {}
    _load_aliases()


def get_all_aliases() -> dict[str, str]:
    """
    Get all currently loaded company aliases.
    
    Returns:
        Dictionary mapping normalized aliases to canonical tickers
    """
    return _load_aliases().copy()
