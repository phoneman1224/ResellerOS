import { useState } from 'react';
import DataTable from '../components/DataTable.jsx';
import { useCollection } from '../hooks/useCollection.js';
import { useApi } from '../context/ApiContext.jsx';
import axios from 'axios';

const initialForm = {
  name: '',
  description: '',
  price: '',
  item_ids: [],
  status: 'draft'
};

function LotsPage () {
  const api = useApi();
  const lots = useCollection('lots');
  const inventory = useCollection('inventory');
  const [form, setForm] = useState(initialForm);
  const [seoSuggestion, setSeoSuggestion] = useState(null);

  const toggleItem = (id) => {
    setForm((prev) => {
      const selected = new Set(prev.item_ids);
      if (selected.has(id)) selected.delete(id); else selected.add(id);
      return { ...prev, item_ids: Array.from(selected) };
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await api.create('lots', {
      ...form,
      price: Number(form.price || 0)
    });
    setForm(initialForm);
    setSeoSuggestion(null);
    lots.refresh();
  };

  const requestSeo = async () => {
    const { data } = await axios.post('/api/lots/seo', {
      ...form,
      price: Number(form.price || 0)
    });
    setSeoSuggestion(data);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-semibold mb-4">Create Lot</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-1 text-sm">
              <span>Name</span>
              <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </label>
            <label className="space-y-1 text-sm">
              <span>Price</span>
              <input type="number" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
            </label>
          </div>
          <label className="space-y-1 text-sm block">
            <span>Description</span>
            <textarea className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" rows="4" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-300">Bundle Inventory</h3>
            <div className="grid gap-2 md:grid-cols-3">
              {inventory.items.map((item) => (
                <label key={item.id} className="flex items-center gap-2 rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm">
                  <input type="checkbox" checked={form.item_ids.includes(item.id)} onChange={() => toggleItem(item.id)} />
                  <span>{item.name}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={requestSeo} className="rounded border border-accent px-3 py-2 text-sm text-accent">AI SEO for Lot</button>
            <button type="submit" className="ml-auto rounded bg-primary px-4 py-2 text-sm font-semibold text-white">Save Lot</button>
          </div>
        </form>

        {seoSuggestion && (
          <article className="mt-6 rounded border border-slate-800 bg-slate-950 p-4 text-sm space-y-2">
            <h3 className="font-semibold text-white">SEO Suggestion</h3>
            <pre className="whitespace-pre-wrap text-slate-300 text-xs">{JSON.stringify(seoSuggestion, null, 2)}</pre>
          </article>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Lots</h2>
          <button className="text-sm text-accent" onClick={lots.refresh}>Refresh</button>
        </div>
        <DataTable
          columns={[
            { header: 'Name', accessor: 'name' },
            { header: 'Price', accessor: 'price' },
            { header: 'Status', accessor: 'status' }
          ]}
          data={lots.items}
        />
      </section>
    </div>
  );
}

export default LotsPage;
