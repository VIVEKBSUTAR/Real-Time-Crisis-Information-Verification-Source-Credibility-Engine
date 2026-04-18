import React, { useState } from 'react';
import { Menu, X, LogOut, Settings, HelpCircle, Radar, ShieldAlert, Archive, BarChart3 } from 'lucide-react';
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

  return (
    <div className="w-screen h-screen flex flex-col bg-slate-100">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 text-slate-100 px-6 py-3 flex-shrink-0 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold bg-white/10 border border-white/20 px-3 py-1 rounded-full tracking-wide">LIVE</span>
            <span className="text-xs font-medium text-slate-200">System monitoring 26,232 claims</span>
          </div>
          <div className="text-xs font-medium text-emerald-300">● Status: Operational</div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white/95 backdrop-blur border-b border-slate-200 px-6 py-4 flex-shrink-0 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-slate-100 rounded-lg lg:hidden text-slate-700"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-2xl font-bold text-slate-900">Sentinel Protocol</h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition">
              <HelpCircle size={20} />
            </button>
            <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition">
              <Settings size={20} />
            </button>
            <button className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-slate-800 transition">
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } bg-white border-r border-slate-200 transition-all duration-300 overflow-y-auto flex-shrink-0`}>
          <nav className="p-6 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
              <button
                key={item.id}
                onClick={() => {
                  setActivePage(item.id);
                  setSidebarOpen(false);
                }}
                className={`w-full text-left px-4 py-3 rounded-xl font-medium transition flex items-center gap-3 ${
                  activePage === item.id
                    ? 'bg-indigo-50 text-indigo-700 border-l-4 border-indigo-600 shadow-sm'
                    : 'text-slate-700 hover:bg-slate-50 border-l-4 border-transparent'
                }`}
              >
                <Icon size={18} />
                {item.label}
              </button>
              );
            })}
          </nav>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto bg-slate-100">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}
