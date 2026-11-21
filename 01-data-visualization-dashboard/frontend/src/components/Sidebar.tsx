"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  SlidersHorizontal,
  BarChart3,
  Terminal,
  BrainCircuit,
  Settings,
  Sparkles
} from "lucide-react";

const navigationItems = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Dataset Explorer", href: "/datasets", icon: Database },
  { name: "Transformations", href: "/transform", icon: SlidersHorizontal },
  { name: "Chart Builder", href: "/charts", icon: BarChart3 },
  { name: "Dashboards", href: "/dashboards", icon: LayoutDashboard },
  { name: "SQL Studio", href: "/sql", icon: Terminal },
  { name: "ML Analytics", href: "/ml-analytics", icon: BrainCircuit },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-surface border-r border-surfaceBorder flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand */}
        <div className="h-16 flex items-center px-6 border-b border-surfaceBorder gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center text-primary border border-primary/30">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <div>
            <span className="font-bold text-lg text-white tracking-tight">Cognix</span>
            <span className="block text-[10px] text-gray-400 uppercase tracking-widest font-mono">Data Visualizer</span>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="p-4 space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary text-white shadow-sm shadow-primary/20"
                    : "text-gray-400 hover:text-white hover:bg-surfaceBorder/40"
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-surfaceBorder">
        <div className="bg-surfaceBorder/30 rounded-lg p-3 text-xs text-gray-400">
          <span className="block font-semibold text-gray-300">Phase 1: Active</span>
          <span className="block text-[11px] text-gray-500 mt-0.5">Standalone DuckDB Columnar Engine</span>
        </div>
      </div>
    </aside>
  );
}
