import {
  listResearchSessions,
  getResearchSession,
  createResearchSession,
  updateResearchSession,
  deleteResearchSession
} from '../models/researchModel.js';
import { researchService } from '../services/researchService.js';

export const researchController = {
  index: (_req, res) => {
    res.json(listResearchSessions());
  },
  show: (req, res) => {
    const session = getResearchSession(Number(req.params.id));
    if (!session) return res.status(404).json({ message: 'Research session not found' });
    res.json(session);
  },
  create: async (req, res) => {
    const payload = req.body;
    const findings = await researchService.performResearch(payload.topic, payload.sources || []);
    const session = createResearchSession({
      topic: payload.topic,
      data_sources: findings.sources,
      summary: findings.summary,
      insights: findings.insights
    });
    res.status(201).json(session);
  },
  update: (req, res) => {
    const id = Number(req.params.id);
    const session = getResearchSession(id);
    if (!session) return res.status(404).json({ message: 'Research session not found' });
    res.json(updateResearchSession(id, req.body));
  },
  destroy: (req, res) => {
    const id = Number(req.params.id);
    const session = getResearchSession(id);
    if (!session) return res.status(404).json({ message: 'Research session not found' });
    deleteResearchSession(id);
    res.status(204).end();
  }
};
