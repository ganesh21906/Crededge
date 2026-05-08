"""
GST Portal API Integration
Verifies GST filing history and business compliance for SMEs
"""

import requests
from typing import Dict, Optional
from datetime import datetime
import os
import hashlib


class GSTPortalClient:
    """
    GST Portal API Integration for business verification
    Official: https://gstcouncil.gov.in/
    """
    
    def __init__(self):
        self.base_url = os.getenv("GST_API_URL", "https://api.gstportal.gov.in/v1")
        self.api_key = os.getenv("GST_API_KEY", "")
        self.enabled = bool(self.api_key)
    
    def verify_gstin(self, gstin: str) -> Dict:
        """
        Verify GSTIN and get basic business details
        
        Args:
            gstin: 15-character GST Identification Number
            
        Returns:
            Business registration details
        """
        if not self.enabled:
            return self._mock_gstin_verification(gstin)
        
        if not self._validate_gstin_format(gstin):
            return {
                "verified": False,
                "error": "Invalid GSTIN format"
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/taxpayers/{gstin}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "verified": True,
                "gstin": gstin,
                "legal_name": data.get("legalName"),
                "trade_name": data.get("tradeName"),
                "registration_date": data.get("registrationDate"),
                "status": data.get("status"),  # "Active", "Cancelled"
                "taxpayer_type": data.get("taxpayerType"),
                "state_jurisdiction": data.get("stateJurisdiction"),
                "business_nature": data.get("natureOfBusinessActivity"),
                "verification_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "verified": False,
                "error": "GSTIN verification failed",
                "details": str(e)
            }
    
    def fetch_return_filing_history(self, gstin: str, financial_year: str = None) -> Dict:
        """
        Fetch GST return filing history
        
        Args:
            gstin: GST Identification Number
            financial_year: FY format "2025-26" (defaults to current FY)
            
        Returns:
            Filing history with regularity analysis
        """
        if not self.enabled:
            return self._mock_filing_history(gstin)
        
        if not financial_year:
            # Current financial year (Apr-Mar)
            now = datetime.now()
            if now.month >= 4:
                financial_year = f"{now.year}-{str(now.year + 1)[-2:]}"
            else:
                financial_year = f"{now.year - 1}-{str(now.year)[-2:]}"
        
        try:
            response = requests.get(
                f"{self.base_url}/taxpayers/{gstin}/returns",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "fy": financial_year
                },
                timeout=15
            )
            response.raise_for_status()
            
            returns_data = response.json().get("returns", [])
            
            # Analyze filing compliance
            analysis = self._analyze_filing_compliance(returns_data)
            
            return {
                "verified": True,
                "data_source": "gst_portal",
                "verification_method": "live_api",
                "gstin": gstin,
                "financial_year": financial_year,
                "total_returns_due": analysis["total_due"],
                "returns_filed": analysis["filed_count"],
                "returns_pending": analysis["pending_count"],
                "filing_regularity": analysis["regularity_percentage"],
                "late_filings": analysis["late_count"],
                "nil_returns": analysis["nil_count"],
                "average_turnover_monthly": analysis["avg_turnover"],
                "compliance_rating": analysis["compliance_rating"],
                "last_filing_date": analysis["last_filing_date"],
                "filing_history": returns_data[:12],  # Last 12 months
                "verification_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "verified": False,
                "error": "Filing history fetch failed",
                "details": str(e)
            }
    
    def get_turnover_details(self, gstin: str, period: str = "annual") -> Dict:
        """
        Get business turnover from GST filings
        
        Args:
            gstin: GST Identification Number
            period: "monthly", "quarterly", "annual"
        """
        if not self.enabled:
            return self._mock_turnover(gstin)
        
        try:
            response = requests.get(
                f"{self.base_url}/taxpayers/{gstin}/turnover",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "period": period
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "verified": True,
                "period": period,
                "total_turnover": data.get("totalTurnover"),
                "taxable_turnover": data.get("taxableTurnover"),
                "tax_paid": data.get("taxPaid"),
                "period_details": data.get("periodDetails", [])
            }
            
        except Exception as e:
            return {
                "verified": False,
                "error": "Turnover fetch failed",
                "details": str(e)
            }
    
    def _validate_gstin_format(self, gstin: str) -> bool:
        """
        Validate GSTIN format: 15 characters
        Format: 2 digits (state) + 10 chars (PAN) + 1 char (entity) + 1 char (Z) + 1 check digit
        """
        if not gstin or len(gstin) != 15:
            return False
        
        # Check state code (01-37)
        try:
            state_code = int(gstin[:2])
            if state_code < 1 or state_code > 37:
                return False
        except ValueError:
            return False
        
        # Check if characters are alphanumeric
        return gstin.isalnum()
    
    def _analyze_filing_compliance(self, returns_data: list) -> Dict:
        """Analyze GST filing compliance"""
        if not returns_data:
            return {
                "total_due": 0,
                "filed_count": 0,
                "pending_count": 0,
                "regularity_percentage": 0,
                "late_count": 0,
                "nil_count": 0,
                "avg_turnover": 0,
                "compliance_rating": "no_data",
                "last_filing_date": None
            }
        
        total_due = len(returns_data)
        filed = [r for r in returns_data if r.get("status") in ["FILED", "FILED_LATE"]]
        filed_count = len(filed)
        pending_count = total_due - filed_count
        
        late_count = len([r for r in filed if r.get("status") == "FILED_LATE"])
        nil_count = len([r for r in filed if r.get("type") == "NIL"])
        
        # Calculate regularity
        regularity = (filed_count / total_due * 100) if total_due > 0 else 0
        
        # Calculate average turnover
        turnovers = [float(r.get("turnover", 0)) for r in filed if r.get("turnover")]
        avg_turnover = sum(turnovers) / len(turnovers) if turnovers else 0
        
        # Compliance rating
        if regularity >= 90:
            compliance_rating = "excellent"
        elif regularity >= 75:
            compliance_rating = "good"
        elif regularity >= 60:
            compliance_rating = "average"
        else:
            compliance_rating = "poor"
        
        # Last filing date
        last_filing = None
        if filed:
            sorted_filings = sorted(filed, key=lambda x: x.get("filing_date", ""), reverse=True)
            last_filing = sorted_filings[0].get("filing_date")
        
        return {
            "total_due": total_due,
            "filed_count": filed_count,
            "pending_count": pending_count,
            "regularity_percentage": round(regularity, 2),
            "late_count": late_count,
            "nil_count": nil_count,
            "avg_turnover": round(avg_turnover, 2),
            "compliance_rating": compliance_rating,
            "last_filing_date": last_filing
        }
    
    def _mock_gstin_verification(self, gstin: str) -> Dict:
        """Mock GSTIN verification for testing"""
        import random
        
        return {
            "verified": True,
            "gstin": gstin,
            "legal_name": "MOCK ENTERPRISES PRIVATE LIMITED",
            "trade_name": "Mock Enterprises",
            "registration_date": "2020-04-01",
            "status": "Active",
            "taxpayer_type": "Regular",
            "state_jurisdiction": "Maharashtra",
            "business_nature": ["Retail Trading", "Services"],
            "verification_timestamp": datetime.now().isoformat(),
            "note": "Mock data - GST API not configured"
        }
    
    def _mock_filing_history(self, gstin: str) -> Dict:
        """Mock filing history for testing"""
        import random
        
        filed_count = random.randint(9, 12)
        total_due = 12
        
        return {
            "verified": True,
            "data_source": "gst_portal_mock",
            "verification_method": "mock",
            "gstin": gstin,
            "financial_year": "2025-26",
            "total_returns_due": total_due,
            "returns_filed": filed_count,
            "returns_pending": total_due - filed_count,
            "filing_regularity": round((filed_count / total_due) * 100, 2),
            "late_filings": random.randint(0, 2),
            "nil_returns": random.randint(0, 1),
            "average_turnover_monthly": random.randint(200000, 5000000),
            "compliance_rating": "good" if filed_count >= 10 else "average",
            "last_filing_date": "2026-01-01",
            "note": "Mock data - GST API not configured"
        }
    
    def _mock_turnover(self, gstin: str) -> Dict:
        """Mock turnover data"""
        import random
        
        return {
            "verified": True,
            "period": "annual",
            "total_turnover": random.randint(5000000, 50000000),
            "taxable_turnover": random.randint(4000000, 45000000),
            "tax_paid": random.randint(500000, 5000000),
            "note": "Mock data - GST API not configured"
        }


