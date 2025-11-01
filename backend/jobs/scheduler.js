import cron from 'node-cron';
import fs from 'node:fs';
import path from 'node:path';

const logsDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', 'shared', 'logs');
fs.mkdirSync(logsDir, { recursive: true });

export function registerJobs () {
  cron.schedule('0 * * * *', () => {
    const logLine = `${new Date().toISOString()} - Background sync executed (offline-safe placeholder)\n`;
    fs.appendFileSync(path.join(logsDir, 'jobs.log'), logLine);
  });
}
