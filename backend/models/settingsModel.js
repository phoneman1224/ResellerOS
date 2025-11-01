import db from '../utils/database.js';
import { fromJSON, toJSON } from '../utils/serializers.js';

const table = 'settings';
const id = 1;

export function getSettings () {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) {
    const defaults = {
      id,
      business_name: null,
      tax_brackets: [],
      currency: 'USD',
      ebay_api_config: null
    };
    setSettings(defaults);
    return defaults;
  }
  return {
    ...row,
    tax_brackets: fromJSON(row.tax_brackets) || [],
    ebay_api_config: fromJSON(row.ebay_api_config) || null
  };
}

export function setSettings (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (id, business_name, tax_brackets, currency, ebay_api_config) VALUES (@id, @business_name, @tax_brackets, @currency, @ebay_api_config) ON CONFLICT(id) DO UPDATE SET business_name=excluded.business_name, tax_brackets=excluded.tax_brackets, currency=excluded.currency, ebay_api_config=excluded.ebay_api_config, updated_at=CURRENT_TIMESTAMP`);
  stmt.run({
    id,
    business_name: payload.business_name || null,
    tax_brackets: toJSON(payload.tax_brackets || []),
    currency: payload.currency || 'USD',
    ebay_api_config: toJSON(payload.ebay_api_config || null)
  });
  return getSettings();
}
