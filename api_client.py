import requests
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from config import settings
import asyncio

class BackendAPIClient:
    """Client for communicating with FastAPI backend on Railway"""
    
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self._session = None
        
    @property
    def session(self):
        """Lazy session initialization"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "Retail-Chatbot/1.0",
                "Accept": "application/json"
            })
        return self._session
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = "GET") -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=self.timeout)
                else:
                    response = self.session.post(url, json=params, timeout=self.timeout)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Request to {endpoint} timed out after {self.max_retries} attempts")
                asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to call {endpoint}: {str(e)}")
                asyncio.sleep(1 * (attempt + 1))
        
        return None
    
    async def _make_async_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Async request failed: {e}")
                return None
    
    # Health Check
    def check_backend_health(self) -> Dict:
        """Check if backend is accessible"""
        try:
            return self._make_request(settings.API_ENDPOINTS["health"])
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Visitor Data Methods
    def get_current_visitors(self) -> Dict:
        """Get current visitor count"""
        return self._make_request(settings.API_ENDPOINTS["visitors_current"]) or {}
    
    def get_section_traffic(self) -> List[Dict]:
        """Get visitor distribution by section"""
        return self._make_request(settings.API_ENDPOINTS["visitors_sections"]) or []
    
    def get_daily_analytics(self) -> Dict:
        """Get daily analytics summary"""
        return self._make_request(settings.API_ENDPOINTS["daily_analytics"]) or {}
    
    def get_visitor_trend(self, hours: int = 6) -> List[Dict]:
        """Get visitor trend over specified hours"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        return self._make_request("/api/visitors/range", params) or []
    
    # Cashier Data Methods
    def get_cashier_status(self) -> Dict:
        """Get current cashier queue status"""
        return self._make_request(settings.API_ENDPOINTS["cashier_current"]) or {}
    
    def get_queue_history(self, hours: int = 6) -> List[Dict]:
        """Get cashier queue history"""
        return self._make_request(f"{settings.API_ENDPOINTS['cashier_history']}?hours={hours}") or []
    
    def get_wait_time(self) -> Dict:
        """Get estimated wait time"""
        return self._make_request(settings.API_ENDPOINTS["cashier_wait_time"]) or {}
    
    # Heatmap Methods
    def get_heatmap_data(self) -> List[Dict]:
        """Get latest heatmap data"""
        return self._make_request(settings.API_ENDPOINTS["heatmap"]) or []
    
    def get_density_analysis(self) -> Dict:
        """Get heatmap density analysis"""
        return self._make_request(f"{settings.API_ENDPOINTS['heatmap']}analysis") or {}
    
    # Prediction Methods
    def get_predictions(self) -> List[Dict]:
        """Get all predictions"""
        return self._make_request(settings.API_ENDPOINTS["predictions"]) or []
    
    def get_traffic_forecast(self) -> Dict:
        """Get traffic forecast"""
        return self._make_request(f"{settings.API_ENDPOINTS['predictions']}traffic/forecast") or {}
    
    def get_metric_prediction(self, metric_type: str, horizon: str = "4h") -> Dict:
        """Get prediction for specific metric"""
        return self._make_request(f"{settings.API_ENDPOINTS['predictions']}metric/{metric_type}?horizon={horizon}") or {}
    
    # Batch Operations
    async def get_multiple_metrics(self) -> Dict[str, Any]:
        """Get multiple metrics concurrently"""
        endpoints = [
            settings.API_ENDPOINTS["visitors_current"],
            settings.API_ENDPOINTS["cashier_current"],
            settings.API_ENDPOINTS["heatmap"]
        ]
        
        tasks = [self._make_async_request(endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks)
        
        return {
            "visitors": results[0],
            "cashier": results[1],
            "heatmap": results[2]
        }

# Global client instance
api_client = BackendAPIClient()