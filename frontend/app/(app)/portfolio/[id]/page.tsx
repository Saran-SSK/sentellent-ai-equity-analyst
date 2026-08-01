"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Plus, Trash2, Loader2, Edit2, X } from "lucide-react";
import Link from "next/link";
import Modal from "@/components/ui/Modal";
import { formatCurrency, formatDate } from "@/utils/format";

interface Company {
  id: number;
  symbol: string; 
  name: string;
}

interface Holding {
  id: number;
  quantity: number;
  average_buy_price: number;
  purchase_date: string | null;
  company: Company;
}

interface Portfolio {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  holdings: Holding[];
}

interface SearchResult {
  symbol: string;
  name: string;
}

export default function PortfolioDetailPage() {
  const router = useRouter();
  const params = useParams();
  const portfolioId = params.id as string;
  
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Add holding modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<SearchResult | null>(null);
  const [quantity, setQuantity] = useState("");
  const [averageBuyPrice, setAverageBuyPrice] = useState("");
  const [purchaseDate, setPurchaseDate] = useState("");
  
  // Edit holding modal
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingHolding, setEditingHolding] = useState<Holding | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  
  // Delete holding
  const [isDeleting, setIsDeleting] = useState<number | null>(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchPortfolio = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/portfolios/${portfolioId}`, {
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (response.status === 404) {
        setError("Portfolio not found");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch portfolio");
      }

      const data: Portfolio = await response.json();
      setPortfolio(data);
    } catch (err) {
      setError("Failed to load portfolio");
      console.error("Error fetching portfolio:", err);
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

  const addHolding = async () => {
    if (!portfolio || !selectedCompany || !quantity || !averageBuyPrice) {
      setAddError("Please fill in all required fields");
      return;
    }

    setIsAdding(true);
    setAddError(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      // Fetch company profile to get database id
      const profileResponse = await fetch(
        `${backendUrl}/api/v1/companies/${selectedCompany.symbol}/profile`,
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
      
      // Add holding to portfolio
      const addResponse = await fetch(
        `${backendUrl}/api/v1/portfolios/${portfolio.id}/holdings`,
        {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            company_id: profile.id,
            quantity: parseInt(quantity),
            average_buy_price: parseFloat(averageBuyPrice),
            purchase_date: purchaseDate || null,
          }),
        }
      );

      if (addResponse.status === 401) {
        router.push("/signin");
        return;
      }

      if (addResponse.status === 409) {
        setAddError("This company is already in this portfolio");
        setIsAdding(false);
        return;
      }

      if (!addResponse.ok) {
        throw new Error("Failed to add holding");
      }

      // Success - refresh portfolio
      await fetchPortfolio();
      setShowAddModal(false);
      resetAddForm();
    } catch (err) {
      setAddError("Failed to add holding");
      console.error("Error adding holding:", err);
    } finally {
      setIsAdding(false);
    }
  };

  const editHolding = async () => {
    if (!editingHolding || !quantity || !averageBuyPrice) {
      setEditError("Please fill in all required fields");
      return;
    }

    setIsEditing(true);
    setEditError(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/api/v1/portfolios/holdings/${editingHolding.id}`,
        {
          method: "PATCH",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            quantity: parseInt(quantity),
            average_buy_price: parseFloat(averageBuyPrice),
            purchase_date: purchaseDate || null,
          }),
        }
      );

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to update holding");
      }

      // Success - refresh portfolio
      await fetchPortfolio();
      setShowEditModal(false);
      resetEditForm();
    } catch (err) {
      setEditError("Failed to update holding");
      console.error("Error updating holding:", err);
    } finally {
      setIsEditing(false);
    }
  };

  const deleteHolding = async (holdingId: number) => {
    if (!confirm("Are you sure you want to delete this holding?")) return;

    setIsDeleting(holdingId);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/api/v1/portfolios/holdings/${holdingId}`,
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
        throw new Error("Failed to delete holding");
      }

      // Success - refresh portfolio
      await fetchPortfolio();
    } catch (err) {
      console.error("Error deleting holding:", err);
    } finally {
      setIsDeleting(null);
    }
  };

  const resetAddForm = () => {
    setSearchQuery("");
    setSearchResults([]);
    setSelectedCompany(null);
    setQuantity("");
    setAverageBuyPrice("");
    setPurchaseDate("");
    setAddError(null);
  };

  const resetEditForm = () => {
    setEditingHolding(null);
    setQuantity("");
    setAverageBuyPrice("");
    setPurchaseDate("");
    setEditError(null);
  };

  const openEditModal = (holding: Holding) => {
    setEditingHolding(holding);
    setQuantity(holding.quantity.toString());
    setAverageBuyPrice(holding.average_buy_price.toString());
    setPurchaseDate(holding.purchase_date || "");
    setEditError(null);
    setShowEditModal(true);
  };

  useEffect(() => {
    fetchPortfolio();
  }, [portfolioId]);

  if (isLoading) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      </div>
    );
  }

  if (error || !portfolio) {
    return (
      <div className="p-8 max-w-6xl mx-auto">
        <div className="mb-6">
          <Link href="/portfolio">
            <button className="p-2 hover:bg-card rounded-lg transition-colors">
              <ArrowLeft className="w-5 h-5 text-text-secondary" />
            </button>
          </Link>
        </div>
        <div className="p-8 rounded-lg bg-danger/10 border border-danger/30 text-danger text-center">
          {error || "Portfolio not found"}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/portfolio">
          <button className="p-2 hover:bg-card rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5 text-text-secondary" />
          </button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            {portfolio.name}
          </h1>
          <p className="text-text-tertiary">
            {portfolio.holdings.length} {portfolio.holdings.length === 1 ? 'holding' : 'holdings'}
          </p>
        </div>
        <button
          onClick={() => {
            setShowAddModal(true);
            resetAddForm();
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Holding
        </button>
      </div>

      {/* Holdings Table */}
      {portfolio.holdings.length === 0 ? (
        <div className="card-base text-center py-12">
          <div className="text-4xl mb-2">💼</div>
          <p className="text-text-tertiary">No holdings in this portfolio</p>
          <p className="text-sm text-text-tertiary mt-1">
            Click "Add Holding" to get started
          </p>
        </div>
      ) : (
        <div className="card-base">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 text-sm font-semibold text-text-tertiary">Company</th>
                  <th className="text-left p-4 text-sm font-semibold text-text-tertiary">Symbol</th>
                  <th className="text-right p-4 text-sm font-semibold text-text-tertiary">Quantity</th>
                  <th className="text-right p-4 text-sm font-semibold text-text-tertiary">Avg Buy Price</th>
                  <th className="text-right p-4 text-sm font-semibold text-text-tertiary">Total Value</th>
                  <th className="text-right p-4 text-sm font-semibold text-text-tertiary">Purchase Date</th>
                  <th className="text-center p-4 text-sm font-semibold text-text-tertiary">Actions</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.holdings.map((holding) => (
                  <tr key={holding.id} className="border-b border-border last:border-0">
                    <td className="p-4">
                      <div className="font-medium text-text-primary">{holding.company.name}</div>
                    </td>
                    <td className="p-4">
                      <span className="font-semibold text-text-primary">{holding.company.symbol}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-text-primary">{holding.quantity}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-text-primary">{formatCurrency(holding.average_buy_price)}</span>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-text-primary font-medium">
                        {formatCurrency(holding.quantity * holding.average_buy_price)}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <span className="text-text-tertiary text-sm">
                        {holding.purchase_date ? formatDate(holding.purchase_date) : "N/A"}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => openEditModal(holding)}
                          className="p-2 text-text-tertiary hover:text-primary transition-colors"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deleteHolding(holding.id)}
                          disabled={isDeleting === holding.id}
                          className="p-2 text-text-tertiary hover:text-danger transition-colors disabled:opacity-50"
                        >
                          {isDeleting === holding.id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Holding Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          resetAddForm();
        }}
        title="Add Holding"
      >
        <div className="space-y-4">
          {addError && (
            <div className="p-3 rounded-lg bg-danger/10 border border-danger/30 text-danger text-sm">
              {addError}
            </div>
          )}
          
          <div>
            <label className="block text-sm text-text-secondary mb-2">Search Company</label>
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
            
            {searchResults.length > 0 && !selectedCompany && (
              <div className="mt-2 space-y-2 max-h-48 overflow-y-auto border border-border rounded-lg">
                {searchResults.map((result) => (
                  <button
                    key={result.symbol}
                    onClick={() => {
                      setSelectedCompany(result);
                      setSearchQuery(result.name);
                      setSearchResults([]);
                    }}
                    className="w-full p-3 text-left hover:bg-background transition-colors border-b border-border last:border-0"
                  >
                    <div className="font-semibold text-text-primary">{result.symbol}</div>
                    <div className="text-sm text-text-tertiary">{result.name}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {selectedCompany && (
            <div className="p-3 rounded-lg bg-background border border-border">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-text-primary">{selectedCompany.symbol}</div>
                  <div className="text-sm text-text-tertiary">{selectedCompany.name}</div>
                </div>
                <button
                  onClick={() => {
                    setSelectedCompany(null);
                    setSearchQuery("");
                  }}
                  className="text-text-tertiary hover:text-danger transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm text-text-secondary mb-2">Quantity *</label>
            <input
              type="number"
              placeholder="Number of shares"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="input-base"
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">Average Buy Price *</label>
            <input
              type="number"
              placeholder="Price per share"
              value={averageBuyPrice}
              onChange={(e) => setAverageBuyPrice(e.target.value)}
              className="input-base"
              min="0"
              step="0.01"
            />
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">Purchase Date</label>
            <input
              type="date"
              value={purchaseDate}
              onChange={(e) => setPurchaseDate(e.target.value)}
              className="input-base"
            />
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <button
            onClick={() => {
              setShowAddModal(false);
              resetAddForm();
            }}
            className="flex-1 px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
            disabled={isAdding}
          >
            Cancel
          </button>
          <button
            onClick={addHolding}
            disabled={!selectedCompany || !quantity || !averageBuyPrice || isAdding}
            className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAdding ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Adding...
              </span>
            ) : (
              "Add Holding"
            )}
          </button>
        </div>
      </Modal>

      {/* Edit Holding Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          resetEditForm();
        }}
        title="Edit Holding"
      >
        <div className="space-y-4">
          {editError && (
            <div className="p-3 rounded-lg bg-danger/10 border border-danger/30 text-danger text-sm">
              {editError}
            </div>
          )}
          
          {editingHolding && (
            <div className="p-3 rounded-lg bg-background border border-border">
              <div className="font-semibold text-text-primary">{editingHolding.company.symbol}</div>
              <div className="text-sm text-text-tertiary">{editingHolding.company.name}</div>
            </div>
          )}

          <div>
            <label className="block text-sm text-text-secondary mb-2">Quantity *</label>
            <input
              type="number"
              placeholder="Number of shares"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="input-base"
              min="1"
            />
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">Average Buy Price *</label>
            <input
              type="number"
              placeholder="Price per share"
              value={averageBuyPrice}
              onChange={(e) => setAverageBuyPrice(e.target.value)}
              className="input-base"
              min="0"
              step="0.01"
            />
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">Purchase Date</label>
            <input
              type="date"
              value={purchaseDate}
              onChange={(e) => setPurchaseDate(e.target.value)}
              className="input-base"
            />
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <button
            onClick={() => {
              setShowEditModal(false);
              resetEditForm();
            }}
            className="flex-1 px-4 py-2 rounded-lg border border-border text-text-primary hover:bg-card transition-colors"
            disabled={isEditing}
          >
            Cancel
          </button>
          <button
            onClick={editHolding}
            disabled={!quantity || !averageBuyPrice || isEditing}
            className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isEditing ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Updating...
              </span>
            ) : (
              "Update Holding"
            )}
          </button>
        </div>
      </Modal>
    </div>
  );
}
