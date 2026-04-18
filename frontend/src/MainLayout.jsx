import React, { useState } from 'react';
import { Menu, X, LogOut, Settings, HelpCircle } from 'lucide-react';
import Intelligence from './pages/Intelligence';
import ActiveThreats from './pages/ActiveThreats';
import Archived from './pages/Archived';
import Analytics from './pages/Analytics';
import GlobalMap from './pages/GlobalMap';

export default function MainLayout() {
  const [activePage, setActivePage] = useState('intelligence');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { id: 'intelligence', label: 'Intelligence', icon: '🔍' },
    { id: 'threats', label: 'Active Threats', icon: '🚨' },
    { id: 'archived', label: 'Archived', icon: '📦' },
    { id: 'map', label: 'Global Map', icon: '🌍' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
  ];

  const renderPage = () => {
    switch (activePage) {
      case 'intelligence':
        return <Intelligence />;
      case 'threats':
        return <ActiveThreats />;
      case 'archived':
        return <Archived />;
      case 'map':
        return <GlobalMap />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Intelligence />;
    }
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-gray-50">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-red-600 to-red-500 text-white px-6 py-3 flex-shrink-0 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold bg-white bg-opacity-20 px-3 py-1 rounded-full">LIVE</span>
            <span className="text-xs font-medium">System monitoring 26,232 claims</span>
          </div>
          <div className="text-xs font-medium">🔴 Status: Operational</div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg lg:hidden"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Sentinel Protocol</h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900">
              <HelpCircle size={20} />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900">
              <Settings size={20} />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-600 hover:text-gray-900">
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
        } bg-white border-r border-gray-200 transition-all duration-300 overflow-y-auto flex-shrink-0`}>
          <nav className="p-6 space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setActivePage(item.id);
                  setSidebarOpen(false);
                }}
                className={`w-full text-left px-4 py-3 rounded-lg font-medium transition ${
                  activePage === item.id
                    ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600'
                    : 'text-gray-700 hover:bg-gray-50 border-l-4 border-transparent'
                }`}
              >
                <span className="text-xl mr-3">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}
