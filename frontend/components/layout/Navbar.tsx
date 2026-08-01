"use client";

import { Search, Bell, Settings } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="h-16 bg-card border-b border-border flex items-center justify-between px-8">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search stocks, news..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-base pl-10 w-full"
          />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4 ml-8">
        <button className="relative p-2 text-text-secondary hover:text-text-primary transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full" />
        </button>

        <button className="p-2 text-text-secondary hover:text-text-primary transition-colors">
          <Settings className="w-5 h-5" />
        </button>

        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-bold text-sm cursor-pointer hover:opacity-90 transition-opacity">
          JI
        </div>
      </div>
    </div>
  );
}
