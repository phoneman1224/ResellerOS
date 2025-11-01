import { useState } from 'react';
import DataTable from '../components/DataTable.jsx';
import { useCollection } from '../hooks/useCollection.js';
import { useApi } from '../context/ApiContext.jsx';
import { formatCurrency, formatDate } from '../lib/formatters.js';

const initialForm = {
  name: '',
  amount: '',
  category: '',
  deductible: true,
  recurring_interval: '',
  incurred_on: ''
};

function ExpensesPage () {
  const { items, refresh } = useCollection('expenses');
  const api = useApi();
  const [form, setForm] = useState(initialForm);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await api.create('expenses', {
      ...form,
      amount: Number(form.amount || 0),
      deductible: form.deductible ? 1 : 0
    });
    setForm(initialForm);
    refresh();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-semibold mb-4">Log Expense</h2>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="space-y-1 text-sm">
            <span>Name</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </label>
          <label className="space-y-1 text-sm">
            <span>Amount</span>
            <input type="number" step="0.01" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Category</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Recurring Interval</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" placeholder="monthly" value={form.recurring_interval} onChange={(e) => setForm({ ...form, recurring_interval: e.target.value })} />
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.deductible} onChange={(e) => setForm({ ...form, deductible: e.target.checked })} />
            <span>Deductible</span>
          </label>
          <label className="space-y-1 text-sm">
            <span>Date</span>
            <input type="date" className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.incurred_on} onChange={(e) => setForm({ ...form, incurred_on: e.target.value })} />
          </label>
          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="rounded bg-primary px-4 py-2 text-sm font-semibold text-white">Save Expense</button>
          </div>
        </form>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Expenses</h2>
          <button className="text-sm text-accent" onClick={refresh}>Refresh</button>
        </div>
        <DataTable
          columns={[
            { header: 'Name', accessor: 'name' },
            { header: 'Amount', accessor: 'amount', render: formatCurrency },
            { header: 'Category', accessor: 'category' },
            { header: 'Date', accessor: 'incurred_on', render: formatDate }
          ]}
          data={items}
        />
      </section>
    </div>
  );
}

export default ExpensesPage;
