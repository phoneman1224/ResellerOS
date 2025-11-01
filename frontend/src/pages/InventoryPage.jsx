import { useState } from 'react';
import DataTable from '../components/DataTable.jsx';
import { useCollection } from '../hooks/useCollection.js';
import { useApi } from '../context/ApiContext.jsx';

const initialForm = {
  name: '',
  sku: '',
  category: '',
  condition: '',
  cost: '',
  source: '',
  quantity: 1,
  tags: ''
};

function InventoryPage () {
  const { items, refresh } = useCollection('inventory');
  const api = useApi();
  const [form, setForm] = useState(initialForm);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await api.create('inventory', {
      ...form,
      cost: Number(form.cost || 0),
      quantity: Number(form.quantity || 1),
      tags: form.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
    });
    setForm(initialForm);
    refresh();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-semibold mb-4">Add Inventory Item</h2>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="space-y-1 text-sm">
            <span>Name</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label className="space-y-1 text-sm">
            <span>SKU</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Category</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Condition</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Cost</span>
            <input type="number" step="0.01" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Source</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Quantity</span>
            <input type="number" min="1" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm md:col-span-2">
            <span>Tags (comma separated)</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} />
          </label>
          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="rounded bg-primary px-4 py-2 text-sm font-semibold text-white">Save Item</button>
          </div>
        </form>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Inventory</h2>
          <button className="text-sm text-accent" onClick={refresh}>Refresh</button>
        </div>
        <DataTable
          columns={[
            { header: 'Name', accessor: 'name' },
            { header: 'SKU', accessor: 'sku' },
            { header: 'Category', accessor: 'category' },
            { header: 'Quantity', accessor: 'quantity' }
          ]}
          data={items}
        />
      </section>
    </div>
  );
}

export default InventoryPage;
