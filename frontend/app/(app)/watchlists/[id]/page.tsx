"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Plus, X, Loader2 } from "lucide-react";
import Link from "next/link";
import Modal from "@/components/ui/Modal";
import DataTable, { Column } from "@/components/tables/DataTable";

interface Company {
  id: number;
  symbol: string;
  name: string;
  exchange: string | null;
  sector: string | null;
  industry: string | null;
  country: string | null;
  currency: string | null;
}

interface WatchlistCompany {
  id: number;
  watchlist_id: number;
  company_id: number;
  created_at: string;
  company: Company;
}

interface Watchlist {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  companies: WatchlistCompany[];
}

interface SearchResult {
  symbol: string;
  name: string;
}

export default function WatchlistDetailPage() {
  const router = useRouter();
  const params = useParams();
  const watchlistId = params.id as string;
  const [watchlist, setWatchlist] = useState<Watchlist | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [isRemoving, setIsRemoving] = useState<number | null>(null);
  const [addError, setAddError] = useState<string | null>(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchWatchlist = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/watchlists/${watchlistId}`, {
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (response.status === 404) {
        setError("Watchlist not found");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch watchlist");
      }

      const data: Watchlist = await response.json();
      setWatchlist(data);
      setError(null);
    } catch (err) {
      setError("Failed to load watchlist");
      console.error("Error fetching watchlist:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const searchCompanies = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    setAddError(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/api/v1/companies/search?q=${encodeURIComponent(query)}`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to search companies");
      }

      const data: SearchResult[] = await response.json();
      setSearchResults(data);
    } catch (err) {
      setAddError("Failed to search companies");
      console.error("Error searching companies:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const addCompany = async (symbol: string) => {
    if (!watchlist) return;

    setIsAdding(true);
    setAddError(null);

    try {
      // First get the company id from symbol
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      // Fetch company profile to get the database id
      const profileResponse = await fetch(
        `${backendUrl}/api/v1/companies/${symbol}/profile`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (profileResponse.status === 401) {
        router.push("/signin");
        return;
      }

      if (!profileResponse.ok) {
        throw new Error("Failed to fetch company profile");
      }

      const profile = await profileResponse.json();
      
      // Add company to watchlist
      const addResponse = await fetch(
        `${backendUrl}/api/v1/watchlists/${watchlist.id}/companies`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({ company_id: profile.id }),
        }
      );

      if (addResponse.status === 401) {
        router.push("/signin");
        return;
      }

      if (addResponse.status === 409) {
        setAddError("This company is already in the watchlist");
        setIsAdding(false);
        return;
      }

      if (!addResponse.ok) {
        throw new Error("Failed to add company to watchlist");
      }

      // Success - refresh watchlist
      await fetchWatchlist();
      setShowAddModal(false);
      setSearchQuery("");
      setSearchResults([]);
    } catch (err) {
      setAddError("Failed to add company to watchlist");
      console.error("Error adding company:", err);
    } finally {
      setIsAdding(false);
    }
  };

  const removeCompany = async (company_id: number) => {
    if (!watchlist) return;

    setIsRemoving(company_id);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/api/v1/watchlists/${watchlist.id}/companies/${company_id}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to remove company from watchlist");
      }

      // Success - refresh watchlist
      await fetchWatchlist();
    } catch (err) {
      console.error("Error removing company:", err);
    } finally {
      setIsRemoving(null);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, [watchlistId]);

  if (isLoading) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      </div>
    );
  }

  if (error || !watchlist) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="mb-6">
          <Link href="/watchlists">
            <button className="p-2 hover:bg-card rounded-lg transition-colors">
              <ArrowLeft className="w-5 h-5 text-text-secondary" />
            </button>
          </Link>
        </div>
        <div className="p-8 rounded-lg bg-danger/10 border border-danger/30 text-danger text-center">
          {error || "Watchlist not found"}
        </div>
      </div>
    );
  }

  const columns: Column<WatchlistCompany>[] = [
    {
      key: "symbol" as any,
      label: "Ticker",
      render: (value, row) => (
        <span className="font-semibold text-text-primary">{row.company.symbol}</span>
      ),
      width: "100px",
    },
    {
      key: "name" as any,
      label: "Company",
      render: (value, row) => row.company.name,
      width: "200px",
    },
    {
      key: "sector" as any,
      label: "Sector",
      render: (value, row) => row.company.sector || "N/A",
      width: "120px",
    },
    {
      key: "exchange" as any,
      label: "Exchange",
      render: (value, row) => row.company.exchange || "N/A",
      width: "100px",
    },
    {
      key: "industry" as any,
      label: "Industry",
      render: (value, row) => row.company.industry || "N/A",
      width: "150px",
    },
    {
      key: "actions" as any,
      label: "Actions",
      render: (value, row) => (
        <button
          onClick={() => removeCompany(row.company_id)}
          disabled={isRemoving === row.company_id}
          className="text-danger hover:opacity-70 transition-opacity disabled:opacity-50"
        >
          {isRemoving === row.company_id ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <X className="w-4 h-4" />
          )}
        </button>
      ),
      width: "80px",
    },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/watchlists">
          <button className="p-2 hover:bg-card rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5 text-text-secondary" />
          </button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            {watchlist.name}
          </h1>
          <p className="text-text-tertiary">
            {watchlist.companies.length} {watchlist.companies.length === 1 ? 'company' : 'companies'} in this watchlist
          </p>
        </div>
        <button
          onClick={() => {
            setShowAddModal(true);
            setSearchQuery("");
            setSearchResults([]);
            setAddError(null);
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Company
        </button>
      </div>

      {/* Table */}
      {watchlist.companies.length === 0 ? (
        <div className="card-base text-center py-12">
          <div className="text-4xl mb-2">📋</div>
          <p className="text-text-tertiary">No companies in this watchlist</p>
          <p className="text-sm text-text-tertiary mt-1">
            Click "Add Company" to get started
          </p>
        </div>
      ) : (
        <div className="card-base mb-8">
          <DataTable columns={columns} data={watchlist.companies} />
        </div>
      )}

      {/* Add Company Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          setSearchQuery("");
          setSearchResults([]);
          setAddError(null);
        }}
        title="Add Company to Watchlist"
      >
        <div className="space-y-4">
          {addError && (
            <div className="p-3 rounded-lg bg-danger/10 border border-danger/30 text-danger text-sm">
              {addError}
            </div>
          )}
          
          <input
            type="text"
            placeholder="Search company or ticker..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              searchCompanies(e.target.value);
            }}
            className="input-base"
            autoFocus
            disabled={isAdding}
          />

          {/* Search Results */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {isSearching ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              </div>
            ) : searchResults.length > 0 ? (
              searchResults.map((result) => (
                <button
                  key={result.symbol}
                  onClick={() => addCompany(result.symbol)}
                  disabled={isAdding}
                  className="w-full p-3 rounded-lg bg-card hover:bg-sidebar border border-border transition-colors text-left disabled:opacity-50"
                >
                  <div className="font-semibold text-text-primary">
                    {result.symbol}
                  </div>
                  <div className="text-sm text-text-tertiary">
                    {result.name}
                  </div>
                </button>
              ))
            ) : searchQuery ? (
              <p className="text-text-tertiary text-sm text-center py-4">
                No results found
              </p>
            ) : (
              <p className="text-text-tertiary text-sm text-center py-4">
                Search for a company to add
              </p>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
