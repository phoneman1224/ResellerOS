import db from '../utils/database.js';
import { mapRows, toJSON, fromJSON } from '../utils/serializers.js';

const table = 'expenses';
const jsonFields = ['related_inventory_ids', 'related_lot_ids'];

export function listExpenses () {
  const stmt = db.prepare(`SELECT * FROM ${table} ORDER BY incurred_on DESC NULLS LAST, created_at DESC`);
  return mapRows(stmt.all(), jsonFields);
}

export function getExpense (id) {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) return null;
  const mapped = { ...row };
  jsonFields.forEach((field) => { mapped[field] = fromJSON(row[field]); });
  return mapped;
}

export function createExpense (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (name, amount, category, deductible, recurring_interval, related_inventory_ids, related_lot_ids, notes, incurred_on) VALUES (@name, @amount, @category, @deductible, @recurring_interval, @related_inventory_ids, @related_lot_ids, @notes, @incurred_on)`);
  const info = stmt.run({
    ...payload,
    related_inventory_ids: toJSON(payload.related_inventory_ids || []),
    related_lot_ids: toJSON(payload.related_lot_ids || [])
  });
  return getExpense(info.lastInsertRowid);
}

export function updateExpense (id, payload) {
  const stmt = db.prepare(`UPDATE ${table} SET name=@name, amount=@amount, category=@category, deductible=@deductible, recurring_interval=@recurring_interval, related_inventory_ids=@related_inventory_ids, related_lot_ids=@related_lot_ids, notes=@notes, incurred_on=@incurred_on, updated_at=CURRENT_TIMESTAMP WHERE id=@id`);
  stmt.run({
    ...payload,
    id,
    related_inventory_ids: toJSON(payload.related_inventory_ids || []),
    related_lot_ids: toJSON(payload.related_lot_ids || [])
  });
  return getExpense(id);
}

export function deleteExpense (id) {
  const stmt = db.prepare(`DELETE FROM ${table} WHERE id = ?`);
  return stmt.run(id);
}