if __name__ == "__main__":
    print("="*70)
    print("GST PORTAL VERIFICATION TEST")
    print("="*70)
    
    client = GSTPortalClient()
    
    if client.enabled:
        print("\n✅ GST API is configured")
        print(f"   Base URL: {client.base_url}")
    else:
        print("\n⚠️  GST API not configured (using mock mode)")
        print("   Set environment variable: GST_API_KEY")
    
    print("\n" + "="*70)
    print("Testing with sample GSTIN...")
    print("="*70)
    
    # Test GSTIN verification
    test_gstin = "29ABCDE1234F1Z5"
    
    gstin_result = client.verify_gstin(test_gstin)
    print(f"\n[1] GSTIN Verification:")
    print(f"    Verified: {gstin_result.get('verified')}")
    if gstin_result.get('verified'):
        print(f"    Legal Name: {gstin_result['legal_name']}")
        print(f"    Status: {gstin_result['status']}")
    
    # Test filing history
    filing_result = client.fetch_return_filing_history(test_gstin)
    print(f"\n[2] Filing History:")
    print(f"    Verified: {filing_result.get('verified')}")
    if filing_result.get('verified'):
        print(f"    Returns Filed: {filing_result['returns_filed']}/{filing_result['total_returns_due']}")
        print(f"    Filing Regularity: {filing_result['filing_regularity']}%")
        print(f"    Compliance Rating: {filing_result['compliance_rating']}")
        print(f"    Avg Monthly Turnover: ₹{filing_result['average_turnover_monthly']:,.2f}")
    
    print("\n" + "="*70)
