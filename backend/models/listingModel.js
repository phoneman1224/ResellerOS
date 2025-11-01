import db from '../utils/database.js';
import { mapRows, toJSON, fromJSON } from '../utils/serializers.js';

const table = 'listings';
const jsonFields = ['inventory_ids', 'photos', 'seo_metadata'];

export function listListings () {
  const stmt = db.prepare(`SELECT * FROM ${table} ORDER BY created_at DESC`);
  return mapRows(stmt.all(), jsonFields);
}

export function getListing (id) {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) return null;
  const mapped = { ...row };
  jsonFields.forEach((field) => { mapped[field] = fromJSON(row[field]); });
  return mapped;
}

export function createListing (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (inventory_ids, title, description, price, status, platform, shipping_profile, photos, seo_metadata) VALUES (@inventory_ids, @title, @description, @price, @status, @platform, @shipping_profile, @photos, @seo_metadata)`);
  const info = stmt.run({
    ...payload,
    inventory_ids: toJSON(payload.inventory_ids || []),
    photos: toJSON(payload.photos || []),
    seo_metadata: toJSON(payload.seo_metadata || {})
  });
  return getListing(info.lastInsertRowid);
}

export function updateListing (id, payload) {
  const stmt = db.prepare(`UPDATE ${table} SET inventory_ids=@inventory_ids, title=@title, description=@description, price=@price, status=@status, platform=@platform, shipping_profile=@shipping_profile, photos=@photos, seo_metadata=@seo_metadata, updated_at=CURRENT_TIMESTAMP WHERE id=@id`);
  stmt.run({
    ...payload,
    id,
    inventory_ids: toJSON(payload.inventory_ids || []),
    photos: toJSON(payload.photos || []),
    seo_metadata: toJSON(payload.seo_metadata || {})
  });
  return getListing(id);
}

export function deleteListing (id) {
  const stmt = db.prepare(`DELETE FROM ${table} WHERE id = ?`);
  return stmt.run(id);
}
