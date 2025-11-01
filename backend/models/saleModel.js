import db from '../utils/database.js';
import { mapRows, toJSON, fromJSON } from '../utils/serializers.js';

const table = 'sales';
const jsonFields = ['related_inventory_ids', 'related_lot_ids'];

export function listSales () {
  const stmt = db.prepare(`SELECT * FROM ${table} ORDER BY sale_date DESC NULLS LAST, created_at DESC`);
  return mapRows(stmt.all(), jsonFields);
}

export function getSale (id) {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) return null;
  const mapped = { ...row };
  jsonFields.forEach((field) => { mapped[field] = fromJSON(row[field]); });
  return mapped;
}

export function createSale (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (platform, sale_price, fees, shipping_cost, sale_date, status, related_inventory_ids, related_lot_ids, refunds, notes) VALUES (@platform, @sale_price, @fees, @shipping_cost, @sale_date, @status, @related_inventory_ids, @related_lot_ids, @refunds, @notes)`);
  const info = stmt.run({
    ...payload,
    related_inventory_ids: toJSON(payload.related_inventory_ids || []),
    related_lot_ids: toJSON(payload.related_lot_ids || [])
  });
  return getSale(info.lastInsertRowid);
}

export function updateSale (id, payload) {
  const stmt = db.prepare(`UPDATE ${table} SET platform=@platform, sale_price=@sale_price, fees=@fees, shipping_cost=@shipping_cost, sale_date=@sale_date, status=@status, related_inventory_ids=@related_inventory_ids, related_lot_ids=@related_lot_ids, refunds=@refunds, notes=@notes, updated_at=CURRENT_TIMESTAMP WHERE id=@id`);
  stmt.run({
    ...payload,
    id,
    related_inventory_ids: toJSON(payload.related_inventory_ids || []),
    related_lot_ids: toJSON(payload.related_lot_ids || [])
  });
  return getSale(id);
}

export function deleteSale (id) {
  const stmt = db.prepare(`DELETE FROM ${table} WHERE id = ?`);
  return stmt.run(id);
}
