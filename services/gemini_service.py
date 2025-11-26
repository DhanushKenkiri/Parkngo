"""
ParknGo - Gemini AI Service Module
Professional Google Gemini AI integration for intelligent decision-making
"""

import os
import logging
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiService:
    """Professional Google Gemini AI service for parking intelligence"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Gemini AI"""
        if not self._initialized:
            self._initialize_gemini()
            GeminiService._initialized = True
    
    def _initialize_gemini(self):
        """Initialize Gemini API"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            
            if not api_key:
                raise ValueError("Missing GEMINI_API_KEY in .env file")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel(model_name)
            
            # Generation config for consistent, fast responses
            self.generation_config = {
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
            
            logger.info(f"✅ Gemini AI initialized: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            raise
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response with automatic retry on failure
        
        Args:
            prompt: Input prompt for Gemini
            max_retries: Maximum retry attempts
        Returns:
            Generated text response
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                return response.text.strip()
                
            except Exception as e:
                logger.warning(f"Gemini API error (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Gemini API failed after {max_retries} attempts")
                    raise
        
        return ""
    
    # ============================================
    # PRICING INTELLIGENCE
    # ============================================
    
    def analyze_demand_forecast(self, context: Dict) -> Dict[str, Any]:
        """
        Use Gemini AI to forecast parking demand and suggest pricing multiplier
        
        Args:
            context: Dictionary with current_time, day_of_week, historical_data, events
        Returns:
            Dictionary with demand_score (0-100), multiplier (0.8-2.0), reasoning
        """
        try:
            prompt = f"""
You are a parking demand forecasting AI. Analyze the following context and predict parking demand.

Context:
- Current Time: {context.get('current_time', 'N/A')}
- Day of Week: {context.get('day_of_week', 'N/A')}
- Weather: {context.get('weather', 'Clear')}
- Nearby Events: {context.get('events', 'None')}
- Historical Average Occupancy: {context.get('avg_occupancy', 60)}%

Respond in JSON format:
{{
  "demand_score": <0-100>,
  "multiplier": <0.8-2.0>,
  "reasoning": "<brief explanation>",
  "peak_expected": <true/false>
}}

Consider:
- Peak hours (7-9 AM, 5-7 PM) = higher demand
- Weekends near malls = very high demand
- Rain/bad weather = higher demand for covered spots
- Events within 500m = surge demand
"""
            
            response = self._generate_with_retry(prompt)
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            logger.info(f"Demand forecast: {result['demand_score']}% (multiplier: {result['multiplier']}x)")
            return result
            
        except Exception as e:
            logger.error(f"Demand forecast error: {e}")
            # Fallback to moderate demand
            return {
                'demand_score': 50,
                'multiplier': 1.0,
                'reasoning': 'AI unavailable, using default multiplier',
                'peak_expected': False
            }
    
    def suggest_dynamic_price(self, base_price: float, spot_data: Dict, context: Dict) -> Dict[str, Any]:
        """
        Calculate dynamic pricing using Gemini AI analysis
        
        Args:
            base_price: Base parking price
            spot_data: Spot features (type, features, location)
            context: Current conditions (time, weather, events)
        Returns:
            Dictionary with final_price, breakdown, reasoning
        """
        try:
            prompt = f"""
You are a parking pricing AI. Calculate optimal dynamic price.

Base Price: ${base_price}
Spot Type: {spot_data.get('type', 'regular')}
Features: {', '.join(spot_data.get('features', []))}
Current Time: {context.get('current_time', 'N/A')}
Weather: {context.get('weather', 'Clear')}
Events: {context.get('events', 'None')}

Apply these factors:
1. Time multiplier: Peak (1.5x), Mid-day (1.2x), Off-peak (0.8x)
2. Weather premium: Rain (1.25x), Extreme heat (1.15x)
3. Event premium: Within 500m (1.1x)
4. Spot features: EV charging (+$2), Covered (+$1.50)

Respond in JSON:
{{
  "final_price": <price>,
  "breakdown": {{
    "base": <price>,
    "time_multiplier": <value>,
    "weather_premium": <value>,
    "event_premium": <value>,
    "feature_fees": <value>
  }},
  "reasoning": "<explanation>"
}}
"""
            
            response = self._generate_with_retry(prompt)
            
            import json
            result = json.loads(response)
            
            logger.info(f"Dynamic price: ${result['final_price']:.2f} (base: ${base_price})")
            return result
            
        except Exception as e:
            logger.error(f"Pricing calculation error: {e}")
            return {
                'final_price': base_price,
                'breakdown': {'base': base_price},
                'reasoning': 'AI unavailable, using base price'
            }
    
    # ============================================
    # FRAUD DETECTION
    # ============================================
    
    def detect_payment_fraud(self, payment_data: Dict, wallet_history: List[Dict]) -> Dict[str, Any]:
        """
        Analyze payment for fraud patterns using Gemini AI
        
        Args:
            payment_data: Current payment details
            wallet_history: Past transactions from wallet
        Returns:
            Dictionary with fraud_score (0-100), risk_level, flags, reasoning
        """
        try:
            prompt = f"""
You are a fraud detection AI for blockchain parking payments.

Current Payment:
- Amount: {payment_data.get('amount', 0)} ADA
- Wallet: {payment_data.get('wallet', 'unknown')[:20]}...
- Time: {payment_data.get('timestamp', 'N/A')}

Wallet History:
- Total Transactions: {len(wallet_history)}
- Average Amount: {sum(tx.get('amount', 0) for tx in wallet_history) / max(len(wallet_history), 1):.2f} ADA
- Failed Transactions: {sum(1 for tx in wallet_history if tx.get('status') == 'failed')}

