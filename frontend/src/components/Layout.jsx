import PropTypes from 'prop-types';
import Sidebar from './Sidebar.jsx';

function Layout ({ children }) {
  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100">
      <Sidebar />
      <main className="flex-1 p-6 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}

Layout.propTypes = {
  children: PropTypes.node
};

export default Layout;
