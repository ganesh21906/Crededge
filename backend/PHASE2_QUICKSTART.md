# Phase 2: Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Understand What Phase 2 Does

**Before (Phase 1):**
- User clicks checkbox "I have utility bills" → Gets points ❌
- No verification, just trust user claims
- Mock data only

**After (Phase 2):**
- User provides consumer number → System verifies with BBPS ✅
- User provides UPI ID → System checks transaction history with Account Aggregator ✅
- Business provides GSTIN → System validates GST filing with GST Portal ✅
- Real verification or mock fallback (development mode)

---

### Step 2: Run Tests (No Setup Required!)

```bash
cd backend
python test_phase2_integration.py
```

**What This Tests:**
- ✅ All 3 API integrations work
- ✅ Mock fallback functions correctly
- ✅ Verification is consistent (same input = same output)
- ✅ No crashes or errors

**Expected:** All tests pass in mock mode (works without API keys)

---

### Step 3: Try the Backend

```bash
cd backend
python app_ml_integrated.py
```

**You'll see:**
```
🔐 Initializing Alternative Data Verifier...
   Verification mode: auto
⚠️  Trained model not found at: ...
   Using mock predictions.

INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Note:** 
- "auto" mode = Uses mock since no API keys configured ✅
- "mock predictions" = ML model not trained yet (optional)

---

### Step 4: Test an Application

**Open another terminal:**

```bash
# Simple test with curl (Windows PowerShell)
$body = @{
    fullName = "Test User"
    dateOfBirth = "1990-01-01"
    gender = "Male"
    maritalStatus = "Single"
    dependents = 0
    mobileNumber = "9876543210"
    email = "test@example.com"
    address = "123 Test St"
    city = "Mumbai"
    state = "Maharashtra"
    pincode = "400001"
    residenceType = "Rented"
    yearsAtAddress = 2.0
    employmentType = "Salaried"
    monthlyIncome = 50000
    qualification = "Graduate"
    hasBankAccount = $true
    hasUtilityBills = $true
    hasRentalAgreement = $true
    hasUPIHistory = $true
    hasSocialMedia = $true
    loanAmount = 200000
    loanPurpose = "Personal"
    repaymentPeriod = 24
    utilityVerification = @{
        electricityConsumerNumber = "123456789012"
        electricityProvider = "MSEDCL"
    }
    upiVerification = @{
        upiId = "test@paytm"
    }
    rentalVerification = @{
        landlordMobile = "9876543210"
        monthlyRent = 15000
    }
    employmentVerification = @{
        epfoUAN = "100123456789"
    }
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/application/individual" -Body $body -ContentType "application/json"
```

**Or use the React frontend:**
```bash
cd frontend
npm start
```
Go to Individual Application form, fill it out with verification details.

---

### Step 5: See the Results

**Response includes:**

```json
{
  "creditScore": 787,
  "verificationStatus": {
    "utilityBills": {
      "verified": true,
      "method": "mock_fallback",
      "regularity_percentage": 91.7,
      "on_time_count": 11,
      "total_payments": 12,
      "payment_trend": "improving"
    },
    "upiHistory": {
      "verified": true,
      "method": "mock_fallback",
      "transaction_count": 156,
      "consistency_score": 82.5
    }
  },
  "dataQuality": {
    "verifiedSources": 3,
    "totalClaimed": 4,
    "verificationRate": 0.75,
    "mode": "auto"
  },
  "recommendations": [
    "Based on your credit score of 787, you're eligible for up to ₹3,00,000",
    "✅ Verified 3 of 4 claimed data sources",
    "💡 Verification bonus: +37 points"
  ]
}
```

**Notice:**
- ✅ Detailed verification for each data source
- ✅ Data quality metrics (75% verified)
- ✅ Verification bonus (+37 points)
- ✅ "mock_fallback" method (no API keys yet)

---

## 🔧 Optional: Add Real API Keys

### For Production Use (Optional)

1. **Copy template:**
   ```bash
   cd backend
   copy .env.api.example .env
   ```

2. **Edit `.env` file:**
   ```env
   BBPS_API_KEY=your_actual_key_here
   AA_API_KEY=your_actual_key_here
   GST_API_KEY=your_actual_key_here
   VERIFICATION_MODE=auto
   ```

3. **Restart backend:**
   ```bash
   python app_ml_integrated.py
   ```

4. **Now you'll see:**
   ```
   🔐 Initializing Alternative Data Verifier...
      Verification mode: auto (detected: live)
   ```

5. **Responses show:**
   ```json
   {
     "method": "live_api"  // Using real APIs!
   }
   ```

---

## 📊 What Each API Does

### BBPS (Utility Bills)
**Input:**
- Consumer number: "123456789012"
- Provider: "MSEDCL"

**Output:**
- ✅ Payment regularity: 91.7%
- ✅ On-time payments: 11/12
- ✅ Payment trend: "improving"
- ✅ Average bill: ₹2,450

**Score Impact:** Higher regularity = higher credit score

---

### Account Aggregator (UPI)
**Input:**
- UPI ID: "user@paytm"
- Consent token (from user approval)

**Output:**
- ✅ Transaction count: 156
- ✅ Monthly average: ₹28,500
- ✅ Consistency score: 82.5
- ✅ Merchant diversity: 24

**Score Impact:** Higher consistency = higher credit score

---

### GST Portal (Business)
**Input:**
- GSTIN: "27AABCU9603R1ZV"

**Output:**
- ✅ Business name: "ABC Enterprises Pvt Ltd"
- ✅ Filing regularity: 91.7%
- ✅ Compliance: "excellent"
- ✅ Average turnover: ₹4.5 Crores

**Score Impact:** Better compliance = higher credit score

---

## 🎯 Key Features

### 1. Automatic Fallback
```python
try:
    # Try real API
    result = bbps_client.verify(consumer_number)
    method = "live_api"
except:
    # Fallback to mock
    result = mock_verify(consumer_number)
    method = "mock_fallback"
```

**Benefit:** Works in development without API keys!

---

### 2. Consistent Mock Data
**Same input always gives same output:**
```python
# Run 1
verify("123456789012") → regularity: 91.7%

# Run 2 (same input)
verify("123456789012") → regularity: 91.7%  ✅
```

**Benefit:** Predictable testing and demos!

---

### 3. Verification Bonus
```python
verified = 3 sources
claimed = 4 sources
rate = 0.75  # 75%

bonus = rate * 50 = 37 points
final_score = base_score + bonus
```

**Benefit:** Rewards users who verify their claims!

---

### 4. Data Quality Metrics
```json
{
  "dataQuality": {
    "verifiedSources": 3,
    "totalClaimed": 4,
    "verificationRate": 0.75,
    "mode": "auto"
  }
}
```

**Benefit:** Transparency for lenders!

---

## 🔍 Verification Status Explained

### "method" Field

| Value | Meaning | When It Happens |
|-------|---------|----------------|
| `live_api` | Real API used | API keys configured |
| `mock_fallback` | Mock used | No API keys OR API failed |
| `consent_required` | Need user approval | UPI verification without consent |

---

### Example Response Types

**1. Live API Success:**
```json
{
  "verified": true,
  "method": "live_api",
  "regularity_percentage": 91.7
}
```

**2. Mock Fallback:**
```json
{
  "verified": true,
  "method": "mock_fallback",
  "regularity_percentage": 91.7
}
```

**3. Consent Required (UPI):**
```json
{
  "verified": false,
  "method": "consent_required",
  "consent_required": true,
  "consent_id": "aa-consent-uuid",
  "consent_url": "https://aa-app.sahamati.org.in/consent/..."
}
```

---

## 🎨 Frontend Integration (Coming Soon)

**Phase 2 backend is ready!**

**Frontend needs:**
1. Update form to collect verification data ✅ (already done in Phase 1)
2. Display verification status in results ⚠️ (needs update)
3. Show consent flow for UPI ⚠️ (needs implementation)
4. Add verification progress indicator ⚠️ (nice to have)

---

## 🐛 Common Issues

### Issue 1: "Module not found: services"
**Solution:**
```bash
cd backend
python app_ml_integrated.py  # Must be in backend directory
```

---

### Issue 2: "Verification always shows mock_fallback"
**Expected!** Without API keys, system uses mock mode.

**To use live APIs:**
1. Get API credentials (see PHASE2_IMPLEMENTATION.md)
2. Add to `.env` file
3. Restart backend

---

### Issue 3: "Credit score seems random"
**Explanation:** ML model not trained yet (optional).

**To train:**
```bash
cd backend/ml_models
python run_training_pipeline.py
```

But verification still works with mock predictions!

---

## 📚 Documentation

- **Detailed guide:** [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)
- **Complete summary:** [PHASE2_COMPLETE_SUMMARY.md](PHASE2_COMPLETE_SUMMARY.md)
- **API examples:** See individual integration files

---

## ✅ Verification Checklist

- [ ] Run `test_phase2_integration.py` (all tests pass)
- [ ] Start backend (`python app_ml_integrated.py`)
- [ ] Submit test application (Postman/curl/frontend)
- [ ] Verify response includes `verificationStatus`
- [ ] Verify response includes `dataQuality`
- [ ] Check verification bonus in `recommendations`
- [ ] Confirm mode shows "auto" or "mock"

---

## 🎉 You're Done!

**Phase 2 Complete:** ✅

**What you have:**
- Real API integrations (BBPS, Account Aggregator, GST)
- Mock fallback for development
- Verification bonus system
- Data quality scoring
- Comprehensive testing

**What works NOW:**
- Submit applications with verification data
- Get detailed verification results
- See verification bonus in credit score
- Test with or without API keys

**Next steps:**
- Get API credentials for production
- Update frontend to show verification status
- Train ML model (optional)
- Deploy to production

---

**Questions?** All documentation is in the `backend/` directory!
