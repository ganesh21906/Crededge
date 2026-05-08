"""
BBPS (Bharat Bill Payment System) Integration
Verifies utility bill payment history
"""

import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
import os


class BBPSVerifier:
    """
    Bharat Bill Payment System API Integration
    Official API: https://www.npci.org.in/what-we-do/bbps/product-overview
    """
    
    def __init__(self):
        self.base_url = os.getenv("BBPS_API_URL", "https://api.bbps.npci.org.in/v1")
        self.api_key = os.getenv("BBPS_API_KEY", "")
        self.client_id = os.getenv("BBPS_CLIENT_ID", "")
        self.enabled = bool(self.api_key and self.client_id)
    
    def verify_electricity_bills(self, consumer_number: str, provider_code: str, 
                                mobile: str) -> Dict:
        """
        Verify electricity bill payment history
        
        Args:
            consumer_number: Consumer number from electricity board
            provider_code: BBPS biller code (e.g., MSEDCL, BSES)
            mobile: Registered mobile number
            
        Returns:
            Payment history with regularity score
        """
        if not self.enabled:
            return self._mock_response()
        
        try:
            # Step 1: Fetch biller details
            biller_info = self._get_biller_info(provider_code)
            
            # Step 2: Validate consumer number
            validation = self._validate_consumer(consumer_number, provider_code, mobile)
            
            if not validation.get("valid"):
                return {
                    "verified": False,
                    "error": "Consumer number validation failed",
                    "details": validation.get("message")
                }
            
            # Step 3: Fetch payment history (last 12 months)
            payment_history = self._fetch_payment_history(
                consumer_number, 
                provider_code,
                months=12
            )
            
            # Step 4: Analyze payment patterns
            analysis = self._analyze_payments(payment_history)
            
            return {
                "verified": True,
                "data_source": "bbps_electricity",
                "provider": biller_info.get("name"),
                "provider_code": provider_code,
                "consumer_number_masked": self._mask_consumer_number(consumer_number),
                "verification_method": "live_api",
                "payment_history_months": len(payment_history),
                "total_bills": analysis["total_bills"],
                "on_time_payments": analysis["on_time_count"],
                "late_payments": analysis["late_count"],
                "payment_regularity": analysis["regularity_percentage"],
                "average_bill_amount": analysis["average_amount"],
                "last_payment_date": analysis["last_payment_date"],
                "payment_trend": analysis["trend"],  # "improving", "stable", "declining"
                "verification_timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "verified": False,
                "error": "API request failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "verified": False,
                "error": "Verification failed",
                "details": str(e)
            }
    
    def _get_biller_info(self, provider_code: str) -> Dict:
        """Fetch biller information from BBPS"""
        response = requests.get(
            f"{self.base_url}/billers/{provider_code}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Client-Id": self.client_id,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def _validate_consumer(self, consumer_number: str, provider_code: str, 
                          mobile: str) -> Dict:
        """Validate consumer number with biller"""
        response = requests.post(
            f"{self.base_url}/billers/{provider_code}/validate",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Client-Id": self.client_id,
                "Content-Type": "application/json"
            },
            json={
                "consumer_number": consumer_number,
                "mobile": mobile
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def _fetch_payment_history(self, consumer_number: str, provider_code: str, 
                               months: int = 12) -> list:
        """Fetch payment history from BBPS"""
        from_date = (datetime.now() - timedelta(days=months*30)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")
        
        response = requests.post(
            f"{self.base_url}/payments/history",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Client-Id": self.client_id,
                "Content-Type": "application/json"
            },
            json={
                "consumer_number": consumer_number,
                "biller_code": provider_code,
                "from_date": from_date,
                "to_date": to_date
            },
            timeout=15
        )
        response.raise_for_status()
        return response.json().get("payments", [])
    
    def _analyze_payments(self, payment_history: list) -> Dict:
        """Analyze payment patterns"""
        if not payment_history:
            return {
                "total_bills": 0,
                "on_time_count": 0,
                "late_count": 0,
                "regularity_percentage": 0,
                "average_amount": 0,
                "last_payment_date": None,
                "trend": "no_data"
            }
        
        total_bills = len(payment_history)
        on_time = sum(1 for p in payment_history if p.get("status") == "paid_on_time")
        late = sum(1 for p in payment_history if p.get("status") == "paid_late")
        
        amounts = [p.get("amount", 0) for p in payment_history]
        average_amount = sum(amounts) / len(amounts) if amounts else 0
        
        # Calculate regularity (on-time payments / total bills)
        regularity = (on_time / total_bills * 100) if total_bills > 0 else 0
        
        # Determine trend (compare recent 3 months vs previous 3 months)
        if len(payment_history) >= 6:
            recent_on_time = sum(1 for p in payment_history[:3] if p.get("status") == "paid_on_time")
            previous_on_time = sum(1 for p in payment_history[3:6] if p.get("status") == "paid_on_time")
            
            if recent_on_time > previous_on_time:
                trend = "improving"
            elif recent_on_time < previous_on_time:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        last_payment = payment_history[0] if payment_history else None
        last_payment_date = last_payment.get("payment_date") if last_payment else None
        
        return {
            "total_bills": total_bills,
            "on_time_count": on_time,
            "late_count": late,
            "regularity_percentage": round(regularity, 2),
            "average_amount": round(average_amount, 2),
            "last_payment_date": last_payment_date,
            "trend": trend
        }
    
    def _mask_consumer_number(self, consumer_number: str) -> str:
        """Mask consumer number for privacy (show last 4 digits)"""
        if len(consumer_number) <= 4:
            return consumer_number
        return "X" * (len(consumer_number) - 4) + consumer_number[-4:]
    
    def _mock_response(self) -> Dict:
        """Mock response when API is not configured"""
        return {
            "verified": False,
            "error": "BBPS API not configured",
            "details": "Set BBPS_API_KEY and BBPS_CLIENT_ID environment variables"
        }


# Provider code mappings
ELECTRICITY_PROVIDERS = {
    "MSEDCL": {"name": "Maharashtra State Electricity Distribution Co Ltd", "state": "Maharashtra"},
    "BSES": {"name": "BSES Rajdhani Power Limited", "state": "Delhi"},
    "TSSPDCL": {"name": "Telangana Southern Power Distribution", "state": "Telangana"},
    "BESCOM": {"name": "Bangalore Electricity Supply Company", "state": "Karnataka"},
    "TSNPDCL": {"name": "Telangana Northern Power Distribution", "state": "Telangana"},
    "APEPDCL": {"name": "Andhra Pradesh Eastern Power Distribution", "state": "Andhra Pradesh"},
    "CESC": {"name": "Calcutta Electric Supply Corporation", "state": "West Bengal"},
    "DHBVNL": {"name": "Dakshin Haryana Bijli Vitran Nigam", "state": "Haryana"}
}


if __name__ == "__main__":
    print("="*70)
    print("BBPS ELECTRICITY VERIFICATION TEST")
    print("="*70)
    
    verifier = BBPSVerifier()
    
    if verifier.enabled:
        print("\n✅ BBPS API is configured")
        print(f"   Base URL: {verifier.base_url}")
    else:
        print("\n⚠️  BBPS API not configured (using mock mode)")
        print("   Set environment variables:")
        print("   - BBPS_API_KEY")
        print("   - BBPS_CLIENT_ID")
    
    print("\n" + "="*70)
    print("Available Providers:")
    for code, info in ELECTRICITY_PROVIDERS.items():
        print(f"  {code}: {info['name']} ({info['state']})")
    print("="*70)
