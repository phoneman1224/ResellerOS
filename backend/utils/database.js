import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';

const rootDir = path.resolve(process.cwd(), '..');
const dbPath = path.join(rootDir, 'db', 'database.sqlite');
const schemaPath = path.join(rootDir, 'db', 'schema.sql');

fs.mkdirSync(path.dirname(dbPath), { recursive: true });

const db = new Database(dbPath);

db.pragma('journal_mode = WAL');

const schema = fs.readFileSync(schemaPath, 'utf8');
db.exec(schema);

export default db;