Detect fraud patterns:
1. Unusual payment amounts (>3x average)
2. High failure rate (>30%)
3. New wallet with large transaction
4. Rapid consecutive payments
5. Mismatch with normal behavior

Respond in JSON:
{{
  "fraud_score": <0-100>,
  "risk_level": "<low|medium|high|critical>",
  "flags": [<list of detected issues>],
  "reasoning": "<explanation>",
  "recommend_action": "<approve|review|decline>"
}}
"""
            
            response = self._generate_with_retry(prompt)
            
            import json
            result = json.loads(response)
            
            logger.info(f"Fraud score: {result['fraud_score']}/100 ({result['risk_level']} risk)")
            return result
            
        except Exception as e:
            logger.error(f"Fraud detection error: {e}")
            return {
                'fraud_score': 20,
                'risk_level': 'low',
                'flags': [],
                'reasoning': 'AI unavailable, defaulting to low risk',
                'recommend_action': 'approve'
            }
    
    # ============================================
    # DISPUTE RESOLUTION
    # ============================================
    
    def investigate_dispute(self, dispute_data: Dict, evidence: Dict) -> Dict[str, Any]:
        """
        AI-powered dispute investigation and evidence analysis
        
        Args:
            dispute_data: Dispute details (customer claim, operator response)
            evidence: Sensor data, payment records, timestamps
        Returns:
            Dictionary with confidence (0-100), ruling, reasoning, evidence_analysis
        """
        try:
            prompt = f"""
You are an impartial AI dispute resolver for parking disputes.

DISPUTE CLAIM:
Customer: "{dispute_data.get('customer_claim', 'N/A')}"
Operator: "{dispute_data.get('operator_response', 'N/A')}"
Disputed Amount: ${dispute_data.get('disputed_amount', 0)}

EVIDENCE:
Sensor Data:
- Spot Status at Arrival: {evidence.get('spot_occupied_at_arrival', 'unknown')}
- Session Start: {evidence.get('session_start', 'N/A')}
- Session End: {evidence.get('session_end', 'N/A')}

Payment Records:
- Amount Charged: ${evidence.get('amount_charged', 0)}
- Payment Status: {evidence.get('payment_status', 'unknown')}

Timeline:
- Reserved Time: {evidence.get('reserved_time', 'N/A')}
- Actual Arrival: {evidence.get('actual_arrival', 'N/A')}
- Overstay: {evidence.get('overstay_minutes', 0)} minutes

Analyze evidence and determine:
1. Who is likely correct (>70% = customer wins, <30% = operator wins, 30-70% = split)
2. Which evidence is most compelling
3. Fair resolution

Respond in JSON:
{{
  "confidence": <0-100>,
  "ruling": "<customer_wins|operator_wins|split_decision>",
  "reasoning": "<detailed analysis>",
  "evidence_summary": "<key findings>",
  "payout_distribution": {{
    "customer_gets": "<ADA amount>",
    "operator_gets": "<ADA amount>"
  }}
}}
"""
            
            response = self._generate_with_retry(prompt)
            
            import json
            result = json.loads(response)
            
            logger.info(f"Dispute ruling: {result['ruling']} (confidence: {result['confidence']}%)")
            return result
            
        except Exception as e:
            logger.error(f"Dispute investigation error: {e}")
            return {
                'confidence': 50,
                'ruling': 'split_decision',
                'reasoning': 'AI unavailable, defaulting to split decision',
                'evidence_summary': 'Unable to analyze',
                'payout_distribution': {
                    'customer_gets': '5 ADA (stake refund)',
                    'operator_gets': '5 ADA (stake refund)'
                }
            }
    
    # ============================================
    # ANOMALY DETECTION
    # ============================================
    
    def detect_parking_anomalies(self, session_data: Dict, historical_patterns: List[Dict]) -> Dict[str, Any]:
        """
        Detect unusual parking patterns (for security monitoring)
        
        Args:
            session_data: Current parking session
            historical_patterns: Past parking behavior
        Returns:
            Dictionary with anomaly_score, detected_issues, recommendation
        """
        try:
            prompt = f"""
You are a security AI detecting anomalous parking behavior.

Current Session:
- Duration: {session_data.get('duration_minutes', 0)} minutes
- Spot Type: {session_data.get('spot_type', 'unknown')}
- Time of Day: {session_data.get('time_of_day', 'unknown')}

Historical Patterns:
- Average Duration: {sum(p.get('duration', 0) for p in historical_patterns) / max(len(historical_patterns), 1):.1f} min
- Typical Spots: {', '.join(set(p.get('spot_type', 'unknown') for p in historical_patterns[:5]))}
- Violation History: {sum(1 for p in historical_patterns if p.get('had_violation', False))} incidents

Detect anomalies:
1. Unusually short/long duration
2. Unexpected spot type
3. Pattern of violations
4. Off-hours parking

Respond in JSON:
{{
  "anomaly_score": <0-100>,
  "detected_issues": [<list of issues>],
  "risk_assessment": "<low|medium|high>",
  "recommendation": "<monitor|alert|investigate>"
}}
"""
            
            response = self._generate_with_retry(prompt)
            
            import json
            result = json.loads(response)
            
            logger.info(f"Anomaly detection: {result['anomaly_score']}/100 ({result['risk_assessment']} risk)")
            return result
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return {
                'anomaly_score': 0,
                'detected_issues': [],
                'risk_assessment': 'low',
                'recommendation': 'monitor'
            }


# Singleton instance
gemini_service = GeminiService()
