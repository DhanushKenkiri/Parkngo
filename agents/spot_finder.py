"""
Spot Finder Agent
Uses Gemini AI to find the best parking spot based on user preferences
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from services import firebase_service, gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpotFinderAgent:
    """
    Finds optimal parking spot using:
    1. Firebase queries for available spots
    2. Gemini AI for intelligent ranking based on user preferences
    3. Distance, features, and real-time availability
    """
    
    def __init__(self):
        self.agent_id = "spot_finder_001"
        self.agent_name = "SpotFinder Agent"
        logger.info(f"✅ {self.agent_name} initialized")
    
    def find_best_spot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find the best parking spot for the user
        
        Args:
            request_data: {
                'user_location': {'lat': float, 'lng': float},
                'vehicle_type': str,
                'desired_features': List[str],
                'duration_hours': float
            }
        
        Returns:
            {
                'recommended_spot': {...},
                'alternatives': [...],
                'reasoning': str,
                'confidence': int
            }
        """
        
        logger.info(f"🔍 Finding best spot for vehicle: {request_data.get('vehicle_type')}")
        
        try:
            # Step 1: Get available spots from Firebase
            filters = {
                'features': request_data.get('desired_features', [])
            }
            
            available_spots = firebase_service.get_available_spots(filters)
            
            if not available_spots:
                return {
                    'success': False,
                    'error': 'No available spots found',
                    'recommended_spot': None,
                    'alternatives': []
                }
            
            logger.info(f"📍 Found {len(available_spots)} available spots")
            
            # Step 2: Calculate distances for each spot
            spots_with_distance = self._calculate_distances(
                available_spots,
                request_data['user_location']
            )
            
            # Step 3: Use Gemini AI to rank spots intelligently
            ranked_spots = self._rank_spots_with_ai(
                spots_with_distance,
                request_data
            )
            
            # Step 4: Return top recommendation + alternatives
            return {
                'success': True,
                'recommended_spot': ranked_spots[0] if ranked_spots else None,
                'alternatives': ranked_spots[1:3] if len(ranked_spots) > 1 else [],
                'total_available': len(available_spots),
                'reasoning': ranked_spots[0].get('ai_reasoning') if ranked_spots else '',
                'confidence': ranked_spots[0].get('ai_score', 0) if ranked_spots else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error finding spot: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'recommended_spot': None,
                'alternatives': []
            }
    
    def _calculate_distances(
        self, 
        spots: Dict[str, Any], 
        user_location: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Calculate distance from user to each parking spot"""
        
        spots_list = []
        
        for spot_id, spot_data in spots.items():
            # In production, spots would have coordinates
            # For testing, we'll simulate distances based on zone
            zone = spot_data.get('zone', 'A')
            
            # Simulate distance (zone A closer, zone B farther)
            simulated_distance = {
                'A': 50,   # 50 meters
                'B': 120,  # 120 meters
                'C': 200,  # 200 meters
            }.get(zone, 100)
            
            spot_with_distance = {
                'spot_id': spot_id,
                'zone': spot_data.get('zone'),
                'type': spot_data.get('type'),
                'features': spot_data.get('features', []),
                'distance_meters': simulated_distance,
                'gpio_pin': spot_data.get('gpio_pin')
            }
            
            spots_list.append(spot_with_distance)
        
        return spots_list
    
    def _rank_spots_with_ai(
        self, 
        spots: List[Dict[str, Any]], 
        request_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use Gemini AI to intelligently rank parking spots"""
        
        logger.info("🧠 Using Gemini AI to rank spots...")
        
        # Prepare context for Gemini
        context = f"""
        You are an AI parking assistant. Rank these parking spots for the user.
        
        USER PREFERENCES:
        - Vehicle Type: {request_data.get('vehicle_type')}
        - Desired Features: {request_data.get('desired_features', [])}
        - Duration: {request_data.get('duration_hours')} hours
        
        AVAILABLE SPOTS:
        {self._format_spots_for_ai(spots)}
        
        For each spot, provide:
        1. Score (0-100) - higher is better
        2. Reasoning (one sentence why this score)
        
        Consider:
        - Distance (closer is better)
        - Features match (covered, EV charging, disabled access)
        - Spot type (premium vs regular)
        
        Return as JSON array with format:
        [
          {{"spot_id": "A-01", "score": 95, "reasoning": "Closest spot with all desired features"}},
          ...
        ]
        """
        
        try:
            response = gemini_service._generate_with_retry(context)
            
            # Parse Gemini response
            import json
            try:
                ai_rankings = json.loads(response)
            except:
                # Fallback: parse as best as possible
                logger.warning("⚠️  Failed to parse Gemini JSON, using fallback ranking")
                ai_rankings = self._fallback_ranking(spots)
            
            # Merge AI rankings with spot data
            ranked_spots = []
            for ranking in ai_rankings:
                spot_id = ranking.get('spot_id')
                spot_data = next((s for s in spots if s['spot_id'] == spot_id), None)
                
                if spot_data:
                    spot_data['ai_score'] = ranking.get('score', 50)
                    spot_data['ai_reasoning'] = ranking.get('reasoning', 'AI analysis')
                    ranked_spots.append(spot_data)
            
            # Sort by AI score
            ranked_spots.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
            
            logger.info(f"✅ Gemini ranked {len(ranked_spots)} spots")
            
            return ranked_spots
            
        except Exception as e:
            logger.error(f"❌ Gemini ranking failed: {e}")
            
            # Fallback: simple distance-based ranking
            return self._fallback_ranking(spots)
    
    def _format_spots_for_ai(self, spots: List[Dict[str, Any]]) -> str:
        """Format spots data for Gemini prompt"""
        
        formatted = []
        for spot in spots:
            formatted.append(
                f"- {spot['spot_id']}: {spot['type']} spot, "
                f"{spot['distance_meters']}m away, "
                f"features: {', '.join(spot['features']) if spot['features'] else 'none'}"
            )
        
        return '\n'.join(formatted)
    
    def _fallback_ranking(self, spots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback ranking algorithm when Gemini is unavailable"""
        
        logger.info("⚙️  Using fallback ranking algorithm")
        
        for spot in spots:
            # Simple score: prioritize distance and premium type
            score = 100 - (spot['distance_meters'] / 10)  # Closer = higher score
            
            if spot['type'] == 'premium':
                score += 10
            
            if 'covered' in spot['features']:
                score += 5
            
            if 'ev_charging' in spot['features']:
                score += 5
            
            spot['ai_score'] = min(100, max(0, int(score)))
            spot['ai_reasoning'] = 'Rule-based ranking (Gemini unavailable)'
        
        spots.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return spots


# Singleton instance
spot_finder_agent = SpotFinderAgent()
