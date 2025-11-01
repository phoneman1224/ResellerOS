import { useState } from 'react';
import DataTable from '../components/DataTable.jsx';
import { useCollection } from '../hooks/useCollection.js';
import { useApi } from '../context/ApiContext.jsx';
import { formatCurrency, formatDate } from '../lib/formatters.js';

const initialForm = {
  platform: 'ebay',
  sale_price: '',
  fees: '',
  shipping_cost: '',
  sale_date: '',
  status: 'completed'
};

function SalesPage () {
  const { items, refresh } = useCollection('sales');
  const api = useApi();
  const [form, setForm] = useState(initialForm);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await api.create('sales', {
      ...form,
      sale_price: Number(form.sale_price || 0),
      fees: Number(form.fees || 0),
      shipping_cost: Number(form.shipping_cost || 0)
    });
    setForm(initialForm);
    refresh();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-semibold mb-4">Record Sale</h2>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="space-y-1 text-sm">
            <span>Platform</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.platform} onChange={(e) => setForm({ ...form, platform: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Sale Price</span>
            <input type="number" step="0.01" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.sale_price} onChange={(e) => setForm({ ...form, sale_price: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Fees</span>
            <input type="number" step="0.01" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.fees} onChange={(e) => setForm({ ...form, fees: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Shipping Cost</span>
            <input type="number" step="0.01" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.shipping_cost} onChange={(e) => setForm({ ...form, shipping_cost: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Sale Date</span>
            <input type="date" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.sale_date} onChange={(e) => setForm({ ...form, sale_date: e.target.value })} />
          </label>
          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="rounded bg-primary px-4 py-2 text-sm font-semibold text-white">Save Sale</button>
          </div>
        </form>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Sales</h2>
          <button className="text-sm text-accent" onClick={refresh}>Refresh</button>
        </div>
        <DataTable
          columns={[
            { header: 'Platform', accessor: 'platform' },
            { header: 'Sale Price', accessor: 'sale_price', render: formatCurrency },
            { header: 'Fees', accessor: 'fees', render: formatCurrency },
            { header: 'Date', accessor: 'sale_date', render: formatDate }
          ]}
          data={items}
        />
      </section>
    </div>
  );
}

export default SalesPage;
