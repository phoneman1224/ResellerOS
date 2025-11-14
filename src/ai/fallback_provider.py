"""
Fallback AI provider using rule-based logic when Ollama is unavailable.
"""
import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


class FallbackProvider:
    """Rule-based fallback provider for AI features."""

    def suggest_price(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based pricing when AI is unavailable.

        Args:
            item_data: Item information dictionary

        Returns:
            Dictionary with price suggestion
        """
        cost = item_data.get("cost", 0)
        category = item_data.get("category", "").lower()
        condition = item_data.get("condition", "").lower()

        # Base multipliers by category
        category_multipliers = {
            "clothing": 3.0,
            "electronics": 2.0,
            "vintage": 4.0,
            "collectibles": 5.0,
            "books": 2.5,
            "toys": 3.5,
            "home": 2.8,
            "garden": 2.8,
            "sports": 3.2,
        }

        # Condition adjustments
        condition_multipliers = {
            "new": 1.2,
            "like new": 1.1,
            "good": 1.0,
            "fair": 0.8,
            "poor": 0.6,
        }

        # Find category multiplier
        base_multiplier = 3.0  # Default
        for cat, mult in category_multipliers.items():
            if cat in category:
                base_multiplier = mult
                break

        # Apply condition multiplier
        condition_mult = condition_multipliers.get(condition, 1.0)

        # Calculate price
        suggested_price = cost * base_multiplier * condition_mult

        # Ensure minimum profit margin (30%)
        min_price = cost * 2.0  # 100% markup minimum
        if suggested_price < min_price:
            suggested_price = min_price

        reasoning = (
            f"Rule-based pricing: {base_multiplier}x markup for {category or 'general'} items, "
            f"adjusted by {condition_mult}x for '{condition}' condition. "
            f"This ensures a minimum 100% markup from cost."
        )

        return {
            "price": round(suggested_price, 2),
            "reasoning": reasoning,
            "confidence": "low",
        }

    def suggest_title(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic title optimization when AI is unavailable.

        Args:
            item_data: Item information dictionary

        Returns:
            Dictionary with title suggestion
        """
        title = item_data.get("title", "")
        category = item_data.get("category", "")
        condition = item_data.get("condition", "")

        # Clean up title
        cleaned = title.strip()

        # Add category if not present
        if category and category.lower() not in cleaned.lower():
            cleaned = f"{cleaned} {category}"

        # Add condition if not present and item has one
        if condition and condition.lower() not in cleaned.lower():
            cleaned = f"{cleaned} {condition}"

        # Capitalize words
        cleaned = cleaned.title()

        # Limit to eBay's 80 character limit
        if len(cleaned) > 80:
            cleaned = cleaned[:77] + "..."

        # Calculate basic SEO score
        seo_score = self._calculate_seo_score(cleaned)

        improvements = []
        if category and category.lower() not in title.lower():
            improvements.append(f"Added category '{category}'")
        if condition and condition.lower() not in title.lower():
            improvements.append(f"Added condition '{condition}'")
        if len(title) != len(cleaned):
            improvements.append("Cleaned and capitalized")

        return {
            "suggested_title": cleaned,
            "seo_score": seo_score,
            "reasoning": "Rule-based title optimization",
            "improvements": improvements,
        }

    def _calculate_seo_score(self, title: str) -> float:
        """Calculate basic SEO score for a title.

        Args:
            title: Title to score

        Returns:
            SEO score (0-100)
        """
        score = 0.0

        # Length check (50-80 chars is ideal)
        length = len(title)
        if 50 <= length <= 80:
            score += 30
        elif 40 <= length < 50 or 80 < length <= 85:
            score += 20
        else:
            score += 10

        # Word count (5-12 words is good)
        word_count = len(title.split())
        if 5 <= word_count <= 12:
            score += 25
        elif 3 <= word_count < 5 or 12 < word_count <= 15:
            score += 15
        else:
            score += 5

        # Has numbers (good for specificity)
        if re.search(r'\d', title):
            score += 15

        # Proper capitalization
        if title[0].isupper():
            score += 10

        # No excessive punctuation
        punct_count = len(re.findall(r'[!?.,;:]', title))
        if punct_count <= 3:
            score += 10
        else:
            score += 5

        # No all caps words (except single letters)
        all_caps_words = [w for w in title.split() if len(w) > 1 and w.isupper()]
        if not all_caps_words:
            score += 10

        return min(score, 100.0)

    def suggest_description(self, item_data: Dict[str, Any]) -> str:
        """Generate basic description template.

        Args:
            item_data: Item information dictionary

        Returns:
            Description text
        """
        title = item_data.get("title", "Item")
        category = item_data.get("category", "")
        condition = item_data.get("condition", "Good")
        notes = item_data.get("notes", "")

        description = f"""
{title}

Condition: {condition}
{f"Category: {category}" if category else ""}

{notes if notes else "Please contact for more details."}

Shipping:
- Fast shipping within 1-2 business days
- Carefully packaged

Returns:
- 30-day return policy
- Item must be in original condition

Thank you for your interest!
"""

        return description.strip()

    def suggest_category(self, item_data: Dict[str, Any]) -> List[str]:
        """Suggest categories based on title keywords.

        Args:
            item_data: Item information dictionary

        Returns:
            List of suggested categories
        """
        title = item_data.get("title", "").lower()
        description = item_data.get("description", "").lower()
        text = f"{title} {description}"

        suggestions = []

        # Keyword-based category detection
        category_keywords = {
            "Clothing": ["shirt", "pants", "dress", "shoes", "jacket", "coat", "sweater", "jeans"],
            "Electronics": ["phone", "computer", "laptop", "tablet", "camera", "headphones", "gaming"],
            "Collectibles": ["vintage", "rare", "antique", "collectible", "limited", "signed"],
            "Books": ["book", "novel", "textbook", "magazine", "comic"],
            "Toys": ["toy", "doll", "action figure", "lego", "playset"],
            "Home & Garden": ["furniture", "decor", "garden", "kitchen", "bedding"],
            "Sports": ["sports", "fitness", "athletic", "exercise", "golf", "baseball"],
        }

        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if category not in suggestions:
                        suggestions.append(category)
                    break

        return suggestions if suggestions else ["Other"]
