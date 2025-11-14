"""
AI-powered SEO agent for title and description optimization.
"""
import logging
import re
from typing import Dict, Any, List
import asyncio

from src.ai.ollama_client import OllamaClient
from src.ai.fallback_provider import FallbackProvider
from src.core.exceptions import OllamaError

logger = logging.getLogger(__name__)


class SEOAgent:
    """AI-powered SEO optimization agent."""

    def __init__(self):
        """Initialize SEO agent."""
        self.ollama = OllamaClient()
        self.fallback = FallbackProvider()

    async def optimize_title(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize item title for SEO.

        Args:
            item_data: Item information dictionary

        Returns:
            Dictionary with optimized title and SEO metrics
        """
        # Try Ollama first if available
        if await self.ollama.is_available():
            try:
                logger.info("Using Ollama for title optimization")
                return await self._optimize_title_with_ai(item_data)
            except OllamaError as e:
                logger.warning(f"Ollama title optimization failed, using fallback: {e}")
        else:
            logger.info("Ollama not available, using fallback title optimization")

        # Use fallback provider
        return self.fallback.suggest_title(item_data)

    async def _optimize_title_with_ai(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize title using AI.

        Args:
            item_data: Item information

        Returns:
            Title optimization results

        Raises:
            OllamaError: If AI generation fails
        """
        prompt = self._build_title_prompt(item_data)

        try:
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=300,
            )

            if not response:
                raise OllamaError("Empty response from Ollama")

            return self._parse_title_response(response, item_data)
        except Exception as e:
            logger.error(f"AI title optimization failed: {e}")
            raise OllamaError(f"Title optimization failed: {str(e)}")

    def _build_title_prompt(self, item_data: Dict[str, Any]) -> str:
        """Build prompt for title optimization.

        Args:
            item_data: Item information

        Returns:
            Formatted prompt string
        """
        title = item_data.get("title", "")
        category = item_data.get("category", "")
        condition = item_data.get("condition", "")
        description = item_data.get("description", "")

        prompt = f"""You are an eBay SEO expert. Optimize this listing title for maximum visibility and sales.

Current Title: {title}
Category: {category}
Condition: {condition}
{f"Description: {description[:200]}" if description else ""}

eBay Title Requirements:
- Maximum 80 characters
- Include relevant keywords for searchability
- Front-load important terms
- Include condition if notable
- Include brand/model if applicable
- Avoid special characters and excessive punctuation
- No promotional language (FREE, L@@K, etc.)

Provide an optimized title that:
1. Uses all available characters effectively (aim for 60-80 chars)
2. Includes primary keywords early
3. Specifies condition, brand, model, size, or color if relevant
4. Is grammatically correct and natural-reading
5. Maximizes search visibility

Respond in this EXACT format:

TITLE: [Your optimized title here]
SEO_SCORE: [Number from 0-100]
IMPROVEMENTS: [Bullet list of what you changed]

Your response:"""

        return prompt

    def _parse_title_response(
        self, response: str, item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse AI title optimization response.

        Args:
            response: AI response text
            item_data: Original item data

        Returns:
            Parsed title optimization dictionary
        """
        try:
            # Extract title
            title_match = re.search(r'TITLE:\s*(.+?)(?=SEO_SCORE:|$)', response, re.DOTALL | re.IGNORECASE)
            if title_match:
                suggested_title = title_match.group(1).strip()
                # Ensure within 80 character limit
                if len(suggested_title) > 80:
                    suggested_title = suggested_title[:77] + "..."
            else:
                logger.warning("Could not parse title from AI response")
                return self.fallback.suggest_title(item_data)

            # Extract SEO score
            score_match = re.search(r'SEO_SCORE:\s*(\d+)', response, re.IGNORECASE)
            seo_score = float(score_match.group(1)) if score_match else 70.0

            # Extract improvements
            improvements_match = re.search(
                r'IMPROVEMENTS:\s*(.+?)$',
                response,
                re.DOTALL | re.IGNORECASE
            )
            if improvements_match:
                improvements_text = improvements_match.group(1).strip()
                # Parse bullet points
                improvements = [
                    line.strip().lstrip('-•*').strip()
                    for line in improvements_text.split('\n')
                    if line.strip() and not line.strip().startswith('Your response')
                ]
            else:
                improvements = ["AI-optimized for SEO"]

            return {
                "suggested_title": suggested_title,
                "seo_score": min(seo_score, 100.0),
                "reasoning": "AI-optimized title for maximum eBay visibility",
                "improvements": improvements,
            }

        except Exception as e:
            logger.error(f"Failed to parse title response: {e}")
            logger.debug(f"Response was: {response}")
            return self.fallback.suggest_title(item_data)

    async def generate_description(self, item_data: Dict[str, Any]) -> str:
        """Generate SEO-optimized product description.

        Args:
            item_data: Item information

        Returns:
            Generated description
        """
        # Try Ollama first
        if await self.ollama.is_available():
            try:
                prompt = self._build_description_prompt(item_data)
                response = await self.ollama.generate(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=800,
                )
                if response:
                    return response.strip()
            except OllamaError as e:
                logger.warning(f"AI description generation failed: {e}")

        # Use fallback
        return self.fallback.suggest_description(item_data)

    def _build_description_prompt(self, item_data: Dict[str, Any]) -> str:
        """Build prompt for description generation.

        Args:
            item_data: Item information

        Returns:
            Formatted prompt string
        """
        title = item_data.get("title", "")
        category = item_data.get("category", "")
        condition = item_data.get("condition", "")
        notes = item_data.get("notes", "")

        prompt = f"""Write a compelling eBay product description for this item.

Item: {title}
Category: {category}
Condition: {condition}
{f"Additional Info: {notes}" if notes else ""}

Description Requirements:
- Professional and engaging tone
- Highlight key features and benefits
- Mention condition clearly
- Include relevant keywords naturally
- Add shipping and return information
- Keep it concise but complete
- Use proper formatting with paragraphs

Write a description (200-400 words):"""

        return prompt

    def calculate_seo_score(self, title: str, category: str = None) -> Dict[str, Any]:
        """Calculate SEO score for a title.

        Args:
            title: Title to analyze
            category: Optional category for context

        Returns:
            Dictionary with SEO metrics
        """
        score = 0.0
        feedback = []

        # Length check (60-80 chars is ideal)
        length = len(title)
        if 60 <= length <= 80:
            score += 25
            feedback.append("✓ Optimal length (60-80 characters)")
        elif 50 <= length < 60:
            score += 20
            feedback.append("⚠ Could use a few more characters")
        elif 80 < length <= 85:
            score += 20
            feedback.append("⚠ Slightly over ideal length")
        else:
            score += 10
            feedback.append("✗ Length not optimal (aim for 60-80 chars)")

        # Word count (8-12 words is good for eBay)
        word_count = len(title.split())
        if 8 <= word_count <= 12:
            score += 20
            feedback.append("✓ Good keyword density")
        else:
            score += 10
            feedback.append("⚠ Consider adjusting word count (8-12 optimal)")

        # Has numbers (good for specificity - size, model, year)
        if re.search(r'\d', title):
            score += 15
            feedback.append("✓ Includes specific numbers/identifiers")
        else:
            score += 5
            feedback.append("⚠ Consider adding size, year, or model number")

        # Proper capitalization
        if title and title[0].isupper():
            score += 10
            feedback.append("✓ Properly capitalized")
        else:
            feedback.append("✗ Should start with capital letter")

        # No excessive punctuation
        punct_count = len(re.findall(r'[!?,;:]', title))
        if punct_count <= 2:
            score += 10
            feedback.append("✓ Clean punctuation")
        else:
            feedback.append("✗ Too much punctuation")

        # No all caps (except acronyms)
        all_caps_words = [w for w in title.split() if len(w) > 2 and w.isupper()]
        if not all_caps_words:
            score += 10
            feedback.append("✓ No excessive caps")
        else:
            feedback.append("✗ Avoid all-caps words")

        # Keywords early in title
        important_words = ['new', 'vintage', 'rare', 'authentic', 'original']
        first_three_words = ' '.join(title.split()[:3]).lower()
        if any(word in first_three_words for word in important_words):
            score += 10
            feedback.append("✓ Important keywords front-loaded")
        else:
            score += 5

        return {
            "score": min(score, 100.0),
            "grade": self._get_grade(score),
            "feedback": feedback,
        }

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade.

        Args:
            score: SEO score (0-100)

        Returns:
            Letter grade
        """
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
