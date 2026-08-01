"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Loader2 } from "lucide-react";
import Modal from "@/components/ui/Modal";
import { Watchlist, Stock } from "@/types";
import { formatDate } from "@/utils/format";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface BackendWatchlist {
  id: number;
  name: string;
  companies: any[];
}

export default function WatchlistsPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchWatchlists = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/watchlists`, {
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch watchlists");
      }

      const data: BackendWatchlist[] = await response.json();
      
      const mappedWatchlists: Watchlist[] = data.map((w) => ({
        id: w.id.toString(),
        name: w.name,
        createdAt: new Date().toISOString(),
        stocks: [],
        stockCount: w.companies.length,
      }));

      setWatchlists(mappedWatchlists);
    } catch (err) {
      setError("Failed to load watchlists");
      console.error("Error fetching watchlists:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateWatchlist = async () => {
    if (!newWatchlistName.trim()) return;

    setIsCreating(true);
    setError(null);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/watchlists`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ name: newWatchlistName }),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to create watchlist");
      }

      await fetchWatchlists();
      setNewWatchlistName("");
      setShowCreateModal(false);
    } catch (err) {
      setError("Failed to create watchlist");
      console.error("Error creating watchlist:", err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteWatchlist = async (id: string) => {
    if (!confirm("Are you sure you want to delete this watchlist?")) return;

    try {
      setError(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/watchlists/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to delete watchlist");
      }

      await fetchWatchlists();
    } catch (err) {
      setError("Failed to delete watchlist");
      console.error("Error deleting watchlist:", err);
    }
  };

  useEffect(() => {
    fetchWatchlists();
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Watchlists
          </h1>
          <p className="text-text-tertiary">
            Organize and track your favorite stocks
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Watchlist
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-danger/10 border border-danger/30 text-danger">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : watchlists.length === 0 ? (
        /* Empty State */
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No watchlists yet
          </h3>
          <p className="text-text-tertiary mb-6">
            Create your first watchlist to start tracking stocks
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create Watchlist
          </button>
        </div>
      ) : (
        /* Watchlists Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {watchlists.map((watchlist) => (
            <Link key={watchlist.id} href={`/watchlists/${watchlist.id}`}>
              <div className="card-base group h-full">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary group-hover:text-primary transition-colors">
                      {watchlist.name}
                    </h3>
                    <p className="text-sm text-text-tertiary mt-1">
                      {watchlist.stockCount} {watchlist.stockCount === 1 ? 'stock' : 'stocks'}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      handleDeleteWatchlist(watchlist.id);
                    }}
                    className="p-2 text-text-tertiary hover:text-danger transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-2">
                  {watchlist.stocks && watchlist.stocks.length > 0 ? (
                    watchlist.stocks.slice(0, 3).map((stock: Stock) => (
                      <div
                        key={stock.id}
                        className="flex items-center justify-between text-sm p-2 rounded-lg bg-background"
                      >
                        <span className="font-medium text-text-primary">
                          {stock.ticker}
                        </span>
                        <span
                          className={
                            stock.change >= 0
                              ? "text-success"
                              : "text-danger"
                          }
                        >
                          {stock.change >= 0 ? "+" : ""}
                          {stock.changePercent.toFixed(2)}%
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-text-tertiary py-2">
                      No stocks added yet
                    </p>
                  )}
                </div>

                <p className="text-xs text-text-tertiary mt-4 pt-4 border-t border-border">
                  Created {formatDate(watchlist.createdAt)}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Create Watchlist Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setNewWatchlistName("");
        }}
        title="Create New Watchlist"
        actions={
          <>
            <button
              onClick={() => {
                setShowCreateModal(false);
                setNewWatchlistName("");
              }}
              className="px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateWatchlist}
              disabled={!newWatchlistName.trim() || isCreating}
              className="btn-primary flex items-center gap-2"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create"
              )}
            </button>
          </>
        }
      >
        <input
          type="text"
          placeholder="e.g., Tech Stocks, Banking Sector"
          value={newWatchlistName}
          onChange={(e) => setNewWatchlistName(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleCreateWatchlist()}
          className="input-base"
          autoFocus
        />
      </Modal>
    </div>
  );
}
