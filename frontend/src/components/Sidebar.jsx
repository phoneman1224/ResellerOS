import { NavLink } from 'react-router-dom';

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/inventory', label: 'Inventory' },
  { to: '/listings', label: 'Listings' },
  { to: '/lots', label: 'Lots' },
  { to: '/expenses', label: 'Expenses' },
  { to: '/sales', label: 'Sales' },
  { to: '/research', label: 'Research' },
  { to: '/admin', label: 'Admin' }
];

const activeClass = ({ isActive }) =>
  `block px-4 py-2 rounded-md transition ${isActive ? 'bg-primary/80 text-white' : 'text-slate-300 hover:bg-slate-800'}`;

function Sidebar () {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 p-4 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">ResellerOS</h1>
        <p className="text-sm text-slate-400">Offline-first control center</p>
      </div>
      <nav className="space-y-2">
        {links.map((link) => (
          <NavLink key={link.to} to={link.to} className={activeClass}>
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className="text-xs text-slate-500">
        <p>AI ready. Works even when offline.</p>
      </div>
    </aside>
  );
}

export default Sidebar;
