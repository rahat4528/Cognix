'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  UploadCloud,
  Crosshair,
  Sparkles,
  Search,
  Video,
  Cpu,
  Layers,
  ShieldCheck
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Workbench', href: '/', icon: LayoutDashboard },
  { name: 'Upload Studio', href: '/upload', icon: UploadCloud },
  { name: 'Object Detection', href: '/detection', icon: Crosshair },
  { name: 'Classification & CAM', href: '/classification', icon: Sparkles },
  { name: 'Visual Similarity', href: '/similarity', icon: Search },
  { name: 'Live Edge Camera', href: '/camera', icon: Video },
  { name: 'Model Registry', href: '/models', icon: Cpu },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-surface border-r border-surfaceBorder flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand */}
      <div className="h-16 flex items-center px-6 border-b border-surfaceBorder space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
          <Layers className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight text-white">Cognix</span>
          <span className="ml-1.5 text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-primary/20 text-primary border border-primary/30">
            CV AI
          </span>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
          Vision Tools
        </div>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? 'bg-primary text-white shadow-md shadow-primary/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Security & Privacy Footer */}
      <div className="p-4 border-t border-surfaceBorder">
        <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800 flex items-start space-x-2.5 text-xs text-slate-400">
          <ShieldCheck className="w-4 h-4 text-accent shrink-0 mt-0.5" />
          <div>
            <div className="font-medium text-slate-300">Privacy Safeguard</div>
            <div className="text-[11px] text-slate-500 leading-relaxed mt-0.5">
              EXIF stripped. Zero biometric profiling. Authentic PyTorch inference.
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
