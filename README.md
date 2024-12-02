# Pulse

An intelligent multi-agent system for e-commerce inventory management and pricing optimization using the Pydantic-AI framework.

## Features

### Implemented
- Multi-agent architecture for coordinated decision making
- Demand forecasting with market signal analysis
- Dynamic price optimization with competitor analysis
- Automated purchase order generation
- Real-time validation and constraint checking
- UTC-aware datetime handling
- Mock database for testing and development

### Core Components
- `DemandForecast`: Predicts future demand with confidence levels
- `PriceOptimization`: Sets optimal prices based on market conditions
- `Purchase`: Generates validated purchase orders
- `MockDB`: Simulates database operations

### Technical Stack
- Python 3.10+
- Pydantic-AI for LLM agent orchestration
- OpenAI GPT-4 for decision making
- Pydantic for data validation
- PyTZ for timezone handling

## Future Enhancements
- Supplier performance tracking
- Inventory optimization algorithms
- Risk assessment and mitigation
- Historical data analysis
- Real-time market monitoring
- Budget optimization

## Why Pulse AI?

Traditional inventory management systems often struggle with:
- Manual decision making
- Delayed responses to market changes
- Suboptimal pricing strategies
- Inventory imbalances

Pulse AI addresses these challenges through:
- Automated decision making
- Real-time market adaptation
- Coordinated pricing and inventory strategies
- Predictive analytics

## Installation
```bash
pip install pydantic-ai pandas pytz
export OPENAI_API_KEY='your-key'
python ecommerce_system.py
```

## License
MIT