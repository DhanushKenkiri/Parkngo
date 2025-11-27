"""
Pricing Agent
Uses Gemini AI for dynamic pricing based on demand, time, weather, events
"""

import logging
from typing import Dict, Any
from datetime import datetime, time as dt_time
import random

from services import gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PricingAgent:
    """
    Calculates dynamic pricing using Gemini AI for:
    - Demand forecasting
    - Time-based pricing (peak/off-peak)
    - Weather adjustments
    - Special event pricing
    - Feature premiums (covered, EV charging)
    """
    
    def __init__(self):
        self.agent_id = "pricing_agent_001"
        self.agent_name = "Pricing Agent"
        
        # Base prices (in ADA)
        self.base_prices = {
            'regular': 0.5,   # 0.5 ADA per hour
            'premium': 0.75,  # 0.75 ADA per hour
            'disabled': 0.5   # Same as regular
        }
        
        logger.info(f"✅ {self.agent_name} initialized")
    
    def calculate_price(
        self, 
        spot_data: Dict[str, Any], 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate dynamic price for parking spot
        
        Args:
            spot_data: {
                'spot_id': str,
                'type': str (regular/premium),
                'features': List[str],
                'zone': str
            }
            request_data: {
                'duration_hours': float,
                'user_location': {...}
            }
        
        Returns:
            {
                'base_price': float,
                'time_multiplier': float,
                'demand_multiplier': float,
                'feature_premium': float,
                'total_price': float,
                'breakdown': {...},
                'ai_reasoning': str
            }
        """
        
        logger.info(f"💰 Calculating price for spot: {spot_data.get('spot_id')}")
        
        try:
            # Get base price
            spot_type = spot_data.get('type', 'regular')
            base_price = self.base_prices.get(spot_type, 0.5)
            duration = request_data.get('duration_hours', 1.0)
            
            # Use Gemini AI for demand analysis
            demand_analysis = self._analyze_demand_with_ai(spot_data, request_data)
            
            # Calculate time-based multiplier
            time_multiplier = self._calculate_time_multiplier()
            
            # Calculate feature premium
            feature_premium = self._calculate_feature_premium(spot_data['features'])
            
            # Calculate total price
            total_price = (
                base_price * duration * 
                demand_analysis['demand_multiplier'] * 
                time_multiplier
            ) + feature_premium
            
            # Use Gemini AI to explain the pricing
            pricing_explanation = self._explain_pricing_with_ai(
                base_price,
                duration,
                demand_analysis,
                time_multiplier,
                feature_premium,
                total_price
            )
            
            return {
                'base_price': base_price,
                'duration_hours': duration,
                'time_multiplier': time_multiplier,
                'demand_multiplier': demand_analysis['demand_multiplier'],
                'feature_premium': feature_premium,
                'total_price': round(total_price, 2),
                'breakdown': {
                    'base': f"{base_price} ADA/hour",
                    'time_adjustment': f"x{time_multiplier} ({'peak' if time_multiplier > 1 else 'off-peak'})",
                    'demand_adjustment': f"x{demand_analysis['demand_multiplier']} ({demand_analysis['reasoning']})",
                    'features': f"+{feature_premium} ADA ({', '.join(spot_data['features']) if spot_data['features'] else 'none'})"
                },
                'ai_reasoning': pricing_explanation,
                'demand_score': demand_analysis.get('demand_score', 50)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating price: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: simple pricing
            base = self.base_prices.get(spot_data.get('type', 'regular'), 0.5)
            duration = request_data.get('duration_hours', 1.0)
            
            return {
                'base_price': base,
                'duration_hours': duration,
                'total_price': base * duration,
                'ai_reasoning': 'Fallback pricing (AI unavailable)'
            }
    
    def _analyze_demand_with_ai(
        self, 
        spot_data: Dict[str, Any], 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Gemini AI to analyze demand and suggest multiplier"""
        
        logger.info("🧠 Analyzing demand with Gemini AI...")
        
        # Prepare context for Gemini
        current_hour = datetime.now().hour
        current_day = datetime.now().strftime('%A')
        
        context = {
            'current_time': {
                'hour': current_hour,
                'day': current_day,
                'is_weekend': datetime.now().weekday() >= 5
            },
            'spot_info': {
                'zone': spot_data.get('zone'),
                'type': spot_data.get('type'),
                'features': spot_data.get('features', [])
            },
            'duration': request_data.get('duration_hours'),
            'weather': 'sunny',  # In production, integrate weather API
            'special_events': []  # In production, check events calendar
        }
        
        try:
            demand_result = gemini_service.analyze_demand_forecast(context)
            
            logger.info(f"✅ Gemini demand analysis: {demand_result.get('demand_score')}/100")
            
            return demand_result
            
        except Exception as e:
            logger.error(f"❌ Gemini demand analysis failed: {e}")
            
            # Fallback: rule-based demand
            return self._fallback_demand_analysis(current_hour)
    
    def _fallback_demand_analysis(self, hour: int) -> Dict[str, Any]:
        """Fallback demand analysis when Gemini is unavailable"""
        
        # Peak hours: 8-10am, 5-7pm
        if (8 <= hour <= 10) or (17 <= hour <= 19):
            return {
                'demand_score': 80,
                'demand_multiplier': 1.4,
                'reasoning': 'Peak hours (high demand)',
                'peak_expected': True
            }
        # Normal hours
        elif 7 <= hour <= 21:
            return {
                'demand_score': 50,
                'demand_multiplier': 1.0,
                'reasoning': 'Normal demand',
                'peak_expected': False
            }
        # Off-peak hours
        else:
            return {
                'demand_score': 20,
                'demand_multiplier': 0.8,
                'reasoning': 'Off-peak hours (low demand)',
                'peak_expected': False
            }
    
    def _calculate_time_multiplier(self) -> float:
        """Calculate time-based pricing multiplier"""
        
        now = datetime.now()
        hour = now.hour
        is_weekend = now.weekday() >= 5
        
        # Peak hours (8-10am, 5-7pm on weekdays)
        if not is_weekend and ((8 <= hour <= 10) or (17 <= hour <= 19)):
            return 1.3
        
        # Weekend premium
        if is_weekend and (10 <= hour <= 20):
            return 1.2
        
        # Night discount
        if hour < 6 or hour > 22:
            return 0.8
        
        # Normal hours
        return 1.0
    
    def _calculate_feature_premium(self, features: List[str]) -> float:
        """Calculate premium for spot features"""
        
        premium = 0.0
        
        feature_prices = {
            'covered': 0.1,
            'ev_charging': 0.2,
            'disabled_access': 0.0,  # No premium for accessibility
            'security_camera': 0.05,
            'well_lit': 0.05
        }
        
        for feature in features:
            premium += feature_prices.get(feature, 0.0)
        
        return premium
    
    def _explain_pricing_with_ai(
        self,
        base_price: float,
        duration: float,
        demand_analysis: Dict[str, Any],
        time_multiplier: float,
        feature_premium: float,
        total_price: float
    ) -> str:
        """Use Gemini AI to explain the pricing breakdown"""
        
        context = f"""
        Explain this parking pricing to the user in one friendly sentence:
        
        Base rate: {base_price} ADA/hour
        Duration: {duration} hours
        Time multiplier: {time_multiplier}x ({'peak' if time_multiplier > 1 else 'off-peak'})
        Demand multiplier: {demand_analysis.get('demand_multiplier')}x ({demand_analysis.get('reasoning')})
        Feature premium: +{feature_premium} ADA
        
        TOTAL: {total_price} ADA
        
        Make it sound reasonable and customer-friendly.
        """
        
        try:
            explanation = gemini_service._generate_with_retry(context)
            
            # Clean up response (remove quotes, extra formatting)
            explanation = explanation.strip().strip('"\'')
            
            logger.info(f"✅ Gemini pricing explanation generated")
            
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Gemini explanation failed: {e}")
            
            # Fallback explanation
            return f"Total: {total_price} ADA for {duration}h parking with current demand conditions"


# Singleton instance
pricing_agent = PricingAgent()
