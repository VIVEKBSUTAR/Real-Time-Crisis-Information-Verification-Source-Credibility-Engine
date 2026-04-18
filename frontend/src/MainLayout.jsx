import React, { useState } from 'react';
import {
  Menu,
  X,
  Radar,
  ShieldAlert,
  Archive,
  BarChart3,
  Search,
  Bell,
  UserCircle2,
  Settings,
  Plus,
  HelpCircle,
  ArrowRightFromLine,
} from 'lucide-react';
import Intelligence from './pages/Intelligence';
import ActiveThreats from './pages/ActiveThreats';
import Archived from './pages/Archived';
import Analytics from './pages/Analytics';

export default function MainLayout() {
  const [activePage, setActivePage] = useState('intelligence');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { id: 'intelligence', label: 'Intelligence', icon: Radar },
    { id: 'threats', label: 'Active Threats', icon: ShieldAlert },
    { id: 'archived', label: 'Archived', icon: Archive },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  const renderPage = () => {
    switch (activePage) {
      case 'intelligence':
        return <Intelligence />;
      case 'threats':
        return <ActiveThreats />;
      case 'archived':
        return <Archived />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Intelligence />;
    }
  };

  const handleNavigate = (pageId) => {
    setActivePage(pageId);
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  const activeTitle = navItems.find((item) => item.id === activePage)?.label || 'Intelligence';

  return (
    <div className="w-screen h-screen flex flex-col bg-slate-100">
      <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 text-slate-100 px-6 py-2.5 flex-shrink-0 shadow-md">
        <div className="max-w-[1600px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold bg-white/10 border border-white/20 px-3 py-1 rounded-full tracking-wide">LIVE</span>
            <span className="text-xs font-medium text-slate-200">System monitoring 26,232 claims</span>
          </div>
          <div className="text-xs font-medium text-emerald-300">● Status: Operational</div>
        </div>
      </div>

      <div className="bg-white border-b border-slate-200 px-6 py-3 flex-shrink-0">
        <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-5">
          <div className="flex items-center gap-3 min-w-[220px]">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-slate-100 rounded-lg lg:hidden text-slate-700"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-xl font-bold text-slate-900">Sentinel Protocol</h1>
          </div>

          <div className="flex-1 max-w-xl relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              placeholder="Search cross-platform intelligence..."
              className="w-full bg-slate-100 border border-slate-200 rounded-lg py-2 pl-9 pr-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition">
              <Bell size={18} />
            </button>
            <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition">
              <Settings size={18} />
            </button>
            <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition">
              <UserCircle2 size={20} />
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-white border-r border-slate-200 transition-all duration-300 overflow-y-auto flex-shrink-0 flex flex-col`}>
          <div className="p-4 border-b border-slate-200">
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
              <p className="text-lg font-bold text-slate-900 leading-5">Sentinel</p>
              <p className="text-lg font-bold text-slate-900 leading-5">Protocol</p>
              <p className="text-[10px] text-slate-500 tracking-widest mt-1 font-semibold">INTELLIGENCE OPS</p>
            </div>
          </div>

          <nav className="p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg font-medium transition flex items-center gap-3 text-sm ${
                    activePage === item.id
                      ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                      : 'text-slate-700 hover:bg-slate-50 border border-transparent'
                  }`}
                >
                  <Icon size={16} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          <div className="mt-auto p-4 border-t border-slate-200 space-y-2">
            <button className="w-full inline-flex items-center justify-center gap-2 bg-indigo-700 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-indigo-800 transition">
              <Plus size={16} />
              New Report
            </button>
            <button className="w-full inline-flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">
              <HelpCircle size={15} />
              Support
            </button>
            <button className="w-full inline-flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">
              <ArrowRightFromLine size={15} />
              Sign Out
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto bg-slate-100">
          <div className="px-8 pt-6 pb-2 border-b border-slate-200 bg-slate-100">
            <p className="text-[11px] uppercase tracking-[0.2em] font-bold text-indigo-600">Command Center</p>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">{activeTitle}</h2>
          </div>
          {renderPage()}
        </div>
      </div>
    </div>
  );
}
