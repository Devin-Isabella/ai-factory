import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

# Config via env or defaults
INFRA_PER_1K_DEFAULT = float(os.getenv("PRICE_INFRA_PER_1K", "0.15"))   # dollars / 1k tokens (example)
MIN_BLOCK_DEFAULT    = int(os.getenv("MIN_BLOCK", "5000"))              # interactions
MARGIN               = 0.15

class QuoteInput(BaseModel):
    # rough knobs collected by the bot
    model: str = "gpt-4o-mini"
    est_tokens_per_interaction: int = 500     # guess; can be adjusted per product
    min_block: int = MIN_BLOCK_DEFAULT        # minimum interactions to prepay
    infra_per_1k: float = INFRA_PER_1K_DEFAULT

class QuoteResult(BaseModel):
    model: str
    interactions: int
    est_tokens_total: int
    infra_cost: float
    safety_pool: float
    customer_price: float
    currency: Literal["USD"] = "USD"

@router.post("/billing/quote", response_model=QuoteResult)
async def quote(inp: QuoteInput):
    interactions = max(inp.min_block, 1)
    est_total_tokens = interactions * max(inp.est_tokens_per_interaction, 1)
    infra_cost = (est_total_tokens / 1000.0) * inp.infra_per_1k
    # Pricing formula: customer price = (infra × 2) × (1 + 0.15)
    customer_price = (infra_cost * 2.0) * (1.0 + MARGIN)
    safety_pool = infra_cost  # the extra x1 (of the ×2) we reserve for repair/safety
    return QuoteResult(
        model=inp.model,
        interactions=interactions,
        est_tokens_total=int(est_total_tokens),
        infra_cost=round(infra_cost, 2),
        safety_pool=round(safety_pool, 2),
        customer_price=round(customer_price, 2),
    )

class CheckoutInput(BaseModel):
    amount_usd: float
    note: str | None = None

class CheckoutResult(BaseModel):
    status: str
    payment_url: str
    note: str | None = None

@router.post("/billing/checkout", response_model=CheckoutResult)
async def checkout(inp: CheckoutInput):
    # MOCK: return a fake payment URL. Later swap to Stripe Checkout Session.
    fake_url = f"/ui/paid.html?amount={inp.amount_usd}"
    return CheckoutResult(status="pending", payment_url=fake_url, note=inp.note)
