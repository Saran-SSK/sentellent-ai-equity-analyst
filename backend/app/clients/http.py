from __future__ import annotations

from typing import Any

import httpx


class HttpClient:
    """Reusable HTTP client for external API integrations.

    This client provides a thin wrapper around ``httpx`` to centralize
    request handling for all external providers.
    """

    def __init__(self, timeout: float = 10.0) -> None:
        """Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds.
        """
        self._client = httpx.Client(timeout=timeout)

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Send a GET request and return the parsed JSON response.

        Args:
            url: Target URL.
            params: Optional query parameters.
            headers: Optional request headers.

        Returns:
            Parsed JSON response.

        Raises:
            httpx.HTTPStatusError:
                If the server returns a non-success status code.

            httpx.RequestError:
                If the request fails due to a network issue.
        """
        response = self._client.get(
            url=url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()

        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()