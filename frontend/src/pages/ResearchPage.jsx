import { useState } from 'react';
import DataTable from '../components/DataTable.jsx';
import { useCollection } from '../hooks/useCollection.js';
import { useApi } from '../context/ApiContext.jsx';

const initialForm = {
  topic: '',
  sources: 'ebay,reddit'
};

function ResearchPage () {
  const sessions = useCollection('research');
  const api = useApi();
  const [form, setForm] = useState(initialForm);
  const [pending, setPending] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setPending(true);
    await api.create('research', {
      topic: form.topic,
      sources: form.sources.split(',').map((source) => source.trim()).filter(Boolean)
    });
    setForm(initialForm);
    setPending(false);
    sessions.refresh();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <h2 className="text-lg font-semibold mb-4">AI Research</h2>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="space-y-1 text-sm">
            <span>Topic</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} required />
          </label>
          <label className="space-y-1 text-sm">
            <span>Sources</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={form.sources} onChange={(e) => setForm({ ...form, sources: e.target.value })} />
          </label>
          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="rounded bg-primary px-4 py-2 text-sm font-semibold text-white" disabled={pending}>
              {pending ? 'Running research…' : 'Run Research'}
            </button>
          </div>
        </form>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Research Sessions</h2>
          <button className="text-sm text-accent" onClick={sessions.refresh}>Refresh</button>
        </div>
        <DataTable
          columns={[
            { header: 'Topic', accessor: 'topic' },
            { header: 'Summary', accessor: 'summary' },
            { header: 'Created', accessor: 'created_at' }
          ]}
          data={sessions.items}
        />
      </section>
    </div>
  );
}

export default ResearchPage;
