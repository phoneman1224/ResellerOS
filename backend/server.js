import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'node:path';
import fs from 'node:fs';
import apiRoutes from './routes/index.js';
import { registerJobs } from './jobs/scheduler.js';

const app = express();
const upload = multer({ dest: path.join(process.cwd(), 'uploads') });
const PORT = process.env.PORT || 4000;

fs.mkdirSync(path.join(process.cwd(), 'uploads'), { recursive: true });

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(path.join(process.cwd(), 'uploads')));

app.post('/api/uploads', upload.single('file'), (req, res) => {
  res.status(201).json({ filename: req.file.filename, originalname: req.file.originalname });
});

app.use('/api', apiRoutes);

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

registerJobs();

app.listen(PORT, () => {
  console.log(`ResellerOS backend listening on http://localhost:${PORT}`);
});
