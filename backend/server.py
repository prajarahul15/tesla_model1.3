from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import sys

# Add the backend directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from models.financial_models import *
from services.financial_calculator import TeslaFinancialCalculator
from services.analytics_engine import AnalyticsEngine
from data.tesla_data import generate_all_tesla_assumptions, TESLA_BASE_YEAR_DATA, MACRO_ASSUMPTIONS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
try:
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    print(f"Connected to MongoDB: {os.environ['DB_NAME']}")
except KeyError as e:
    print(f"Missing environment variable: {e}")
    # Fallback for development
    client = None
    db = None

# Create the main app without a prefix
app = FastAPI(title="Tesla Financial Model & Analytics API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize calculators
tesla_calculator = TeslaFinancialCalculator()
analytics_engine = AnalyticsEngine()

# Initialize analytics engine on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Tesla Financial Model & Analytics API started successfully")
    logger.info("Loading analytics data...")
    
    # Load analytics data
    if analytics_engine.load_data():
        logger.info("Analytics data loaded successfully")
    else:
        logger.error("Failed to load analytics data")

# Professional Dashboard API Endpoints

@api_router.get("/analytics/overview")
async def get_data_overview():
    """Get comprehensive data overview metrics"""
    try:
        metrics = analytics_engine.get_data_overview_metrics()
        if metrics is None:
            raise HTTPException(status_code=500, detail="Failed to calculate overview metrics")
        
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating overview: {str(e)}")

@api_router.get("/analytics/economic-variables")
async def get_economic_variables():
    """Get economic variables data for analysis"""
    try:
        econ_data = analytics_engine.get_economic_variables_data()
        if econ_data is None:
            raise HTTPException(status_code=500, detail="Economic variables data not available")
        
        return {
            "success": True,
            "data": econ_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting economic data: {str(e)}")

@api_router.get("/analytics/lineups")
async def get_available_lineups():
    """Get list of available lineups for forecasting"""
    try:
        if analytics_engine.sample_data is None:
            if not analytics_engine.load_data():
                raise HTTPException(status_code=500, detail="Failed to load data")
        
        lineups = analytics_engine.sample_data['Lineup'].unique().tolist()
        
        # Get metadata for each lineup
        lineup_metadata = []
        for lineup in lineups:
            lineup_data = analytics_engine.sample_data[analytics_engine.sample_data['Lineup'] == lineup]
            lineup_metadata.append({
                'lineup': lineup,
                'profile': lineup_data['Profile'].iloc[0],
                'line_item': lineup_data['Line_Item'].iloc[0],
                'records': int(len(lineup_data)),
                'date_range': {
                    'start': lineup_data['DATE'].min().strftime('%Y-%m-%d'),
                    'end': lineup_data['DATE'].max().strftime('%Y-%m-%d')
                },
                'total_actual': int(lineup_data['Actual'].sum()),
                'total_plan': int(lineup_data['Plan'].sum())
            })
        
        return {
            "success": True,
            "lineups": lineup_metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting lineups: {str(e)}")

class ForecastRequest(BaseModel):
    lineup: str
    forecast_type: str  # 'univariate' or 'multivariate'
    months_ahead: int = 12

@api_router.post("/analytics/forecast")
async def generate_forecast(request: ForecastRequest):
    """Generate forecast for specified lineup and type"""
    try:
        if request.forecast_type not in ['univariate', 'multivariate']:
            raise HTTPException(status_code=400, detail="Forecast type must be 'univariate' or 'multivariate'")
        
        if request.months_ahead < 1 or request.months_ahead > 24:
            raise HTTPException(status_code=400, detail="Months ahead must be between 1 and 24")
        
        # Ensure data is loaded
        if analytics_engine.sample_data is None:
            if not analytics_engine.load_data():
                raise HTTPException(status_code=500, detail="Failed to load data")
        
        # Check if lineup exists
        available_lineups = analytics_engine.sample_data['Lineup'].unique()
        if request.lineup not in available_lineups:
            raise HTTPException(status_code=400, detail=f"Lineup {request.lineup} not found. Available: {list(available_lineups)}")
        
        # Generate forecast
        forecast_result = analytics_engine.generate_forecast(
            request.lineup, 
            request.forecast_type, 
            request.months_ahead
        )
        
        if forecast_result is None:
            raise HTTPException(status_code=500, detail="Failed to generate forecast")
        
        return {
            "success": True,
            "forecast": forecast_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

class CompareRequest(BaseModel):
    lineup: str
    months_ahead: int = 12

@api_router.post("/analytics/compare-forecasts")
async def compare_forecasts(request: CompareRequest):
    """Compare univariate vs multivariate forecasting methods"""
    try:
        # Ensure data is loaded
        if analytics_engine.sample_data is None:
            if not analytics_engine.load_data():
                raise HTTPException(status_code=500, detail="Failed to load data")
        
        # Check if lineup exists
        available_lineups = analytics_engine.sample_data['Lineup'].unique()
        if request.lineup not in available_lineups:
            raise HTTPException(status_code=400, detail=f"Lineup {request.lineup} not found")
        
        # Generate comparison
        comparison_result = analytics_engine.compare_forecast_methods(
            request.lineup, 
            request.months_ahead
        )
        
        if comparison_result is None:
            raise HTTPException(status_code=500, detail="Failed to generate forecast comparison")
        
        return {
            "success": True,
            "comparison": comparison_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing forecasts: {str(e)}")

# Tesla Financial Model Endpoints (existing)

@api_router.get("/tesla/overview")
async def get_tesla_overview():
    """Get Tesla overview data and market assumptions"""
    return {
        "tesla_base_data": TESLA_BASE_YEAR_DATA,
        "macro_assumptions": MACRO_ASSUMPTIONS,
        "model_description": "Tesla 5-Year Financial Model (2025-2029) with DCF Valuation",
        "scenarios": ["best", "base", "worst"],
        "forecast_years": [2025, 2026, 2027, 2028, 2029]
    }

@api_router.get("/tesla/assumptions/{scenario}")
async def get_scenario_assumptions(scenario: str):
    """Get all assumptions for a specific scenario"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        assumptions = []
        
        for year in [2025, 2026, 2027, 2028, 2029]:
            from data.tesla_data import get_tesla_assumptions
            assumption_dict = get_tesla_assumptions(scenario_enum, year)
            assumptions.append(assumption_dict)
        
        return {
            "scenario": scenario,
            "assumptions": assumptions
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario. Use 'best', 'base', or 'worst'")

@api_router.post("/tesla/model/{scenario}")
async def generate_financial_model(scenario: str):
    """Generate complete financial model for scenario"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        model = tesla_calculator.build_complete_financial_model(scenario_enum)
        
        # Store in database if available
        if db is not None:
            try:
                await db.financial_models.insert_one(model.dict())
            except Exception as e:
                print(f"Database insert error: {e}")
        
        return {
            "success": True,
            "message": f"Financial model generated for {scenario} scenario",
            "model": model.dict()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario. Use 'best', 'base', or 'worst'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating model: {str(e)}")

@api_router.get("/tesla/model/{scenario}/income-statement")
async def get_income_statements(scenario: str):
    """Get income statements for all years in scenario"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        model = tesla_calculator.build_complete_financial_model(scenario_enum)
        
        income_statements = [stmt.dict() for stmt in model.income_statements]
        
        return {
            "scenario": scenario,
            "income_statements": income_statements
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tesla/model/{scenario}/balance-sheet")
async def get_balance_sheets(scenario: str):
    """Get balance sheets for all years in scenario"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        model = tesla_calculator.build_complete_financial_model(scenario_enum)
        
        balance_sheets = [bs.dict() for bs in model.balance_sheets]
        
        return {
            "scenario": scenario,
            "balance_sheets": balance_sheets
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tesla/model/{scenario}/cash-flow")
async def get_cash_flows(scenario: str):
    """Get cash flow statements for all years in scenario"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        model = tesla_calculator.build_complete_financial_model(scenario_enum)
        
        cash_flows = [cf.dict() for cf in model.cash_flow_statements]
        
        return {
            "scenario": scenario,
            "cash_flow_statements": cash_flows
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tesla/model/{scenario}/dcf-valuation")
async def get_dcf_valuation(scenario: str):
    """Get DCF valuation for scenario"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        model = tesla_calculator.build_complete_financial_model(scenario_enum)
        
        return {
            "scenario": scenario,
            "dcf_valuation": model.dcf_valuation.dict()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tesla/comparison")
async def get_scenario_comparison():
    """Compare all three scenarios side by side"""
    try:
        models = {}
        for scenario in ["best", "base", "worst"]:
            scenario_enum = ScenarioType(scenario)
            model = tesla_calculator.build_complete_financial_model(scenario_enum)
            models[scenario] = model.dict()
        
        # Create comparison summary
        comparison = {
            "revenue_comparison": {},
            "valuation_comparison": {},
            "margin_comparison": {}
        }
        
        for scenario, model in models.items():
            # 2029 projections
            final_income = model["income_statements"][-1]
            dcf = model["dcf_valuation"]
            
            comparison["revenue_comparison"][scenario] = {
                "2029_revenue": final_income["total_revenue"],
                "5yr_cagr": ((final_income["total_revenue"] / TESLA_BASE_YEAR_DATA["total_revenue"]) ** (1/5)) - 1
            }
            
            comparison["valuation_comparison"][scenario] = {
                "price_per_share": dcf["price_per_share"],
                "enterprise_value": dcf["enterprise_value"],
                "wacc": dcf["wacc"]
            }
            
            comparison["margin_comparison"][scenario] = {
                "2029_gross_margin": final_income["gross_margin"],
                "2029_operating_margin": final_income["operating_margin"],
                "2029_net_margin": final_income["net_margin"]
            }
        
        return {
            "success": True,
            "models": models,
            "comparison_summary": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/tesla/update-assumption")
async def update_assumption(update: ModelInput):
    """Update a specific assumption and recalculate model"""
    try:
        # This would be more complex in a real system with persistent storage
        # For now, we'll return the instruction on how this would work
        return {
            "success": True,
            "message": f"Would update {update.field_name} to {update.field_value} for {update.scenario} {update.year}",
            "note": "Real-time updates would require storing model state and recalculating affected statements"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tesla/sensitivity/{scenario}")
async def get_sensitivity_analysis(scenario: str):
    """Get detailed sensitivity analysis for DCF valuation"""
    try:
        scenario_enum = ScenarioType(scenario.lower())
        model = tesla_calculator.build_complete_financial_model(scenario_enum)
        
        dcf = model.dcf_valuation
        
        return {
            "scenario": scenario,
            "base_valuation": dcf.price_per_share,
            "sensitivity_analysis": {
                "growth_rates": dcf.sensitivity_growth_rates,
                "wacc_rates": dcf.sensitivity_wacc_rates,
                "price_matrix": dcf.sensitivity_matrix
            },
            "key_assumptions": {
                "terminal_growth_rate": dcf.terminal_growth_rate,
                "wacc": dcf.wacc,
                "final_year_fcf": dcf.projected_free_cash_flows[-1]
            }
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Original status check endpoints (keeping for compatibility)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

@api_router.get("/")
async def root():
    return {"message": "Tesla Financial Model & Analytics API - Ready for Analysis"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    if db is not None:
        try:
            await db.status_checks.insert_one(status_obj.dict())
        except Exception as e:
            print(f"Database insert error: {e}")
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if db is not None:
        try:
            status_checks = await db.status_checks.find().to_list(1000)
            return [StatusCheck(**status_check) for status_check in status_checks]
        except Exception as e:
            print(f"Database query error: {e}")
    return []

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()