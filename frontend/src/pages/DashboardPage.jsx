import { useMemo } from 'react';
import { useCollection } from '../hooks/useCollection.js';
import StatsCard from '../components/StatsCard.jsx';
import DataTable from '../components/DataTable.jsx';
import { formatCurrency, formatDate } from '../lib/formatters.js';

function DashboardPage () {
  const inventory = useCollection('inventory');
  const sales = useCollection('sales');
  const expenses = useCollection('expenses');

  const kpis = useMemo(() => {
    const totalCost = inventory.items.reduce((acc, item) => acc + Number(item.cost || 0), 0);
    const totalSales = sales.items.reduce((acc, sale) => acc + Number(sale.sale_price || 0), 0);
    const totalExpenses = expenses.items.reduce((acc, expense) => acc + Number(expense.amount || 0), 0);
    return {
      inventoryCount: inventory.items.length,
      totalCost,
      totalSales,
      grossProfit: totalSales - totalCost - totalExpenses
    };
  }, [inventory.items, sales.items, expenses.items]);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard title="Active SKUs" value={kpis.inventoryCount} subtitle="Manageable inventory on hand" />
        <StatsCard title="Inventory Cost" value={formatCurrency(kpis.totalCost)} subtitle="Total COGS" />
        <StatsCard title="Sales Revenue" value={formatCurrency(kpis.totalSales)} subtitle="Lifetime tracked sales" />
        <StatsCard title="Estimated Profit" value={formatCurrency(kpis.grossProfit)} subtitle="Revenue - cost - expenses" />
      </div>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Recent Inventory</h2>
          <DataTable
            columns={[
              { header: 'Name', accessor: 'name' },
              { header: 'Category', accessor: 'category' },
              { header: 'Cost', accessor: 'cost', render: formatCurrency },
              { header: 'Updated', accessor: 'updated_at', render: formatDate }
            ]}
            data={inventory.items.slice(0, 5)}
          />
        </div>
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Latest Sales</h2>
          <DataTable
            columns={[
              { header: 'Platform', accessor: 'platform' },
              { header: 'Sale Price', accessor: 'sale_price', render: formatCurrency },
              { header: 'Fees', accessor: 'fees', render: formatCurrency },
              { header: 'Date', accessor: 'sale_date', render: formatDate }
            ]}
            data={sales.items.slice(0, 5)}
          />
        </div>
      </section>
    </div>
  );
}

export default DashboardPage;
