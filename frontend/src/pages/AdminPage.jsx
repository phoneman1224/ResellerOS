import { useEffect, useState } from 'react';
import { useApi } from '../context/ApiContext.jsx';

const defaultSettings = {
  business_name: '',
  currency: 'USD',
  tax_brackets: '[]'
};

function AdminPage () {
  const api = useApi();
  const [settings, setSettings] = useState(defaultSettings);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    async function loadSettings () {
      const { data } = await api.client.get('/settings');
      setSettings({
        ...data,
        tax_brackets: JSON.stringify(data.tax_brackets || [])
      });
    }
    loadSettings();
  }, [api]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const payload = {
      business_name: settings.business_name,
      currency: settings.currency,
      tax_brackets: JSON.parse(settings.tax_brackets || '[]')
    };
    const { data } = await api.client.put('/settings', payload);
    setSettings({ ...data, tax_brackets: JSON.stringify(data.tax_brackets || []) });
    setMessage('Settings saved');
    setTimeout(() => setMessage(null), 3000);
  };

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">System Settings</h2>
          {message && <span className="text-sm text-accent">{message}</span>}
        </div>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="space-y-1 text-sm">
            <span>Business Name</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={settings.business_name} onChange={(e) => setSettings({ ...settings, business_name: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm">
            <span>Currency</span>
            <input className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" value={settings.currency} onChange={(e) => setSettings({ ...settings, currency: e.target.value })} />
          </label>
          <label className="space-y-1 text-sm md:col-span-2">
            <span>Tax Brackets (JSON)</span>
            <textarea className="w-full rounded bg-slate-950 border border-slate-800 px-3 py-2" rows="4" value={settings.tax_brackets} onChange={(e) => setSettings({ ...settings, tax_brackets: e.target.value })} />
          </label>
          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="rounded bg-primary px-4 py-2 text-sm font-semibold text-white">Save Settings</button>
          </div>
        </form>
      </section>

      <section className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 space-y-3">
        <h2 className="text-lg font-semibold">Data Control</h2>
        <p className="text-sm text-slate-300">
          Back up your data by copying <code>db/database.sqlite</code>. Import/export tools for CSV and JSON are accessible under each module.
        </p>
        <p className="text-sm text-slate-400">
          API base URL: <code>http://localhost:4000/api</code>
        </p>
        <p className="text-sm text-slate-400">
          Logs are written to <code>shared/logs/jobs.log</code> for background jobs.
        </p>
      </section>
    </div>
  );
}

export default AdminPage;
