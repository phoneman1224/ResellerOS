import db from '../utils/database.js';
import { mapRows, toJSON, fromJSON } from '../utils/serializers.js';

const table = 'inventory_items';
const jsonFields = ['tags', 'photos'];

export function listInventory () {
  const stmt = db.prepare(`SELECT * FROM ${table} ORDER BY created_at DESC`);
  return mapRows(stmt.all(), jsonFields);
}

export function getInventoryItem (id) {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) return null;
  const mapped = { ...row };
  jsonFields.forEach((field) => { mapped[field] = fromJSON(row[field]); });
  return mapped;
}

export function createInventoryItem (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (name, sku, category, condition, cost, source, quantity, tags, photos, notes) VALUES (@name, @sku, @category, @condition, @cost, @source, @quantity, @tags, @photos, @notes)`);
  const info = stmt.run({
    ...payload,
    tags: toJSON(payload.tags || []),
    photos: toJSON(payload.photos || [])
  });
  return getInventoryItem(info.lastInsertRowid);
}

export function updateInventoryItem (id, payload) {
  const stmt = db.prepare(`UPDATE ${table} SET name=@name, sku=@sku, category=@category, condition=@condition, cost=@cost, source=@source, quantity=@quantity, tags=@tags, photos=@photos, notes=@notes, updated_at=CURRENT_TIMESTAMP WHERE id=@id`);
  stmt.run({
    ...payload,
    id,
    tags: toJSON(payload.tags || []),
    photos: toJSON(payload.photos || [])
  });
  return getInventoryItem(id);
}

export function deleteInventoryItem (id) {
  const stmt = db.prepare(`DELETE FROM ${table} WHERE id = ?`);
  return stmt.run(id);
}
