import db from '../utils/database.js';
import { mapRows, toJSON, fromJSON } from '../utils/serializers.js';

const table = 'lots';
const jsonFields = ['item_ids', 'photos'];

export function listLots () {
  const stmt = db.prepare(`SELECT * FROM ${table} ORDER BY created_at DESC`);
  return mapRows(stmt.all(), jsonFields);
}

export function getLot (id) {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) return null;
  const mapped = { ...row };
  jsonFields.forEach((field) => { mapped[field] = fromJSON(row[field]); });
  return mapped;
}

export function createLot (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (name, description, price, item_ids, status, photos) VALUES (@name, @description, @price, @item_ids, @status, @photos)`);
  const info = stmt.run({
    ...payload,
    item_ids: toJSON(payload.item_ids || []),
    photos: toJSON(payload.photos || [])
  });
  return getLot(info.lastInsertRowid);
}

export function updateLot (id, payload) {
  const stmt = db.prepare(`UPDATE ${table} SET name=@name, description=@description, price=@price, item_ids=@item_ids, status=@status, photos=@photos, updated_at=CURRENT_TIMESTAMP WHERE id=@id`);
  stmt.run({
    ...payload,
    id,
    item_ids: toJSON(payload.item_ids || []),
    photos: toJSON(payload.photos || [])
  });
  return getLot(id);
}

export function deleteLot (id) {
  const stmt = db.prepare(`DELETE FROM ${table} WHERE id = ?`);
  return stmt.run(id);
}
