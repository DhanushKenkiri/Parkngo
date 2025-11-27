"""
Route Optimizer Agent
Uses Gemini AI to calculate optimal walking route to parking spot
"""

import logging
import math
from typing import Dict, Any, List, Tuple

from services import gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouteOptimizerAgent:
    """
    Calculates optimal route from user location to parking spot using:
    - Distance calculation (Haversine formula)
    - Walking time estimation
    - Gemini AI for route suggestions and alternative paths
    """
    
    def __init__(self):
        self.agent_id = "route_optimizer_001"
        self.agent_name = "Route Optimizer Agent"
        
        # Average walking speed: 1.4 m/s (5 km/h)
        self.walking_speed_ms = 1.4
        
        logger.info(f"✅ {self.agent_name} initialized")
    
    def optimize_route(
        self, 
        user_location: Dict[str, float], 
        spot_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate optimal route to parking spot
        
        Args:
            user_location: {'lat': float, 'lng': float}
            spot_data: {
                'spot_id': str,
                'zone': str,
                'distance_meters': float (pre-calculated)
            }
        
        Returns:
            {
                'distance_meters': float,
                'walking_time_minutes': float,
                'directions': List[str],
                'alternative_routes': List[...],
                'ai_suggestions': str
            }
        """
        
        logger.info(f"🗺️  Calculating route to spot: {spot_data.get('spot_id')}")
        
        try:
            # Use pre-calculated distance from spot_data
            distance = spot_data.get('distance_meters', 100)
            
            # Calculate walking time
            walking_time_sec = distance / self.walking_speed_ms
            walking_time_min = walking_time_sec / 60
            
            # Use Gemini AI to generate walking directions
            directions = self._generate_directions_with_ai(
                user_location,
                spot_data,
                distance
            )
            
            # Use Gemini AI for route optimization suggestions
            ai_suggestions = self._get_route_suggestions_with_ai(
                spot_data,
                distance,
                walking_time_min
            )
            
            return {
                'distance_meters': round(distance, 1),
                'walking_time_minutes': round(walking_time_min, 1),
                'walking_time_seconds': round(walking_time_sec, 0),
                'directions': directions.get('steps', []),
                'ai_suggestions': ai_suggestions,
                'entrance': self._get_entrance_info(spot_data),
                'accessibility': {
                    'wheelchair_accessible': 'disabled_access' in spot_data.get('features', []),
                    'elevator_available': spot_data.get('zone') in ['A', 'B']  # Simulate
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating route: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: basic route info
            distance = spot_data.get('distance_meters', 100)
            return {
                'distance_meters': distance,
                'walking_time_minutes': round(distance / self.walking_speed_ms / 60, 1),
                'directions': [f"Walk to Zone {spot_data.get('zone')} parking area"],
                'ai_suggestions': 'Basic route (AI unavailable)'
            }
    
    def _generate_directions_with_ai(
        self,
        user_location: Dict[str, float],
        spot_data: Dict[str, Any],
        distance: float
    ) -> Dict[str, Any]:
        """Use Gemini AI to generate step-by-step walking directions"""
        
        logger.info("🧠 Generating directions with Gemini AI...")
        
        context = f"""
        Generate step-by-step walking directions to a parking spot.
        
        USER LOCATION: Entrance area (simulated coordinates: {user_location})
        DESTINATION: Parking Zone {spot_data.get('zone')}, Spot {spot_data.get('spot_id')}
        DISTANCE: {distance} meters
        
        Generate 3-5 simple walking directions as a JSON array:
        [
          "Step 1: ...",
          "Step 2: ...",
          ...
        ]
        
        Keep it practical and clear for someone walking to their car.
        """
        
        try:
            response = gemini_service._generate_with_retry(context)
            
            # Parse Gemini response
            import json
            try:
                steps = json.loads(response)
                if isinstance(steps, list):
                    return {'steps': steps}
                else:
                    raise ValueError("Invalid format")
            except:
                # Try to extract list from response
                import re
                matches = re.findall(r'"(.*?)"', response)
                if matches:
                    return {'steps': matches[:5]}
                else:
                    return {'steps': self._fallback_directions(spot_data)}
            
        except Exception as e:
            logger.error(f"❌ Gemini directions failed: {e}")
            return {'steps': self._fallback_directions(spot_data)}
    
    def _fallback_directions(self, spot_data: Dict[str, Any]) -> List[str]:
        """Fallback directions when Gemini is unavailable"""
        
        zone = spot_data.get('zone', 'A')
        spot_id = spot_data.get('spot_id', '??')
        
        return [
            "Exit the main entrance and turn towards the parking area",
            f"Follow signs to Zone {zone}",
            f"Look for spot {spot_id} on your left",
            "Park your vehicle and lock it securely"
        ]
    
    def _get_route_suggestions_with_ai(
        self,
        spot_data: Dict[str, Any],
        distance: float,
        walking_time: float
    ) -> str:
        """Use Gemini AI to provide helpful route suggestions"""
        
        context = f"""
        Give one helpful tip for someone walking to parking spot {spot_data.get('spot_id')} 
        in Zone {spot_data.get('zone')}.
        
        Distance: {distance} meters (~{walking_time:.1f} min walk)
        Features: {', '.join(spot_data.get('features', []))}
        
        Provide ONE practical tip (1 sentence) like:
        - Weather considerations
        - What to look for
        - Time-saving hints
        
        Be friendly and concise.
        """
        
        try:
            suggestion = gemini_service._generate_with_retry(context)
            
            # Clean up response
            suggestion = suggestion.strip().strip('"\'')
            
            logger.info(f"✅ Gemini route suggestion generated")
            
            return suggestion
            
        except Exception as e:
            logger.error(f"❌ Gemini suggestion failed: {e}")
            
            # Fallback suggestion
            return f"Follow the signs to Zone {spot_data.get('zone')} - it's a {walking_time:.0f} minute walk."
    
    def _get_entrance_info(self, spot_data: Dict[str, Any]) -> Dict[str, str]:
        """Get entrance information for the parking zone"""
        
        zone = spot_data.get('zone', 'A')
        
        # Simulate entrance info
        entrance_map = {
            'A': {
                'name': 'Main Entrance',
                'description': 'Ground floor, near the security booth',
                'coordinates': 'N1, Ground Level'
            },
            'B': {
                'name': 'West Entrance',
                'description': 'Second floor, elevator available',
                'coordinates': 'W2, Level 2'
            },
            'C': {
                'name': 'East Entrance',
                'description': 'Third floor, stairs and elevator',
                'coordinates': 'E3, Level 3'
            }
        }
        
        return entrance_map.get(zone, entrance_map['A'])
    
    def calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Returns distance in meters
        """
        
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)
        
        # Haversine formula
        a = (
            math.sin(delta_phi / 2) ** 2 +
            math.cos(phi1) * math.cos(phi2) *
            math.sin(delta_lambda / 2) ** 2
        )
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return distance


# Singleton instance
route_optimizer_agent = RouteOptimizerAgent()
