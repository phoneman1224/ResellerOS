import db from '../utils/database.js';
import { mapRows, toJSON, fromJSON } from '../utils/serializers.js';

const table = 'research_sessions';
const jsonFields = ['data_sources', 'insights'];

export function listResearchSessions () {
  const stmt = db.prepare(`SELECT * FROM ${table} ORDER BY created_at DESC`);
  return mapRows(stmt.all(), jsonFields);
}

export function getResearchSession (id) {
  const stmt = db.prepare(`SELECT * FROM ${table} WHERE id = ?`);
  const row = stmt.get(id);
  if (!row) return null;
  const mapped = { ...row };
  jsonFields.forEach((field) => { mapped[field] = fromJSON(row[field]); });
  return mapped;
}

export function createResearchSession (payload) {
  const stmt = db.prepare(`INSERT INTO ${table} (topic, data_sources, summary, insights) VALUES (@topic, @data_sources, @summary, @insights)`);
  const info = stmt.run({
    ...payload,
    data_sources: toJSON(payload.data_sources || []),
    insights: toJSON(payload.insights || [])
  });
  return getResearchSession(info.lastInsertRowid);
}

export function updateResearchSession (id, payload) {
  const stmt = db.prepare(`UPDATE ${table} SET topic=@topic, data_sources=@data_sources, summary=@summary, insights=@insights WHERE id=@id`);
  stmt.run({
    ...payload,
    id,
    data_sources: toJSON(payload.data_sources || []),
    insights: toJSON(payload.insights || [])
  });
  return getResearchSession(id);
}

export function deleteResearchSession (id) {
  const stmt = db.prepare(`DELETE FROM ${table} WHERE id = ?`);
  return stmt.run(id);
}
