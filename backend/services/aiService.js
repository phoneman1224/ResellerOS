import fs from 'node:fs';
import path from 'node:path';

const promptsDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'ai_prompts');

function loadPrompt (name) {
  const file = path.join(promptsDir, `${name}.md`);
  if (fs.existsSync(file)) {
    return fs.readFileSync(file, 'utf8');
  }
  return '';
}

async function callOllama (model, prompt) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 25_000);
  try {
    const response = await fetch('http://127.0.0.1:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, prompt, stream: false }),
      signal: controller.signal
    });
    if (!response.ok) {
      throw new Error(`Ollama returned ${response.status}`);
    }
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.warn('[AI] Ollama request failed, falling back to rule-based output:', error.message);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

function fallbackCompletion (type, payload) {
  switch (type) {
    case 'seo':
      return {
        title: `${payload.name} | ${payload.category || 'ResellerOS Listing'}`,
        description: `High-quality ${payload.condition || 'pre-owned'} ${payload.name} sourced from ${payload.source || 'trusted suppliers'}. Includes ${payload.tags?.join(', ') || 'popular keywords'}.` ,
        tags: payload.tags || [payload.category, payload.condition, payload.source].filter(Boolean)
      };
    case 'pricing':
      return {
        suggestedPrice: Math.max(Number(payload.cost || 0) * 2.5, 5).toFixed(2),
        strategy: 'Suggested price is based on 2.5x cost heuristic when AI is unavailable.'
      };
    case 'marketing':
      return {
        post: `New drop: ${payload.name}! Available now for $${payload.price}. ${payload.tags?.map((tag) => `#${tag.replace(/\s+/g, '')}`).join(' ') || '#resellerlife'} #ResellerOS`
      };
    default:
      return { message: 'AI service offline. Using heuristic suggestions.' };
  }
}

export const aiService = {
  async generateListingSEO (payload) {
    const promptTemplate = loadPrompt('seo');
    const prompt = `${promptTemplate}\n\nItem Data:\n${JSON.stringify(payload, null, 2)}`;
    const completion = await callOllama('mistral', prompt);
    if (!completion) return fallbackCompletion('seo', payload);
    return { raw: completion };
  },
  async generatePricingInsight (payload) {
    const promptTemplate = loadPrompt('pricing');
    const prompt = `${promptTemplate}\n\nItem Data:\n${JSON.stringify(payload, null, 2)}`;
    const completion = await callOllama('mistral', prompt);
    if (!completion) return fallbackCompletion('pricing', payload);
    return { raw: completion };
  },
  async generateMarketingCopy (payload) {
    const promptTemplate = loadPrompt('marketing');
    const prompt = `${promptTemplate}\n\nContext:\n${JSON.stringify(payload, null, 2)}`;
    const completion = await callOllama('mistral', prompt);
    if (!completion) return fallbackCompletion('marketing', payload);
    return { raw: completion };
  }
};
