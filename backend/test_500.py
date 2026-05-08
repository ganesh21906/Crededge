import json
from fastapi.testclient import TestClient
from main import app
from datetime import datetime

client = TestClient(app)

payload = {
  "fullName": "John Doe",
  "dateOfBirth": "1990-01-01",
  "gender": "male",
  "maritalStatus": "single",
  "dependents": 0,
  "mobileNumber": "9999999999",
  "email": "test@test.com",
  "address": "123 Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "residenceType": "rented",
  "yearsAtAddress": 2,
  "employmentType": "salaried",
  "employerName": "Tech Corp",
  "monthlyIncome": 50000,
  "yearsEmployed": 3,
  "industryType": "it",
  "qualification": "bachelors",
  "loanAmount": 50000,
  "loanPurpose": "education",
  "repaymentPeriod": 6,
  "hasBankAccount": False,
  "hasUtilityBills": False,
  "hasRentalAgreement": False,
  "hasUPIHistory": False,
  "hasSocialMedia": False
}

try:
    response = client.post('/api/applications/individual', json=payload)
    print(f'STATUS: {response.status_code}')
    print(f'BODY: {response.text}')
except Exception as e:
    import traceback
    traceback.print_exc()
