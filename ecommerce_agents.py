from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from pydantic_ai import Agent, RunContext
import pytz
import json


# Enums for market signals and pricing strategies
class MarketSignal(str, Enum):
    HIGH_DEMAND = "high_demand"
    LOW_DEMAND = "low_demand"
    SEASONAL = "seasonal"
    TRENDING = "trending"


class PricingStrategy(str, Enum):
    COST_PLUS = "cost_plus"
    MARKET_BASED = "market_based"
    DYNAMIC = "dynamic"


# Model for demand forecasting
class DemandForecast(BaseModel):
    product_id: int
    predicted_demand: float = Field(gt=0)
    confidence: float = Field(ge=0, le=1)
    market_signals: List[MarketSignal]
    suggested_stock_level: int = Field(gt=0)
    price_recommendation: float = Field(gt=0)

    @validator('suggested_stock_level', pre=True, always=True)
    def set_suggested_stock_level(cls, v, values):
        if 'predicted_demand' in values and v < values['predicted_demand']:
            return int(values['predicted_demand'] * 1.2)
        return v


# Model for price optimization
class PriceOptimization(BaseModel):
    product_id: int
    base_cost: float = Field(gt=0)
    suggested_price: float = Field(gt=0)
    min_price: float
    max_price: float
    strategy: PricingStrategy
    margin: float = Field(ge=0)

    @validator('suggested_price')
    def check_price_within_range(cls, v, values):
        if 'min_price' in values and 'max_price' in values:
            if not (values['min_price'] <= v <= values['max_price']):
                raise ValueError("Suggested price is outside the allowed range")
        if 'base_cost' in values and v <= values['base_cost']:
            raise ValueError("Suggested price is below the base cost")
        return v


# Model for purchase orders
class Purchase(BaseModel):
    product_id: int
    supplier_id: str
    quantity: int = Field(gt=0)
    unit_cost: float = Field(gt=0)
    total_cost: float = Field(gt=0)
    expected_delivery: datetime
    priority: int = Field(ge=1, le=5)

    @validator('total_cost', pre=True, always=True)
    def calculate_total_cost(cls, v, values):
        if 'quantity' in values and 'unit_cost' in values:
            return values['quantity'] * values['unit_cost']
        return v

    @validator('expected_delivery')
    def check_future_delivery_date(cls, v):
        if v <= datetime.now(pytz.UTC):
            raise ValueError("Expected delivery date must be in the future")
        return v


# Mock database class
class MockDB:
    def __init__(self):
        self.products = {
            1: {
                "base_cost": 100,
                "min_price": 110,
                "max_price": 130,
                "supplier": "SUP1",
                "market_data": {
                    "competitor_prices": {"Comp1": 120, "Comp2": 130},
                    "market_share": {"Comp1": 0.4, "Comp2": 0.3, "Us": 0.3},
                    "total_market_size": 10000,
                    "growth_rate": 0.05,
                    "seasonality_factor": 1.0
                }
            }
        }
        self.stock = {1: 100}

    async def get_data(self, product_id: int) -> Dict:
        return self.products.get(product_id, {})

    async def get_stock(self, product_id: int) -> int:
        return self.stock.get(product_id, 0)


# Dependency class
@dataclass
class Deps:
    db: MockDB
    product_id: int
    current_date: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))


# Agents for forecasting, pricing, and purchasing
forecasting_agent = Agent(
    'openai:gpt-4',
    deps_type=Deps,
    result_type=DemandForecast,
    system_prompt="""Analyze data for accurate demand forecasting. 
    Ensure suggested stock > predicted demand. Keep confidence between 0-1."""
)

pricing_agent = Agent(
    'openai:gpt-4',
    deps_type=Deps,
    result_type=PriceOptimization,
    system_prompt="""Set optimal prices within min-max range. 
    Ensure price > cost and calculate proper margins."""
)

purchasing_agent = Agent(
    'openai:gpt-4',
    deps_type=Deps,
    result_type=Purchase,
    system_prompt="""Generate valid purchase orders with:
    - Matching product IDs
    - Future delivery dates
    - Correct cost calculations
    - Quantities matching forecasts"""
)


# Tools to fetch market and product information
@forecasting_agent.tool
async def get_market_info(ctx: RunContext[Deps]) -> str:
    data = await ctx.deps.db.get_data(ctx.deps.product_id)
    stock = await ctx.deps.db.get_stock(ctx.deps.product_id)
    return json.dumps({"market_data": data.get("market_data", {}), "stock": stock})


@pricing_agent.tool
@purchasing_agent.tool
async def get_product_info(ctx: RunContext[Deps]) -> str:
    data = await ctx.deps.db.get_data(ctx.deps.product_id)
    return json.dumps(data)


# Main optimization process
async def optimize(product_id: int):
    db = MockDB()
    deps = Deps(db=db, product_id=product_id)
    future_delivery = datetime.now(pytz.UTC) + timedelta(days=14)

    try:
        forecast = await forecasting_agent.run(
            f"Generate forecast for product {product_id}",
            deps=deps
        )

        pricing = await pricing_agent.run(
            f"Optimize pricing for product {product_id} with suggested price {forecast.data.price_recommendation}",
            deps=deps
        )

        purchase = await purchasing_agent.run(
            f"Generate purchase order for product {product_id} with delivery after {future_delivery.isoformat()}",
            deps=deps
        )

        if not (forecast.data.product_id == pricing.data.product_id == purchase.data.product_id == product_id):
            raise ValueError("Product ID mismatch")

        return forecast, pricing, purchase
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None, None
