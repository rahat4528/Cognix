"use client";

import { useState, useEffect } from "react";
import { User, Bell, ChevronDown } from "lucide-react";
import { api } from "@/lib/api";

export default function Header() {
  const [userEmail, setUserEmail] = useState<string>("admin@cognix.local");
  const [workspaceName, setWorkspaceName] = useState<string>("Enterprise Analytics & ML");

  useEffect(() => {
    // Attempt to load workspace from local storage or profile
    const storedWs = typeof window !== "undefined" ? localStorage.getItem("cognix_ws_name") : null;
    if (storedWs) setWorkspaceName(storedWs);
  }, []);

  return (
    <header className="h-16 border-b border-surfaceBorder bg-surface/50 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-40">
      {/* Workspace Indicator */}
      <div className="flex items-center gap-3">
        <span className="text-xs uppercase tracking-wider text-gray-400 font-medium">Workspace:</span>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-surfaceBorder/40 rounded-lg border border-surfaceBorder text-sm text-gray-200">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-medium">{workspaceName}</span>
          <ChevronDown className="w-3.5 h-3.5 text-gray-400 ml-1" />
        </div>
      </div>

      {/* User Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5 px-3 py-1.5 bg-surfaceBorder/30 rounded-full border border-surfaceBorder">
          <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-primary text-xs font-semibold">
            A
          </div>
          <span className="text-xs text-gray-300 font-medium">{userEmail}</span>
        </div>
      </div>
    </header>
  );
}
