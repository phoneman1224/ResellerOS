"""
AI-powered pricing agent with intelligent suggestions.
"""
import logging
import re
from typing import Dict, Any, Optional
import asyncio

from src.ai.ollama_client import OllamaClient
from src.ai.fallback_provider import FallbackProvider
from src.core.exceptions import OllamaError

logger = logging.getLogger(__name__)


class PricingAgent:
    """AI-powered pricing suggestion agent."""

    def __init__(self):
        """Initialize pricing agent."""
        self.ollama = OllamaClient()
        self.fallback = FallbackProvider()

    async def suggest_price(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest optimal pricing for an item.

        Args:
            item_data: Item information dictionary with keys:
                - title: Item title
                - category: Item category
                - cost: Item cost
                - condition: Item condition
                - market_data: Optional market research data

        Returns:
            Dictionary with keys:
                - price: Suggested price
                - reasoning: Explanation for the price
                - confidence: Confidence level (high/medium/low)
        """
        # Try Ollama first if available
        if await self.ollama.is_available():
            try:
                logger.info("Using Ollama for pricing suggestion")
                return await self._suggest_price_with_ai(item_data)
            except OllamaError as e:
                logger.warning(f"Ollama pricing failed, using fallback: {e}")
        else:
            logger.info("Ollama not available, using fallback pricing")

        # Use fallback provider
        return self.fallback.suggest_price(item_data)

    async def _suggest_price_with_ai(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pricing suggestion using AI.

        Args:
            item_data: Item information

        Returns:
            Pricing suggestion dictionary

        Raises:
            OllamaError: If AI generation fails
        """
        prompt = self._build_pricing_prompt(item_data)

        try:
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent pricing
                max_tokens=500,
            )

            if not response:
                raise OllamaError("Empty response from Ollama")

            return self._parse_pricing_response(response, item_data)
        except Exception as e:
            logger.error(f"AI pricing generation failed: {e}")
            raise OllamaError(f"Pricing generation failed: {str(e)}")

    def _build_pricing_prompt(self, item_data: Dict[str, Any]) -> str:
        """Build prompt for pricing AI.

        Args:
            item_data: Item information

        Returns:
            Formatted prompt string
        """
        title = item_data.get("title", "")
        category = item_data.get("category", "")
        cost = item_data.get("cost", 0)
        condition = item_data.get("condition", "Good")
        market_data = item_data.get("market_data", {})

        avg_price = market_data.get("average_price", 0)
        price_range = market_data.get("price_range", {})
        min_price = price_range.get("min", 0)
        max_price = price_range.get("max", 0)

        prompt = f"""You are an expert eBay pricing consultant helping resellers maximize profit while remaining competitive.

Item Details:
- Title: {title}
- Category: {category}
- Condition: {condition}
- Cost: ${cost:.2f}

"""

        if market_data and avg_price > 0:
            prompt += f"""Market Research:
- Average sold price: ${avg_price:.2f}
- Price range: ${min_price:.2f} - ${max_price:.2f}

"""

        prompt += """Pricing Guidelines:
1. Ensure minimum 30% profit margin after eBay fees (~13%)
2. Leave room for offers (10-15% below asking price)
3. Consider market competition and demand
4. Account for item condition
5. Factor in shipping costs if applicable

Provide your pricing recommendation in this EXACT format:

PRICE: $XX.XX
REASONING: [2-3 sentences explaining your pricing logic]
CONFIDENCE: [high/medium/low]

Your response:"""

        return prompt

    def _parse_pricing_response(
        self, response: str, item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse AI pricing response.

        Args:
            response: AI response text
            item_data: Original item data for validation

        Returns:
            Parsed pricing dictionary
        """
        try:
            # Extract price
            price_match = re.search(r'PRICE:\s*\$?(\d+\.?\d*)', response, re.IGNORECASE)
            if price_match:
                price = float(price_match.group(1))
            else:
                logger.warning("Could not parse price from AI response")
                return self.fallback.suggest_price(item_data)

            # Extract reasoning
            reasoning_match = re.search(
                r'REASONING:\s*(.+?)(?=CONFIDENCE:|$)',
                response,
                re.DOTALL | re.IGNORECASE
            )
            reasoning = (
                reasoning_match.group(1).strip()
                if reasoning_match
                else "AI-generated pricing suggestion"
            )

            # Extract confidence
            confidence_match = re.search(
                r'CONFIDENCE:\s*(high|medium|low)',
                response,
                re.IGNORECASE
            )
            confidence = (
                confidence_match.group(1).lower()
                if confidence_match
                else "medium"
            )

            # Validate price
            cost = item_data.get("cost", 0)

            # Ensure minimum profit margin
            min_acceptable_price = cost * 2.0  # Minimum 100% markup
            if price < min_acceptable_price:
                logger.warning(
                    f"AI price ${price:.2f} below minimum, adjusting to ${min_acceptable_price:.2f}"
                )
                price = min_acceptable_price
                reasoning += f" (Adjusted to meet minimum profit margin requirement)"

            # Cap maximum reasonable price (10x cost)
            max_acceptable_price = cost * 10.0
            if price > max_acceptable_price:
                logger.warning(
                    f"AI price ${price:.2f} seems too high, capping at ${max_acceptable_price:.2f}"
                )
                price = max_acceptable_price
                reasoning += f" (Capped to reasonable maximum)"

            return {
                "price": round(price, 2),
                "reasoning": reasoning.strip(),
                "confidence": confidence,
            }

        except Exception as e:
            logger.error(f"Failed to parse pricing response: {e}")
            logger.debug(f"Response was: {response}")
            return self.fallback.suggest_price(item_data)

    def calculate_profit_metrics(
        self, cost: float, price: float, ebay_fee_rate: float = 0.13
    ) -> Dict[str, float]:
        """Calculate profit metrics for a given cost and price.

        Args:
            cost: Item cost
            price: Selling price
            ebay_fee_rate: eBay fee percentage (default 13%)

        Returns:
            Dictionary with profit metrics
        """
        ebay_fees = price * ebay_fee_rate
        gross_profit = price - cost
        net_profit = gross_profit - ebay_fees
        profit_margin = (net_profit / price * 100) if price > 0 else 0
        roi = (net_profit / cost * 100) if cost > 0 else 0

        return {
            "price": round(price, 2),
            "cost": round(cost, 2),
            "ebay_fees": round(ebay_fees, 2),
            "gross_profit": round(gross_profit, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin": round(profit_margin, 2),
            "roi": round(roi, 2),
        }
