import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FileText, GitCompare, Shield } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/compare', label: 'Compare', icon: GitCompare },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-shrink-0 border-r border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 lg:block">
      <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6 dark:border-gray-700">
        <Shield className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
        <span className="text-lg font-bold text-gray-900 dark:text-white">LegalAI</span>
      </div>
      <nav className="mt-4 space-y-1 px-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
