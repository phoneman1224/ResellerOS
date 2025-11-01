import { useState } from 'react';
import DataTable from '../components/DataTable.jsx';
import { useCollection } from '../hooks/useCollection.js';
import { useApi } from '../context/ApiContext.jsx';
import axios from 'axios';

const initialForm = {
  title: '',
  description: '',
  price: '',
  inventory_ids: [],
  status: 'draft'
};

function ListingsPage () {
  const api = useApi();
  const listings = useCollection('listings');
  const inventory = useCollection('inventory');
  const [form, setForm] = useState(initialForm);
  const [seoSuggestion, setSeoSuggestion] = useState(null);
  const [pricingInsight, setPricingInsight] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await api.create('listings', {
      ...form,
      price: Number(form.price || 0),
      inventory_ids: form.inventory_ids
    });
    setForm(initialForm);
    setSeoSuggestion(null);
    setPricingInsight(null);
    listings.refresh();
  };

  const toggleInventoryId = (id) => {
    setForm((prev) => {
      const selected = new Set(prev.inventory_ids);
      if (selected.has(id)) {
        selected.delete(id);
      } else {
        selected.add(id);
      }
      return { ...prev, inventory_ids: Array.from(selected) };
    });
  };

  const requestSeo = async () => {
    const { data } = await axios.post('/api/listings/seo', {
      title: form.title,
      description: form.description,
      inventory_ids: form.inventory_ids,
      price: form.price
    });
    setSeoSuggestion(data);
  };

  const requestPricing = async () => {
    const { data } = await axios.post('/api/listings/pricing', {
      inventory_ids: form.inventory_ids,
      price: form.price
    });
    setPricingInsight(data);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-semibold mb-4">Create Listing</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-1 text-sm">
              <span>Title</span>
              <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
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
            <h3 className="text-sm font-semibold text-slate-300">Attach Inventory</h3>
            <div className="grid gap-2 md:grid-cols-3">
              {inventory.items.map((item) => (
                <label key={item.id} className="flex items-center gap-2 rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm">
                  <input type="checkbox" checked={form.inventory_ids.includes(item.id)} onChange={() => toggleInventoryId(item.id)} />
                  <span>{item.name}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={requestSeo} className="rounded border border-accent px-3 py-2 text-sm text-accent">AI SEO Suggestion</button>
            <button type="button" onClick={requestPricing} className="rounded border border-primary px-3 py-2 text-sm text-primary">AI Pricing Insight</button>
            <button type="submit" className="ml-auto rounded bg-primary px-4 py-2 text-sm font-semibold text-white">Save Listing</button>
          </div>
        </form>

        {(seoSuggestion || pricingInsight) && (
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {seoSuggestion && (
              <article className="rounded border border-slate-800 bg-slate-950 p-4 text-sm space-y-2">
                <h3 className="font-semibold text-white">SEO Suggestion</h3>
                <pre className="whitespace-pre-wrap text-slate-300 text-xs">{JSON.stringify(seoSuggestion, null, 2)}</pre>
              </article>
            )}
            {pricingInsight && (
              <article className="rounded border border-slate-800 bg-slate-950 p-4 text-sm space-y-2">
                <h3 className="font-semibold text-white">Pricing Insight</h3>
                <pre className="whitespace-pre-wrap text-slate-300 text-xs">{JSON.stringify(pricingInsight, null, 2)}</pre>
              </article>
            )}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Listings</h2>
          <button className="text-sm text-accent" onClick={listings.refresh}>Refresh</button>
        </div>
        <DataTable
          columns={[
            { header: 'Title', accessor: 'title' },
            { header: 'Price', accessor: 'price' },
            { header: 'Status', accessor: 'status' }
          ]}
          data={listings.items}
        />
      </section>
    </div>
  );
}

export default ListingsPage;
