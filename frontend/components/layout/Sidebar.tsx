"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  Bookmark,
  Briefcase,
  Building2,
  Newspaper,
  BookOpen,
  Settings,
  LogOut,
  User,
  ChevronDown,
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(true);

  const menuItems = [
    { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/ai", icon: MessageSquare, label: "AI Assistant" },
    { href: "/watchlists", icon: Bookmark, label: "Watchlists" },
    { href: "/portfolio", icon: Briefcase, label: "Portfolio" },
    { href: "/companies", icon: Building2, label: "Companies" },
    { href: "/market-news", icon: Newspaper, label: "Market News" },
    { href: "/research", icon: BookOpen, label: "Research" },
  ];

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <div
      className={`${
        expanded ? "w-sidebar" : "w-20"
      } bg-sidebar border-r border-border h-screen flex flex-col transition-all duration-300 overflow-hidden`}
    >
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold">S</span>
          </div>
          {expanded && (
            <div>
              <div className="text-sm font-bold text-text-primary">Sentellent</div>
              <div className="text-xs text-text-tertiary">AI Equity</div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-6 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                active
                  ? "bg-primary/20 text-primary border border-primary/30"
                  : "text-text-secondary hover:bg-sidebar border border-transparent hover:text-text-primary"
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {expanded && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Settings & User */}
      <div className="p-3 border-t border-border space-y-2">
        <Link
          href="/settings"
          className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
            isActive("/settings")
              ? "bg-primary/20 text-primary border border-primary/30"
              : "text-text-secondary hover:bg-sidebar border border-transparent hover:text-text-primary"
          }`}
        >
          <Settings className="w-5 h-5 flex-shrink-0" />
          {expanded && <span className="text-sm font-medium">Settings</span>}
        </Link>

        <div className="relative group">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-card border border-border text-text-primary hover:border-primary/30 transition-all duration-200">
            <User className="w-5 h-5 flex-shrink-0" />
            {expanded && (
              <>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium">John Investor</div>
                  <div className="text-xs text-text-tertiary">john@email.com</div>
                </div>
                <ChevronDown className="w-4 h-4" />
              </>
            )}
          </button>

          {expanded && (
            <div className="absolute bottom-full left-0 right-0 mb-2 bg-card border border-border rounded-xl shadow-lg hidden group-hover:block z-50">
              <button className="w-full flex items-center gap-3 px-4 py-3 text-danger hover:bg-danger/10 rounded-xl transition-colors">
                <LogOut className="w-4 h-4" />
                <span className="text-sm">Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Collapse Button */}
      <div className="p-3 border-t border-border">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center py-2 text-text-tertiary hover:text-text-primary transition-colors"
        >
          <ChevronDown
            className={`w-5 h-5 transition-transform ${
              expanded ? "rotate-90" : "-rotate-90"
            }`}
          />
        </button>
      </div>
    </div>
  );
}
