import path from 'node:path';
import fs from 'node:fs';
import { aiService } from './aiService.js';

const cacheDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..', 'shared');
fs.mkdirSync(cacheDir, { recursive: true });

export const researchService = {
  async performResearch (topic, sources = []) {
    const normalizedSources = sources.length ? sources : ['ebay', 'reddit', 'youtube'];
    const snapshot = normalizedSources.map((source) => ({
      source,
      entries: this.loadCachedData(source, topic)
    }));

    const aiSummary = await aiService.generateMarketingCopy({
      name: `Research summary for ${topic}`,
      price: 0,
      tags: normalizedSources
    });

    return {
      summary: aiSummary.raw || 'Research summary generated via heuristic marketing copy.',
      insights: snapshot.map(({ source, entries }) => ({
        source,
        highlight: entries.length ? entries[0].title : `No cached data for ${source}`
      })),
      sources: snapshot
    };
  },

  loadCachedData (source, topic) {
    const file = path.join(cacheDir, `${source}-${topic.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.json`);
    if (fs.existsSync(file)) {
      try {
        return JSON.parse(fs.readFileSync(file, 'utf8'));
      } catch (error) {
        console.warn('Failed to parse cached research file', file, error.message);
      }
    }
    return [];
  }
};
