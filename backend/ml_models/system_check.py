"""
System Check - Validate ML Pipeline Installation
Run this to check if everything is set up correctly
"""

import sys
import os

def print_header(text):
    print("\n" + "="*70)
    print(text)
    print("="*70)

def check_mark(status):
    return "✅" if status else "❌"

def main():
    print_header("AI CREDIT RISK ASSESSMENT - SYSTEM CHECK")
    
    results = []
    
    # Check 1: Python Version
    print("\n[1] Checking Python Version...")
    python_version = sys.version_info
    python_ok = python_version.major == 3 and python_version.minor >= 8
    version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    print(f"    Python Version: {version_str}")
    print(f"    {check_mark(python_ok)} Python 3.8+ required, found {version_str}")
    results.append(("Python Version", python_ok))
    
    # Check 2: Required Packages
    print("\n[2] Checking Required Packages...")
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'xgboost': 'XGBoost',
        'shap': 'SHAP',
        'joblib': 'Joblib',
        'matplotlib': 'Matplotlib'
    }
    
    packages_ok = True
    for module_name, display_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"    ✅ {display_name}")
        except ImportError:
            print(f"    ❌ {display_name} - NOT INSTALLED")
            packages_ok = False
    
    results.append(("Required Packages", packages_ok))
    
    # Check 3: ML Models Directory
    print("\n[3] Checking ML Models Directory...")
    ml_dir = os.path.join(os.path.dirname(__file__))
    ml_files = [
        'feature_engineering.py',
        'generate_data.py',
        'train_model.py',
        'shap_explainer.py',
        'run_training_pipeline.py'
    ]
    
    ml_files_ok = True
    for file in ml_files:
        file_path = os.path.join(ml_dir, file)
        exists = os.path.exists(file_path)
        print(f"    {check_mark(exists)} {file}")
        if not exists:
            ml_files_ok = False
    
    results.append(("ML Files", ml_files_ok))
    
    # Check 4: Data Directory
    print("\n[4] Checking Data Directory...")
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    data_dir_exists = os.path.exists(data_dir)
    print(f"    {check_mark(data_dir_exists)} Data directory: {data_dir}")
    results.append(("Data Directory", data_dir_exists))
    
    # Check 5: Trained Model
    print("\n[5] Checking Trained Model...")
    model_path = os.path.join(data_dir, 'credit_risk_xgboost_v1.pkl')
    model_exists = os.path.exists(model_path)
    if model_exists:
        model_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        print(f"    ✅ Trained model found: {model_size:.2f} MB")
    else:
        print(f"    ⚠️  Trained model not found")
        print(f"    Run: python run_training_pipeline.py")
    results.append(("Trained Model", model_exists))
    
    # Check 6: Training Data
    print("\n[6] Checking Training Data...")
    data_files = ['train_data.csv', 'val_data.csv', 'test_data.csv']
    data_exists = all(os.path.exists(os.path.join(data_dir, f)) for f in data_files)
    if data_exists:
        print(f"    ✅ Training data found")
        for f in data_files:
            size = os.path.getsize(os.path.join(data_dir, f)) / (1024 * 1024)
            print(f"       - {f}: {size:.2f} MB")
    else:
        print(f"    ⚠️  Training data not found")
        print(f"    Run: python run_training_pipeline.py")
    results.append(("Training Data", data_exists))
    
    # Check 7: Test Imports
    print("\n[7] Testing ML Module Imports...")
    import_ok = True
    try:
        from feature_engineering import AlternativeDataFeatureEngineering
        print(f"    ✅ feature_engineering imported successfully")
    except Exception as e:
        print(f"    ❌ feature_engineering import failed: {e}")
        import_ok = False
    
    try:
        from generate_data import SyntheticDataGenerator
        print(f"    ✅ generate_data imported successfully")
    except Exception as e:
        print(f"    ❌ generate_data import failed: {e}")
        import_ok = False
    
    try:
        from train_model import CreditRiskModel
        print(f"    ✅ train_model imported successfully")
    except Exception as e:
        print(f"    ❌ train_model import failed: {e}")
        import_ok = False
    
    results.append(("Module Imports", import_ok))
    
    # Check 8: Backend API Files
    print("\n[8] Checking Backend API Files...")
    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    api_files = ['app.py', 'app_ml_integrated.py', 'requirements.txt']
    api_files_ok = all(os.path.exists(os.path.join(backend_dir, f)) for f in api_files)
    for f in api_files:
        exists = os.path.exists(os.path.join(backend_dir, f))
        print(f"    {check_mark(exists)} {f}")
    results.append(("Backend Files", api_files_ok))
    
    # Summary
    print_header("SYSTEM CHECK SUMMARY")
    
    all_ok = all(status for _, status in results)
    
    for check_name, status in results:
        print(f"  {check_mark(status)} {check_name}")
    
    print("\n" + "="*70)
    
    if all_ok:
        print("✅ ALL CHECKS PASSED - System is ready!")
        print("\nNext steps:")
        if not model_exists:
            print("  1. Train model: python run_training_pipeline.py")
        print("  2. Start backend: cd .. && python app_ml_integrated.py")
        print("  3. Start frontend: cd ../../frontend && npm start")
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues above")
        print("\nTo fix issues:")
        if not packages_ok:
            print("  • Install packages: cd .. && pip install -r requirements.txt")
        if not model_exists:
            print("  • Train model: python run_training_pipeline.py")
    
    print("="*70 + "\n")
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
