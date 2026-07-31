"""
Unit tests for company_normalizer module.
"""

import pytest

from app.utils.company_normalizer import (
    _is_valid_ticker_format,
    _normalize_alias,
    add_company_alias,
    get_all_aliases,
    reload_aliases,
    to_canonical_company_id,
)


class TestNormalizeAlias:
    """Test alias normalization function."""

    def test_basic_normalization(self):
        """Test basic whitespace and case normalization."""
        assert _normalize_alias("Apple") == "apple"
        assert _normalize_alias("APPLE") == "apple"
        assert _normalize_alias("apple") == "apple"

    def test_whitespace_normalization(self):
        """Test whitespace stripping and collapsing."""
        assert _normalize_alias("  Apple  ") == "apple"
        assert _normalize_alias("Apple Inc") == "apple inc"
        assert _normalize_alias("Apple  Inc") == "apple inc"
        assert _normalize_alias("Apple   Inc.") == "apple inc"

    def test_punctuation_removal(self):
        """Test punctuation removal (keeps & only)."""
        assert _normalize_alias("Apple, Inc.") == "apple inc"
        assert _normalize_alias("Apple; Inc") == "apple inc"
        assert _normalize_alias("Apple: Inc") == "apple inc"
        assert _normalize_alias("Apple Inc.") == "apple inc"
        assert _normalize_alias("Johnson & Johnson") == "johnson & johnson"
        assert _normalize_alias("JPMorgan Chase & Co") == "jpmorgan chase & co"

    def test_empty_string(self):
        """Test empty string handling."""
        assert _normalize_alias("") == ""
        assert _normalize_alias("   ") == ""

    def test_complex_normalization(self):
        """Test complex company names."""
        assert _normalize_alias("Apple Inc.") == "apple inc"
        assert _normalize_alias("APPLE INC") == "apple inc"
        assert _normalize_alias("  APPLE  INC.  ") == "apple inc"


class TestIsValidTickerFormat:
    """Test ticker format validation."""

    def test_valid_tickers(self):
        """Test valid ticker symbols."""
        assert _is_valid_ticker_format("AAPL") is True
        assert _is_valid_ticker_format("MSFT") is True
        assert _is_valid_ticker_format("NVDA") is True
        assert _is_valid_ticker_format("GOOGL") is True
        assert _is_valid_ticker_format("TSLA") is True
        assert _is_valid_ticker_format("A") is True
        assert _is_valid_ticker_format("BRK.B") is False  # Contains dot

    def test_invalid_tickers(self):
        """Test invalid ticker symbols."""
        assert _is_valid_ticker_format("AAPL1") is False  # Contains number
        assert _is_valid_ticker_format("AAPL-") is False  # Contains hyphen
        assert _is_valid_ticker_format("AAPL_") is False  # Contains underscore
        assert _is_valid_ticker_format("AAPL ") is False  # Contains space
        assert _is_valid_ticker_format(" aapl") is False  # Contains space
        assert _is_valid_ticker_format("aapl") is False  # Lowercase
        assert _is_valid_ticker_format("") is False  # Empty
        assert _is_valid_ticker_format("ABCDEFG") is False  # Too long (7 chars)
        assert _is_valid_ticker_format("12345") is False  # Numbers only

    def test_edge_cases(self):
        """Test edge cases."""
        assert _is_valid_ticker_format(None) is False
        assert _is_valid_ticker_format("A") is True  # Single character
        assert _is_valid_ticker_format("AAAAAA") is True  # Max length (6 chars)
        assert _is_valid_ticker_format("AAAAAAA") is False  # Too long (7 chars)


