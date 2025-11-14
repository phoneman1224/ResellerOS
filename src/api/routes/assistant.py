"""
AI Assistant API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
import asyncio

from src.ai.pricing_agent import PricingAgent
from src.ai.seo_agent import SEOAgent

logger = logging.getLogger(__name__)
router = APIRouter()

pricing_agent = PricingAgent()
seo_agent = SEOAgent()


class PricingRequest(BaseModel):
    """Request for pricing suggestion."""
    title: str
    category: str = ""
    cost: float
    condition: str = "Good"
    market_data: Dict[str, Any] = {}


class TitleOptimizationRequest(BaseModel):
    """Request for title optimization."""
    title: str
    category: str = ""
    condition: str = ""
    description: str = ""


class DescriptionRequest(BaseModel):
    """Request for description generation."""
    title: str
    category: str = ""
    condition: str = ""
    notes: str = ""


@router.post("/suggest-price")
async def suggest_price(request: PricingRequest):
    """Get AI pricing suggestion.

    Args:
        request: Pricing request data

    Returns:
        Price suggestion with reasoning
    """
    try:
        item_data = request.model_dump()
        suggestion = await pricing_agent.suggest_price(item_data)

        return {
            "success": True,
            "data": suggestion,
        }
    except Exception as e:
        logger.error(f"Pricing suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate pricing suggestion: {str(e)}")


@router.post("/optimize-title")
async def optimize_title(request: TitleOptimizationRequest):
    """Get AI title optimization.

    Args:
        request: Title optimization request

    Returns:
        Optimized title with SEO score
    """
    try:
        item_data = request.model_dump()
        optimization = await seo_agent.optimize_title(item_data)

        return {
            "success": True,
            "data": optimization,
        }
    except Exception as e:
        logger.error(f"Title optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize title: {str(e)}")


@router.post("/generate-description")
async def generate_description(request: DescriptionRequest):
    """Generate AI description.

    Args:
        request: Description generation request

    Returns:
        Generated description
    """
    try:
        item_data = request.model_dump()
        description = await seo_agent.generate_description(item_data)

        return {
            "success": True,
            "data": {"description": description},
        }
    except Exception as e:
        logger.error(f"Description generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")


@router.post("/calculate-seo-score")
async def calculate_seo_score(title: str, category: str = ""):
    """Calculate SEO score for a title.

    Args:
        title: Title to analyze
        category: Optional category

    Returns:
        SEO score and feedback
    """
    try:
        score_data = seo_agent.calculate_seo_score(title, category)

        return {
            "success": True,
            "data": score_data,
        }
    except Exception as e:
        logger.error(f"SEO score calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate SEO score: {str(e)}")


@router.get("/ollama-status")
async def check_ollama_status():
    """Check if Ollama is available.

    Returns:
        Ollama availability status
    """
    try:
        from src.ai.ollama_client import OllamaClient

        client = OllamaClient()
        is_available = await client.is_available()

        models = []
        if is_available:
            try:
                models = await client.list_models()
            except:
                pass

        return {
            "success": True,
            "data": {
                "available": is_available,
                "models": models,
                "status": "online" if is_available else "offline",
            },
        }
    except Exception as e:
        logger.error(f"Ollama status check failed: {e}")
        return {
            "success": True,
            "data": {
                "available": False,
                "models": [],
                "status": "offline",
                "error": str(e),
            },
        }
