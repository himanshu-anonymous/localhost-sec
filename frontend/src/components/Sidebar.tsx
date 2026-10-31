import React from 'react';
import { 
  LayoutGrid, 
  Network, 
  Sliders, 
  Box, 
  BarChart3, 
  Sparkles, 
  FileText, 
  Settings, 
  ShieldAlert, 
  ChevronDown,
  Layers,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutGrid },
    { id: 'simulations', label: 'Simulations', icon: Network },
    { id: 'policy-stack', label: 'Policy stack', icon: Sliders },
    { id: 'cyber-range', label: 'Cyber-range', icon: Box },
    { id: 'benchmarks', label: 'Benchmarks', icon: BarChart3 },
    { id: 'ai-reasoning', label: 'AI reasoning', icon: Sparkles },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 h-screen sticky top-0 overflow-y-auto">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded bg-[#dc2626] flex items-center justify-center text-white shadow-sm">
              <ShieldAlert className="w-5 h-5 fill-white" />
            </div>
            <div>
              <div className="font-bold text-slate-900 tracking-wider text-sm flex items-center gap-1.5">
                BASTION X
              </div>
              <div className="text-[10px] text-slate-400 font-semibold tracking-widest uppercase">
                DEFENCE SIMULATOR
              </div>
            </div>
          </div>
        </div>

        {/* Workspace Selector */}
        <div className="px-5 pt-4 pb-2">
          <label className="text-[10px] font-bold tracking-wider text-slate-400 uppercase block mb-1.5">
            WORKSPACE
          </label>
          <div className="flex items-center justify-between border border-slate-200 rounded-md px-3 py-2 text-xs font-semibold text-slate-800 bg-white hover:bg-slate-50 cursor-pointer shadow-2xs">
            <span>localhost</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </div>
        </div>

        {/* Navigation Items */}
        <div className="px-3 pt-3">
          <label className="text-[10px] font-bold tracking-wider text-slate-400 uppercase block px-2 mb-2">
            OPERATIONS
          </label>
          <nav className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-md transition-all text-left ${
                    isActive
                      ? 'bg-[#dc2626] text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Isolated by design Card */}
        <div className="p-4 mx-3 mt-6 border border-red-100 bg-red-50/40 rounded-lg">
          <div className="flex items-center gap-1.5 text-xs font-bold text-red-900 mb-1">
            <Cpu className="w-3.5 h-3.5 text-[#dc2626]" />
            <span>Isolated by design</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-600">
            Train, evaluate and benchmark policies across private networks.
          </p>
        </div>
      </div>

      {/* Footer Area */}
      <div className="p-4 border-t border-slate-200 space-y-2">
        <a 
          href="/docs" 
          target="_blank" 
          rel="noreferrer"
          className="flex items-center gap-2.5 text-xs text-slate-500 hover:text-slate-800 py-1"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Documentation</span>
        </a>
        <div className="flex items-center gap-2.5 text-xs text-slate-500 hover:text-slate-800 py-1 cursor-pointer">
          <Settings className="w-3.5 h-3.5" />
          <span>Workspace settings</span>
        </div>
        <div className="pt-2 flex items-center gap-2.5">
          <div className="w-5 h-5 rounded bg-[#dc2626] text-[10px] font-bold text-white flex items-center justify-center">
            EX
          </div>
          <div className="text-[11px] leading-tight">
            <div className="font-semibold text-slate-800">Local workspace</div>
            <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">SIMULATED ONLY</div>
          </div>
        </div>
      </div>
    </aside>
  );
};

