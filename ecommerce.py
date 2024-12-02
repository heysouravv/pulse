import asyncio
from ecommerce_agents import optimize

if __name__ == "__main__":
    import asyncio
    
    result = asyncio.run(optimize(1))
    if result and all(result):
        forecast, pricing, purchase = result
        print("\nValidated Results:")
        print(f"Forecast: {forecast.data}")
        print(f"Pricing: {pricing.data}")
        print(f"Purchase: {purchase.data}")
    else:
        print("Optimization failed")