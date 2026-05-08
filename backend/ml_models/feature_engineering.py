"""
Feature Engineering Pipeline for Credit Risk Assessment
Transforms raw alternative data into ML model features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class AlternativeDataFeatureEngineering:
    """
    Feature engineering for alternative credit data sources
    """
    
    def __init__(self):
        self.feature_names = []
        
    def engineer_features(self, application_data: Dict) -> Dict:
        """
        Main feature engineering pipeline
        """
        features = {}
        
        # 1. Payment Behavior Features (35% weight)
        features.update(self._payment_behavior_features(application_data))
        
        # 2. Income Stability Features (25% weight)
        features.update(self._income_stability_features(application_data))
        
        # 3. Digital Footprint Features (20% weight)
        features.update(self._digital_footprint_features(application_data))
        
        # 4. Employment/Business Features (15% weight)
        features.update(self._employment_business_features(application_data))
        
        # 5. Financial Behavior Features (5% weight)
        features.update(self._financial_behavior_features(application_data))
        
        # 6. Demographic Features
        features.update(self._demographic_features(application_data))
        
        # 7. Alternative Data Availability Score
        features['alternative_data_count'] = self._count_alternative_sources(application_data)
        
        return features
    
    def _payment_behavior_features(self, data: Dict) -> Dict:
        """
        Features related to payment history (utility, rent, etc.)
        """
        features = {}
        
        # Simulate utility payment data analysis
        if data.get('hasUtilityBills'):
            # In real implementation, this would analyze actual bill data
            features['utility_payment_regularity'] = np.random.uniform(80, 98)
            features['utility_payment_delay_count'] = np.random.randint(0, 3)
            features['utility_longest_streak_months'] = np.random.randint(12, 36)
            features['utility_avg_amount'] = np.random.uniform(2000, 5000)
        else:
            features['utility_payment_regularity'] = 0
            features['utility_payment_delay_count'] = -1
            features['utility_longest_streak_months'] = 0
            features['utility_avg_amount'] = 0
        
        # Rent payment history
        if data.get('hasRentalAgreement'):
            features['rent_payment_punctuality'] = np.random.uniform(85, 100)
            features['rent_tenure_months'] = data.get('yearsAtAddress', 1) * 12
            features['rent_amount'] = np.random.uniform(8000, 25000)
        else:
            features['rent_payment_punctuality'] = 0
            features['rent_tenure_months'] = 0
            features['rent_amount'] = 0
        
        # Combined payment score
        payment_scores = [
            features['utility_payment_regularity'],
            features['rent_payment_punctuality']
        ]
        features['overall_payment_score'] = np.mean([s for s in payment_scores if s > 0]) if any(s > 0 for s in payment_scores) else 50
        
        return features
    
    def _income_stability_features(self, data: Dict) -> Dict:
        """
        Features related to income consistency and stability
        """
        features = {}
        
        monthly_income = data.get('monthlyIncome', 0)
        employment_type = data.get('employmentType', 'unemployed')
        years_employed = data.get('yearsEmployed', 0)
        
        # Income level
        features['monthly_income'] = monthly_income
        features['annual_income'] = monthly_income * 12
        
        # Income stability based on employment type
        stability_mapping = {
            'salaried': 0.9,
            'self-employed': 0.7,
            'freelancer': 0.6,
            'business': 0.7,
            'unemployed': 0.1,
            'student': 0.3
        }
        features['income_stability_score'] = stability_mapping.get(employment_type, 0.5) * 100
        
        # Employment tenure
        features['employment_tenure_months'] = years_employed * 12 if years_employed else 0
        
        # Income-to-loan ratio
        loan_amount = data.get('loanAmount', 0)
        if monthly_income > 0:
            features['loan_to_income_ratio'] = loan_amount / (monthly_income * 12)
        else:
            features['loan_to_income_ratio'] = 999  # Very high risk
        
        # Simulated income volatility (in real case, from bank statements)
        features['income_volatility'] = np.random.uniform(0.05, 0.20)  # Lower is better
        
        return features
    
    def _digital_footprint_features(self, data: Dict) -> Dict:
        """
        Features from digital payment behavior (UPI, wallets)
        """
        features = {}
        
        if data.get('hasUPIHistory'):
            # Simulate UPI transaction analysis
            features['upi_transaction_count_monthly'] = np.random.randint(50, 200)
            features['upi_avg_transaction_amount'] = np.random.uniform(500, 2000)
            features['upi_merchant_diversity'] = np.random.randint(20, 60)
            features['upi_consistency_score'] = np.random.uniform(70, 95)
            
            # Spending pattern
            features['savings_to_spending_ratio'] = np.random.uniform(0.10, 0.35)
        else:
            features['upi_transaction_count_monthly'] = 0
            features['upi_avg_transaction_amount'] = 0
            features['upi_merchant_diversity'] = 0
            features['upi_consistency_score'] = 0
            features['savings_to_spending_ratio'] = 0
        
        # Social media presence (professional verification)
        features['social_media_verified'] = 1 if data.get('hasSocialMedia') else 0
        
        # Overall digital footprint score
        if data.get('hasUPIHistory'):
            features['digital_footprint_score'] = (
                features['upi_consistency_score'] * 0.4 +
                min(features['upi_merchant_diversity'], 50) * 2 * 0.3 +
                min(features['upi_transaction_count_monthly'] / 2, 100) * 0.3
            )
        else:
            features['digital_footprint_score'] = 0
        
        return features
    
    def _employment_business_features(self, data: Dict) -> Dict:
        """
        Employment or business profile features
        """
        features = {}
        
        employment_type = data.get('employmentType', 'unemployed')
        
        # For individuals
        if employment_type in ['salaried', 'self-employed', 'freelancer']:
            features['is_salaried'] = 1 if employment_type == 'salaried' else 0
            features['is_self_employed'] = 1 if employment_type == 'self-employed' else 0
            features['is_freelancer'] = 1 if employment_type == 'freelancer' else 0
            
            # Industry risk (IT is lower risk, others medium)
            industry = data.get('industryType', 'other')
            industry_risk = {
                'it': 0.9,
                'banking': 0.85,
                'healthcare': 0.8,
                'education': 0.75,
                'retail': 0.65,
                'manufacturing': 0.7,
                'other': 0.6
            }
            features['industry_stability_score'] = industry_risk.get(industry, 0.6) * 100
            
            # Employer verification (simulated)
            features['employer_verified'] = np.random.choice([0, 1], p=[0.2, 0.8])
        
        # For SMEs (from businessType, annualRevenue, etc.)
        elif 'businessName' in data or 'annualRevenue' in data:
            features['is_business'] = 1
            features['business_vintage_years'] = datetime.now().year - data.get('yearOfEstablishment', datetime.now().year)
            
            # GST compliance
            features['gst_registered'] = 1 if data.get('gstNumber') else 0
            features['gst_filing_regularity'] = np.random.uniform(85, 100) if data.get('hasGSTReturns') else 0
            
            # Revenue analysis
            annual_revenue = data.get('annualRevenue', 0)
            features['annual_revenue'] = annual_revenue
            features['revenue_to_loan_ratio'] = annual_revenue / data.get('loanAmount', 1) if annual_revenue > 0 else 0
            
        else:
            features['is_unemployed'] = 1
            features['employment_risk_score'] = 20
        
        return features
    
    def _financial_behavior_features(self, data: Dict) -> Dict:
        """
        Banking and financial behavior features
        """
        features = {}
        
        # Bank account presence
        features['has_bank_account'] = 1 if data.get('hasBankAccount') else 0
        
        # Get monthly income first (needed for later calculations)
        monthly_income = data.get('monthlyIncome', 1)
        
        if data.get('hasBankAccount'):
            avg_balance = data.get('averageBalance', 0)
            
            features['avg_bank_balance'] = avg_balance
            features['balance_to_income_ratio'] = avg_balance / monthly_income if monthly_income > 0 else 0
            
            # Savings behavior
            features['savings_rate'] = min((avg_balance / monthly_income) * 100, 100) if monthly_income > 0 else 0
        else:
            features['avg_bank_balance'] = 0
            features['balance_to_income_ratio'] = 0
            features['savings_rate'] = 0
        
        # Debt burden (simulated - in real case from credit bureau)
        features['existing_debt_amount'] = np.random.uniform(0, monthly_income * 5)
        features['debt_to_income_ratio'] = features['existing_debt_amount'] / (monthly_income * 12) if monthly_income > 0 else 0
        
        return features
    
    def _demographic_features(self, data: Dict) -> Dict:
        """
        Demographic features (age, education, location, etc.)
        """
        features = {}
        
        # Age calculation
        if 'dateOfBirth' in data:
            try:
                dob = pd.to_datetime(data['dateOfBirth'])
                age = (datetime.now() - dob).days / 365.25
                features['age'] = age
                features['age_group'] = self._get_age_group(age)
            except:
                features['age'] = 30
                features['age_group'] = 2
        else:
            features['age'] = 30
            features['age_group'] = 2
        
        # Education level
        education_mapping = {
            '10th': 1,
            '12th': 2,
            'diploma': 3,
            'graduate': 4,
            'postgraduate': 5,
            'phd': 6
        }
        features['education_level'] = education_mapping.get(data.get('qualification', 'graduate'), 4)
        
        # Marital status
        features['is_married'] = 1 if data.get('maritalStatus') == 'married' else 0
        features['dependents_count'] = data.get('dependents', 0)
        
        # Residence stability
        features['years_at_address'] = data.get('yearsAtAddress', 1)
        features['residence_owned'] = 1 if data.get('residenceType') == 'owned' else 0
        
        # Location tier (simulated - in real case from pincode)
        features['location_tier'] = np.random.choice([1, 2, 3], p=[0.3, 0.4, 0.3])
        
        return features
    
    def _count_alternative_sources(self, data: Dict) -> int:
        """
        Count how many alternative data sources are available
        """
        count = 0
        sources = [
            'hasUtilityBills',
            'hasRentalAgreement',
            'hasUPIHistory',
            'hasSocialMedia',
            'hasGSTReturns',
            'hasBankAccount'
        ]
        for source in sources:
            if data.get(source):
                count += 1
        return count
    
    def _get_age_group(self, age: float) -> int:
        """
        Age group encoding
        """
        if age < 25:
            return 1
        elif age < 35:
            return 2
        elif age < 45:
            return 3
        elif age < 55:
            return 4
        else:
            return 5
    
    def get_feature_dataframe(self, application_data: Dict) -> pd.DataFrame:
        """
        Convert features to pandas DataFrame for model input
        """
        features = self.engineer_features(application_data)
        return pd.DataFrame([features])
    
    def get_feature_names(self) -> List[str]:
        """
        Return list of all feature names
        """
        # Return sample to get feature names
        sample_data = {
            'monthlyIncome': 50000,
            'employmentType': 'salaried',
            'yearsEmployed': 3,
            'hasUtilityBills': True,
            'hasRentalAgreement': True,
            'hasUPIHistory': True,
            'hasSocialMedia': True,
            'hasBankAccount': True,
            'loanAmount': 200000,
            'dateOfBirth': '1990-01-01',
            'qualification': 'graduate',
            'maritalStatus': 'married',
            'dependents': 2,
            'yearsAtAddress': 3,
            'residenceType': 'rented',
            'averageBalance': 25000
        }
        features = self.engineer_features(sample_data)
        return list(features.keys())


if __name__ == "__main__":
    # Test the feature engineering
    sample_application = {
        'fullName': 'Test User',
        'dateOfBirth': '1992-05-15',
        'monthlyIncome': 55000,
        'employmentType': 'salaried',
        'yearsEmployed': 4,
        'industryType': 'it',
        'qualification': 'graduate',
        'maritalStatus': 'married',
        'dependents': 1,
        'yearsAtAddress': 3.5,
        'residenceType': 'rented',
        'hasBankAccount': True,
        'averageBalance': 28000,
        'hasUtilityBills': True,
        'hasRentalAgreement': True,
        'hasUPIHistory': True,
        'hasSocialMedia': True,
        'loanAmount': 250000
    }
    
    fe = AlternativeDataFeatureEngineering()
    features = fe.engineer_features(sample_application)
    
    print("Engineered Features:")
    print("-" * 50)
    for key, value in features.items():
        print(f"{key:40s}: {value}")
    
    print(f"\nTotal features: {len(features)}")
    print(f"Alternative data sources available: {features['alternative_data_count']}")
