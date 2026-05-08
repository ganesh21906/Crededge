"""
Synthetic Data Generator for Credit Risk Model Training
Generates realistic loan application data with alternative data features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class SyntheticDataGenerator:
    """
    Generate synthetic training data for credit risk model
    """
    
    def __init__(self, n_samples=5000, random_state=42):
        self.n_samples = n_samples
        self.random_state = random_state
        np.random.seed(random_state)
        random.seed(random_state)
    
    def generate_dataset(self) -> pd.DataFrame:
        """
        Generate complete synthetic dataset with alternative data features
        """
        print(f"Generating {self.n_samples} synthetic loan applications...")
        
        data = []
        
        for i in range(self.n_samples):
            application = self._generate_single_application(i)
            data.append(application)
        
        df = pd.DataFrame(data)
        
        # Generate target variable (loan outcome)
        df = self._generate_target_variable(df)
        
        print(f"Dataset generated: {df.shape}")
        print(f"Default rate: {(1 - df['loan_repaid'].mean()) * 100:.2f}%")
        
        return df
    
    def _generate_single_application(self, idx: int) -> dict:
        """
        Generate a single loan application with all features
        """
        app = {}
        
        # Application ID
        app['application_id'] = f"APP-{idx:06d}"
        app['application_date'] = datetime.now() - timedelta(days=random.randint(1, 365))
        
        # Demographics
        app['age'] = np.random.normal(35, 10)
        app['age'] = max(22, min(65, app['age']))  # Clamp between 22-65
        
        app['gender'] = random.choice(['male', 'female'])
        app['marital_status'] = random.choices(['single', 'married', 'divorced'], weights=[0.3, 0.6, 0.1])[0]
        app['dependents'] = np.random.poisson(1.2)
        
        # Education
        app['education_level'] = random.choices([1, 2, 3, 4, 5, 6], [0.05, 0.1, 0.15, 0.4, 0.25, 0.05])[0]
        
        # Location
        app['location_tier'] = random.choices([1, 2, 3], weights=[0.3, 0.4, 0.3])[0]
        app['years_at_address'] = max(0.5, np.random.exponential(3))
        app['residence_owned'] = random.choices([0, 1], weights=[0.65, 0.35])[0]
        
        # Employment
        employment_types = ['salaried', 'self-employed', 'freelancer', 'business']
        app['employment_type'] = random.choices(employment_types, weights=[0.55, 0.25, 0.15, 0.05])[0]
        app['employment_tenure_months'] = max(3, np.random.exponential(36))
        
        # Income (based on education and employment type)
        base_income = 25000 + app['education_level'] * 5000
        if app['employment_type'] == 'salaried':
            app['monthly_income'] = base_income * np.random.uniform(1.0, 2.5)
        elif app['employment_type'] == 'self-employed':
            app['monthly_income'] = base_income * np.random.uniform(0.8, 3.0)
        elif app['employment_type'] == 'freelancer':
            app['monthly_income'] = base_income * np.random.uniform(0.6, 2.5)
        else:  # business
            app['monthly_income'] = base_income * np.random.uniform(1.5, 5.0)
        
        app['annual_income'] = app['monthly_income'] * 12
        
        # Income stability
        stability_by_type = {
            'salaried': 0.9,
            'self-employed': 0.7,
            'freelancer': 0.6,
            'business': 0.7
        }
        app['income_stability_score'] = stability_by_type[app['employment_type']] * 100 * np.random.uniform(0.9, 1.1)
        app['income_volatility'] = np.random.uniform(0.05, 0.25)
        
        # Industry
        app['industry_stability_score'] = np.random.uniform(60, 95)
        app['employer_verified'] = random.choices([0, 1], weights=[0.2, 0.8])[0]
        
        # Banking
        app['has_bank_account'] = random.choices([0, 1], weights=[0.05, 0.95])[0]
        if app['has_bank_account']:
            app['avg_bank_balance'] = app['monthly_income'] * np.random.uniform(0.1, 1.5)
            app['balance_to_income_ratio'] = app['avg_bank_balance'] / app['monthly_income']
            app['savings_rate'] = min(100, app['balance_to_income_ratio'] * 100)
        else:
            app['avg_bank_balance'] = 0
            app['balance_to_income_ratio'] = 0
            app['savings_rate'] = 0
        
        # Debt
        app['existing_debt_amount'] = app['monthly_income'] * np.random.uniform(0, 4)
        app['debt_to_income_ratio'] = app['existing_debt_amount'] / app['annual_income']
        
        # Payment History - CRITICAL FEATURES
        # Good payers have high regularity, bad payers have low
        payment_quality = np.random.beta(8, 2)  # Skewed towards good payers
        
        app['utility_payment_regularity'] = payment_quality * 100 * np.random.uniform(0.9, 1.0)
        app['utility_payment_delay_count'] = int((1 - payment_quality) * 10)
        app['utility_longest_streak_months'] = int(payment_quality * 36)
        app['utility_avg_amount'] = np.random.uniform(2000, 5000)
        
        app['rent_payment_punctuality'] = payment_quality * 100 * np.random.uniform(0.85, 1.0)
        app['rent_tenure_months'] = app['years_at_address'] * 12
        app['rent_amount'] = np.random.uniform(8000, 25000)
        
        app['overall_payment_score'] = (app['utility_payment_regularity'] + app['rent_payment_punctuality']) / 2
        
        # Digital Footprint
        has_digital = random.choices([0, 1], weights=[0.15, 0.85])[0]
        if has_digital:
            app['upi_transaction_count_monthly'] = int(np.random.gamma(5, 20))
            app['upi_avg_transaction_amount'] = np.random.uniform(500, 2500)
            app['upi_merchant_diversity'] = int(np.random.gamma(3, 10))
            app['upi_consistency_score'] = payment_quality * 100 * np.random.uniform(0.8, 1.0)
            app['savings_to_spending_ratio'] = np.random.uniform(0.05, 0.40)
            app['digital_footprint_score'] = (
                app['upi_consistency_score'] * 0.4 +
                min(app['upi_merchant_diversity'], 50) * 2 * 0.3 +
                min(app['upi_transaction_count_monthly'] / 2, 100) * 0.3
            )
        else:
            app['upi_transaction_count_monthly'] = 0
            app['upi_avg_transaction_amount'] = 0
            app['upi_merchant_diversity'] = 0
            app['upi_consistency_score'] = 0
            app['savings_to_spending_ratio'] = 0
            app['digital_footprint_score'] = 0
        
        # Social media
        app['social_media_verified'] = random.choices([0, 1], weights=[0.3, 0.7])[0]
        
        # Alternative data count
        app['alternative_data_count'] = sum([
            app['utility_payment_regularity'] > 0,
            app['rent_payment_punctuality'] > 0,
            has_digital,
            app['social_media_verified'],
            app['has_bank_account']
        ])
        
        # Loan details
        app['loan_amount'] = np.random.choice([50000, 100000, 150000, 200000, 300000, 500000], 
                                               p=[0.2, 0.25, 0.20, 0.15, 0.12, 0.08])
        app['loan_to_income_ratio'] = app['loan_amount'] / app['annual_income']
        app['loan_purpose'] = random.choice(['education', 'medical', 'business', 'home', 'vehicle', 'wedding', 'debt'])
        app['repayment_period_months'] = random.choice([12, 24, 36, 60])
        
        return app
    
    def _generate_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate loan outcome based on features (logistic relationship)
        This creates a realistic relationship between features and default risk
        """
        # Create a risk score based on key features
        risk_score = (
            df['overall_payment_score'] * 0.35 +  # Payment history most important
            df['income_stability_score'] * 0.25 +
            df['digital_footprint_score'] * 0.20 +
            (100 - df['debt_to_income_ratio'] * 100).clip(0, 100) * 0.15 +
            df['savings_rate'] * 0.05
        )
        
        # Add some randomness
        risk_score = risk_score + np.random.normal(0, 10, len(df))
        
        # Convert to probability (sigmoid function)
        probability_repaid = 1 / (1 + np.exp(-(risk_score - 60) / 10))
        
        # Generate binary outcome
        df['loan_repaid'] = (np.random.random(len(df)) < probability_repaid).astype(int)
        df['loan_defaulted'] = 1 - df['loan_repaid']
        
        # Calculate what their credit score would be
        df['true_credit_score'] = (risk_score * 10).clip(300, 900)
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, filepath: str):
        """
        Save dataset to CSV
        """
        df.to_csv(filepath, index=False)
        print(f"Dataset saved to: {filepath}")
    
    def generate_train_test_split(self, df=None, test_size=0.2, val_size=0.1):
        """
        Generate and split dataset into train, validation, and test sets
        """
        if df is None:
            df = self.generate_dataset()
        
        # Convert datetime to string to avoid multiplication issues
        if 'application_date' in df.columns:
            df['application_date'] = df['application_date'].astype(str)
        
        # Shuffle
        df = df.sample(frac=1, random_state=self.random_state).reset_index(drop=True)
        
        # Split
        n = len(df)
        n_test = int(n * test_size)
        n_val = int(n * val_size)
        n_train = n - n_test - n_val
        
        train_df = df.iloc[:n_train]
        val_df = df.iloc[n_train:n_train + n_val]
        test_df = df.iloc[n_train + n_val:]
        
        print(f"\nDataset split:")
        print(f"Train: {len(train_df)} samples ({len(train_df)/len(df)*100:.1f}%)")
        print(f"Val:   {len(val_df)} samples ({len(val_df)/len(df)*100:.1f}%)")
        print(f"Test:  {len(test_df)} samples ({len(test_df)/len(df)*100:.1f}%)")
        
        return train_df, val_df, test_df


if __name__ == "__main__":
    # Generate dataset
    generator = SyntheticDataGenerator(n_samples=5000, random_state=42)
    
    # Generate and split
    train_df, val_df, test_df = generator.generate_train_test_split()
    
    # Save datasets
    train_df.to_csv('../data/train_data.csv', index=False)
    val_df.to_csv('../data/val_data.csv', index=False)
    test_df.to_csv('../data/test_data.csv', index=False)
    
    print("\n" + "="*60)
    print("DATASET STATISTICS")
    print("="*60)
    
    print(f"\nDefault rates:")
    print(f"Train: {(1 - train_df['loan_repaid'].mean())*100:.2f}%")
    print(f"Val:   {(1 - val_df['loan_repaid'].mean())*100:.2f}%")
    print(f"Test:  {(1 - test_df['loan_repaid'].mean())*100:.2f}%")
    
    print(f"\nIncome distribution:")
    print(train_df['monthly_income'].describe())
    
    print(f"\nPayment regularity distribution:")
    print(train_df['overall_payment_score'].describe())
    
    print("\nDatasets ready for model training!")
