const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api";

export async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Handle unauthorized - redirect to login
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export async function getWatchlists() {
  return apiCall("/v1/watchlists", { method: "GET" });
}

export async function createWatchlist(name: string) {
  return apiCall("/v1/watchlists", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function deleteWatchlist(watchlistId: string) {
  return apiCall(`/v1/watchlists/${watchlistId}`, { method: "DELETE" });
}

export async function addCompanyToWatchlist(
  watchlistId: string,
  companyId: number
) {
  return apiCall(`/v1/watchlists/${watchlistId}/companies`, {
    method: "POST",
    body: JSON.stringify({ company_id: companyId }),
  });
}

export async function removeCompanyFromWatchlist(
  watchlistId: string,
  companyId: number
) {
  return apiCall(`/v1/watchlists/${watchlistId}/companies/${companyId}`, {
    method: "DELETE",
  });
}

export async function searchCompanies(query: string) {
  return apiCall(`/v1/companies/search?q=${encodeURIComponent(query)}`, {
    method: "GET",
  });
}
