import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import InventoryPage from './pages/InventoryPage.jsx';
import ListingsPage from './pages/ListingsPage.jsx';
import LotsPage from './pages/LotsPage.jsx';
import ExpensesPage from './pages/ExpensesPage.jsx';
import SalesPage from './pages/SalesPage.jsx';
import ResearchPage from './pages/ResearchPage.jsx';
import AdminPage from './pages/AdminPage.jsx';
import { ApiProvider } from './context/ApiContext.jsx';

function App () {
  return (
    <ApiProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/listings" element={<ListingsPage />} />
          <Route path="/lots" element={<LotsPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/sales" element={<SalesPage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </Layout>
    </ApiProvider>
  );
}

export default App;
