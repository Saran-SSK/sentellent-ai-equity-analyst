"use client";

import { useState } from "react";
import { ArrowLeft, Plus, X } from "lucide-react";
import Link from "next/link";
import Modal from "@/components/ui/Modal";
import DataTable, { Column } from "@/components/tables/DataTable";
import { Stock } from "@/types";
import { formatCurrency, formatPercent, getChangeColor } from "@/utils/format";
import { MOCK_WATCHLISTS, SEARCH_RESULTS } from "@/utils/mockData";

export default function WatchlistDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const watchlist = MOCK_WATCHLISTS.find((w) => w.id === params.id);
  const [stocks, setStocks] = useState<Stock[]>(watchlist?.stocks || []);
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [suggestions, setSuggestions] = useState(SEARCH_RESULTS);

  if (!watchlist) {
    return (
      <div className="p-8 text-center">
        <p className="text-text-tertiary">Watchlist not found</p>
      </div>
    );
  }

  const handleAddStock = (stock: any) => {
    const mockStock: Stock = {
      id: stock.id,
      ticker: stock.ticker,
      company: stock.company,
      sector: "Tech",
      exchange: "NSE",
      currentPrice: Math.random() * 5000,
      change: Math.random() * 100 - 50,
      changePercent: Math.random() * 10 - 5,
      volume: Math.random() * 5000000,
      marketCap: Math.random() * 1000000000000,
    };

    if (!stocks.find((s) => s.id === mockStock.id)) {
      setStocks([...stocks, mockStock]);
    }
    setShowAddModal(false);
    setSearchQuery("");
  };

  const handleRemoveStock = (id: number) => {
    setStocks(stocks.filter((s) => s.id !== id));
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      setSuggestions(
        SEARCH_RESULTS.filter(
          (s) =>
            s.ticker.toLowerCase().includes(query.toLowerCase()) ||
            s.company.toLowerCase().includes(query.toLowerCase())
        )
      );
    } else {
      setSuggestions(SEARCH_RESULTS);
    }
  };

  const columns: Column<Stock>[] = [
    {
      key: "ticker",
      label: "Ticker",
      render: (value) => (
        <span className="font-semibold text-text-primary">{value}</span>
      ),
      width: "100px",
    },
    {
      key: "company",
      label: "Company",
      width: "200px",
    },
    {
      key: "sector",
      label: "Sector",
      width: "120px",
    },
    {
      key: "exchange",
      label: "Exchange",
      width: "100px",
    },
    {
      key: "currentPrice",
      label: "Price",
      render: (value) => formatCurrency(value as number),
    },
    {
      key: "changePercent",
      label: "Change",
      render: (value, row) => (
        <span className={getChangeColor((row as Stock).change)}>
          {formatPercent((value as number))}
        </span>
      ),
    },
    {
      key: "id",
      label: "Actions",
      render: (value) => (
        <button
          onClick={() => handleRemoveStock(value as number)}
          className="text-danger hover:opacity-70 transition-opacity"
        >
          <X className="w-4 h-4" />
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
            {stocks.length} stocks in this watchlist
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Add Stock
        </button>
      </div>

      {/* Table */}
      <div className="card-base mb-8">
        <DataTable columns={columns} data={stocks} />
      </div>

      {/* Add Stock Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          setSearchQuery("");
        }}
        title="Add Company to Watchlist"
      >
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Search company or ticker..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="input-base"
            autoFocus
          />

          {/* Search Results */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {suggestions.length > 0 ? (
              suggestions.map((stock) => (
                <button
                  key={stock.id}
                  onClick={() => handleAddStock(stock)}
                  className="w-full p-3 rounded-lg bg-card hover:bg-sidebar border border-border transition-colors text-left"
                >
                  <div className="font-semibold text-text-primary">
                    {stock.ticker}
                  </div>
                  <div className="text-sm text-text-tertiary">
                    {stock.company}
                  </div>
                </button>
              ))
            ) : (
              <p className="text-text-tertiary text-sm text-center py-4">
                No results found
              </p>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
