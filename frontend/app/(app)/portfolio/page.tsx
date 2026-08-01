"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Loader2, Edit2, X } from "lucide-react";
import Modal from "@/components/ui/Modal";
import { formatCurrency, formatDate } from "@/utils/format";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface BackendPortfolio {
  id: number;
  name: string;
  holdings: BackendHolding[];
}

interface BackendHolding {
  id: number;
  company_id: number;
  company_name: string;
  ticker: string;
  quantity: number;
  average_buy_price: number;
  purchase_date: string;
}

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<BackendPortfolio[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
  const [newPortfolioName, setNewPortfolioName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchPortfolios = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/portfolios`, {
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch portfolios");
      }

      const data: BackendPortfolio[] = await response.json();
      setPortfolios(data);
    } catch (err) {
      setError("Failed to load portfolios");
      console.error("Error fetching portfolios:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreatePortfolio = async () => {
    if (!newPortfolioName.trim()) return;

    setIsCreating(true);
    setError(null);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/portfolios`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ name: newPortfolioName }),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to create portfolio");
      }

      await fetchPortfolios();
      setNewPortfolioName("");
      setShowCreateModal(false);
    } catch (err) {
      setError("Failed to create portfolio");
      console.error("Error creating portfolio:", err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleRenamePortfolio = async () => {
    if (!newPortfolioName.trim() || !selectedPortfolioId) return;

    setIsRenaming(true);
    setError(null);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/portfolios/${selectedPortfolioId}`, {
        method: "PATCH",
        headers: getAuthHeaders(),
        body: JSON.stringify({ name: newPortfolioName }),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to rename portfolio");
      }

      await fetchPortfolios();
      setNewPortfolioName("");
      setShowRenameModal(false);
      setSelectedPortfolioId(null);
    } catch (err) {
      setError("Failed to rename portfolio");
      console.error("Error renaming portfolio:", err);
    } finally {
      setIsRenaming(false);
    }
  };

  const handleDeletePortfolio = async (id: number) => {
    if (!confirm("Are you sure you want to delete this portfolio?")) return;

    try {
      setError(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/portfolios/${id}`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to delete portfolio");
      }

      await fetchPortfolios();
    } catch (err) {
      setError("Failed to delete portfolio");
      console.error("Error deleting portfolio:", err);
    }
  };

  const openRenameModal = (portfolio: BackendPortfolio) => {
    setSelectedPortfolioId(portfolio.id);
    setNewPortfolioName(portfolio.name);
    setShowRenameModal(true);
  };

  useEffect(() => {
    fetchPortfolios();
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Portfolios
          </h1>
          <p className="text-text-tertiary">
            Track and manage your investment portfolios
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Portfolio
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
      ) : portfolios.length === 0 ? (
        /* Empty State */
        <div className="text-center py-12">
          <div className="text-6xl mb-4">💼</div>
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No portfolios yet
          </h3>
          <p className="text-text-tertiary mb-6">
            Create your first portfolio to start tracking investments
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create Portfolio
          </button>
        </div>
      ) : (
        /* Portfolios Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {portfolios.map((portfolio) => (
            <Link key={portfolio.id} href={`/portfolio/${portfolio.id}`} className="card-base group hover:border-primary/30 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-text-primary">
                    {portfolio.name}
                  </h3>
                  <p className="text-sm text-text-tertiary mt-1">
                    {portfolio.holdings.length} {portfolio.holdings.length === 1 ? 'holding' : 'holdings'}
                  </p>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      openRenameModal(portfolio);
                    }}
                    className="p-2 text-text-tertiary hover:text-primary transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      handleDeletePortfolio(portfolio.id);
                    }}
                    className="p-2 text-text-tertiary hover:text-danger transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-2 max-h-48 overflow-y-auto">
                {portfolio.holdings.length > 0 ? (
                  portfolio.holdings.slice(0, 5).map((holding) => (
                    <div
                      key={holding.id}
                      className="flex items-center justify-between text-sm p-2 rounded-lg bg-background"
                    >
                      <div>
                        <div className="font-medium text-text-primary">
                          {holding.ticker}
                        </div>
                        <div className="text-xs text-text-tertiary">
                          {holding.quantity} shares
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-text-primary">
                          {formatCurrency(holding.average_buy_price)}
                        </div>
                        <div className="text-xs text-text-tertiary">
                          {formatDate(holding.purchase_date)}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-text-tertiary py-2">
                    No holdings added yet
                  </p>
                )}
              </div>

              {portfolio.holdings.length > 5 && (
                <p className="text-xs text-text-tertiary mt-2">
                  +{portfolio.holdings.length - 5} more holdings
                </p>
              )}
            </Link>
          ))}
        </div>
      )}

      {/* Create Portfolio Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setNewPortfolioName("");
        }}
        title="Create New Portfolio"
        actions={
          <>
            <button
              onClick={() => {
                setShowCreateModal(false);
                setNewPortfolioName("");
              }}
              className="px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleCreatePortfolio}
              disabled={!newPortfolioName.trim() || isCreating}
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
          placeholder="e.g., Long Term, Retirement"
          value={newPortfolioName}
          onChange={(e) => setNewPortfolioName(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleCreatePortfolio()}
          className="input-base"
          autoFocus
        />
      </Modal>

      {/* Rename Portfolio Modal */}
      <Modal
        isOpen={showRenameModal}
        onClose={() => {
          setShowRenameModal(false);
          setNewPortfolioName("");
          setSelectedPortfolioId(null);
        }}
        title="Rename Portfolio"
        actions={
          <>
            <button
              onClick={() => {
                setShowRenameModal(false);
                setNewPortfolioName("");
                setSelectedPortfolioId(null);
              }}
              className="px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleRenamePortfolio}
              disabled={!newPortfolioName.trim() || isRenaming}
              className="btn-primary flex items-center gap-2"
            >
              {isRenaming ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Renaming...
                </>
              ) : (
                "Rename"
              )}
            </button>
          </>
        }
      >
        <input
          type="text"
          placeholder="Portfolio name"
          value={newPortfolioName}
          onChange={(e) => setNewPortfolioName(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleRenamePortfolio()}
          className="input-base"
          autoFocus
        />
      </Modal>
    </div>
  );
}
