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
  User,
  ChevronDown,
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(true);

  const menuItems = [
    { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { href: "/chat", icon: MessageSquare, label: "AI Chat" },
    { href: "/watchlists", icon: Bookmark, label: "Watchlists" },
    { href: "/portfolio", icon: Briefcase, label: "Portfolio" },
    { href: "/companies", icon: Building2, label: "Companies" },
    { href: "/settings", icon: User, label: "Investor Profile" },
  ];

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <div
      className={`${
        expanded ? "w-[260px]" : "w-20"
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