class TestToCanonicalCompanyId:
    """Test main conversion function."""

    def test_apple_variants(self):
        """Test various Apple company name variants."""
        assert to_canonical_company_id("Apple") == "AAPL"
        assert to_canonical_company_id("apple") == "AAPL"
        assert to_canonical_company_id("APPLE") == "AAPL"
        assert to_canonical_company_id("Apple Inc") == "AAPL"
        assert to_canonical_company_id("Apple Inc.") == "AAPL"
        assert to_canonical_company_id("Apple Corporation") == "AAPL"
        assert to_canonical_company_id("  Apple  ") == "AAPL"
        assert to_canonical_company_id("  APPLE INC  ") == "AAPL"

    def test_ticker_symbols(self):
        """Test that valid ticker symbols are returned as-is."""
        assert to_canonical_company_id("AAPL") == "AAPL"
        assert to_canonical_company_id("MSFT") == "MSFT"
        assert to_canonical_company_id("NVDA") == "NVDA"
        assert to_canonical_company_id("GOOGL") == "GOOGL"
        assert to_canonical_company_id("TSLA") == "TSLA"

    def test_microsoft_variants(self):
        """Test Microsoft company name variants."""
        assert to_canonical_company_id("Microsoft") == "MSFT"
        assert to_canonical_company_id("microsoft") == "MSFT"
        assert to_canonical_company_id("Microsoft Corporation") == "MSFT"
        assert to_canonical_company_id("Microsoft Corp") == "MSFT"

    def test_google_variants(self):
        """Test Google/Alphabet company name variants."""
        assert to_canonical_company_id("Google") == "GOOGL"
        assert to_canonical_company_id("google") == "GOOGL"
        assert to_canonical_company_id("Alphabet") == "GOOGL"
        assert to_canonical_company_id("Alphabet Inc") == "GOOGL"
        assert to_canonical_company_id("Alphabet Inc.") == "GOOGL"

    def test_nvidia_variants(self):
        """Test Nvidia company name variants."""
        assert to_canonical_company_id("Nvidia") == "NVDA"
        assert to_canonical_company_id("nvidia") == "NVDA"
        assert to_canonical_company_id("NVIDIA") == "NVDA"
        assert to_canonical_company_id("Nvidia Corporation") == "NVDA"

    def test_empty_string(self):
        """Test empty string raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            to_canonical_company_id("")
        with pytest.raises(ValueError, match="cannot be empty"):
            to_canonical_company_id("   ")

    def test_none_value(self):
        """Test None raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            to_canonical_company_id(None)

    def test_unknown_company(self):
        """Test unknown company raises ValueError."""
        with pytest.raises(ValueError, match="Unknown company identifier"):
            to_canonical_company_id("UnknownCompany")
        with pytest.raises(ValueError, match="Unknown company identifier"):
            to_canonical_company_id("Some Random Company Name")

    def test_invalid_company_format(self):
        """Test company names that don't look like tickers and aren't in aliases."""
        with pytest.raises(ValueError, match="Unknown company identifier"):
            to_canonical_company_id("APPLE INCORPORATED COMPANY LIMITED")
        with pytest.raises(ValueError, match="Unknown company identifier"):
            to_canonical_company_id("Some Company With Long Name")


class TestAddCompanyAlias:
    """Test adding company aliases at runtime."""

    def test_add_alias(self):
        """Test adding a new alias."""
        # Add a new alias
        add_company_alias("Test Company", "TEST")
        
        # Verify it works
        assert to_canonical_company_id("Test Company") == "TEST"
        assert to_canonical_company_id("test company") == "TEST"
        
        # Reload to clear cache
        reload_aliases()

    def test_add_alias_validation(self):
        """Test validation when adding aliases."""
        with pytest.raises(ValueError, match="Alias cannot be empty"):
            add_company_alias("", "TEST")
        
        with pytest.raises(ValueError, match="Canonical ticker cannot be empty"):
            add_company_alias("Test Company", "")
        
        with pytest.raises(ValueError, match="Invalid ticker format"):
            add_company_alias("Test Company", "TOOLONG")

    def test_add_alias_overwrites(self):
        """Test that adding an alias overwrites existing."""
        add_company_alias("Apple", "TESTA")
        assert to_canonical_company_id("Apple") == "TESTA"
        reload_aliases()


class TestGetAllAliases:
    """Test getting all loaded aliases."""

    def test_get_aliases(self):
        """Test retrieving all aliases."""
        aliases = get_all_aliases()
        assert isinstance(aliases, dict)
        assert len(aliases) > 0  # Should have some aliases loaded
        assert "apple" in aliases
        assert aliases["apple"] == "AAPL"


class TestReloadAliases:
    """Test reloading aliases from file."""

    def test_reload_clears_cache(self):
        """Test that reload clears the cache."""
        # Add a runtime alias
        add_company_alias("TestAlias", "TEST")
        
        # Verify it works
        assert to_canonical_company_id("TestAlias") == "TEST"
        
        # Reload
        reload_aliases()
        
        # Verify it no longer works
        with pytest.raises(ValueError, match="Unknown company identifier"):
            to_canonical_company_id("TestAlias")


class TestBackwardCompatibility:
    """Test backward compatibility with existing usage."""

    def test_existing_apple_ingestion(self):
        """Test that existing Apple ingestion still works."""
        # These are the formats that might be used in existing code
        assert to_canonical_company_id("Apple") == "AAPL"
        assert to_canonical_company_id("AAPL") == "AAPL"

    def test_future_microsoft(self):
        """Test that Microsoft will work when added."""
        assert to_canonical_company_id("Microsoft") == "MSFT"
        assert to_canonical_company_id("MSFT") == "MSFT"

    def test_future_nvidia(self):
        """Test that Nvidia will work when added."""
        assert to_canonical_company_id("Nvidia") == "NVDA"
        assert to_canonical_company_id("NVDA") == "NVDA"

    def test_future_google(self):
        """Test that Google/Alphabet will work when added."""
        assert to_canonical_company_id("Google") == "GOOGL"
        assert to_canonical_company_id("GOOGL") == "GOOGL"
