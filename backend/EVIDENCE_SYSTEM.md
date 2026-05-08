# Evidence-Based Verification System

## Overview

This hybrid approach allows users to upload evidence now and integrate with live government APIs later:

1. **Phase 2 (Current)**: Accept evidence uploads + mock verification
2. **Phase 3 (Future)**: Compare uploaded evidence against live API data
3. **Phase 4 (Later)**: Fully automated live API verification

---

## Evidence Types

### Individual Applications

- **utility_bill**: Screenshot/PDF of electricity bill (shows consumer number, bill amount, payment history)
- **upi_statement**: PDF/screenshot of UPI transaction history from 3-6 months
- **rental_agreement**: PDF of rental agreement or proof of rent payment
- **employment_letter**: Employment certificate or recent payslip

### SME Applications

- **utility_bill**: Business utility bill (electricity, water, internet)
- **gst_filing**: GST return filing confirmation from portal
- **bank_statement**: Recent business bank statements (3-6 months)
- **employment_letter**: Business registration or partnership deed

---

## API Endpoints

### 1. Upload Evidence

**POST** `/api/evidence/upload/{application_id}`

Upload a document for an application.

**Query Parameters:**
- `evidence_type` (string): Type of evidence being uploaded
- `file` (binary): File upload (max 10MB)

**Example:**
```bash
curl -X POST http://localhost:8000/api/evidence/upload/IND-12345?evidence_type=utility_bill \
  -F "file=@electricity_bill.pdf"
```

**Response:**
```json
{
  "status": "success",
  "message": "Evidence uploaded successfully",
  "applicationId": "IND-12345",
  "evidenceType": "utility_bill",
  "fileId": "a1b2c3d4",
  "fileName": "utility_bill_a1b2c3d4.pdf",
  "uploadedAt": "2026-01-07T10:30:45.123456"
}
```

---

### 2. Get Evidence Summary

**GET** `/api/evidence/{application_id}`

Get all evidence files uploaded for an application.

**Response:**
```json
{
  "applicationId": "IND-12345",
  "totalFiles": 3,
  "evidenceTypes": ["utility_bill", "upi_statement", "rental_agreement"],
  "totalSizeBytes": 2457600,
  "files": [
    {
      "evidenceType": "utility_bill",
      "filename": "utility_bill_a1b2c3d4.pdf",
      "fileSizeBytes": 512000,
      "uploadedTimestamp": "2026-01-07T10:30:45.123456"
    },
    {
      "evidenceType": "upi_statement",
      "filename": "upi_statement_b2c3d4e5.pdf",
      "fileSizeBytes": 1024000,
      "uploadedTimestamp": "2026-01-07T10:31:15.654321"
    },
    {
      "evidenceType": "rental_agreement",
      "filename": "rental_agreement_c3d4e5f6.pdf",
      "fileSizeBytes": 921600,
      "uploadedTimestamp": "2026-01-07T10:32:00.111111"
    }
  ]
}
```

---

### 3. Check Evidence Completeness

**GET** `/api/evidence/{application_id}/check?application_type=Individual`

Check if all required evidence is uploaded.

**Query Parameters:**
- `application_type` (string): "Individual" or "SME"

**Response:**
```json
{
  "applicationId": "IND-12345",
  "applicationType": "Individual",
  "requiredEvidence": [
    "utility_bill",
    "upi_statement",
    "rental_agreement",
    "employment_letter"
  ],
  "uploadedEvidence": [
    "utility_bill",
    "upi_statement",
    "rental_agreement"
  ],
  "missingEvidence": [
    "employment_letter"
  ],
  "allRequired": false,
  "completeness": "3/4 (75%)"
}
```

---

### 4. Delete Evidence

**DELETE** `/api/evidence/{application_id}/{evidence_type}`

Delete evidence file(s) of a specific type.

**Response:**
```json
{
  "status": "success",
  "message": "Deleted 1 evidence file(s)",
  "applicationId": "IND-12345",
  "evidenceType": "utility_bill"
}
```

---

## File Storage Structure

Files are stored locally in:
```
backend/data/evidence/
├── IND-12345/
│   ├── utility_bill_a1b2c3d4.pdf
│   ├── upi_statement_b2c3d4e5.pdf
│   └── rental_agreement_c3d4e5f6.pdf
├── IND-12346/
│   ├── utility_bill_d4e5f6g7.pdf
│   └── ...
└── SME-67890/
    ├── gst_filing_e5f6g7h8.pdf
    └── ...
```

**Note:** For production, replace with cloud storage (AWS S3, Google Cloud Storage, etc.)

---

## Future Integration: Live API Comparison

Once APIs are integrated, the system will:

1. **User uploads evidence** (screenshot of electricity bill with consumer number)
2. **System stores the file** with application ID
3. **Live API verifies** the consumer number against real BBPS data
4. **System compares** uploaded evidence with API response:
   - ✅ Match: Evidence authentic
   - ⚠️ Mismatch: Flag for manual review
   - ❌ No match: Evidence likely fraudulent

**Example workflow:**
```
User uploads: utility_bill_2024_jan.pdf (consumer: 123456789)
  ↓
BBPS API verifies: consumer 123456789 exists, verified_name: "John Doe"
  ↓
Compare: Check if bill shows "John Doe" as consumer
  ↓
Result: Authentic (verified), Authentic (unverified), or Suspicious
```

---

## Three-Phase Implementation

### Phase 2 (Current)
- ✅ Upload evidence documents
- ✅ Store with application ID
- ✅ Track completeness
- ✅ Mock verification (doesn't check uploads)

### Phase 3 (Next)
- API integration with BBPS, AA, GST
- **Compare uploaded evidence with API data**
- Flag mismatches for review
- Calculate authenticity score

### Phase 4 (Future)
- Fully automated verification
- AI-powered document analysis (OCR, face detection)
- Fraud detection
- API-only verification (uploads optional)

---

## Implementation Guide

### Backend Setup (Already Done ✅)

1. Evidence manager service created
2. Upload endpoints added to API
3. File storage system ready

### Frontend Integration (TODO)

Add to Individual/SME forms:

```jsx
<section>
  <h3>Upload Evidence Documents</h3>
  
  {/* Utility Bill */}
  <FileUpload 
    label="Electricity Bill (PDF/Image)"
    evidenceType="utility_bill"
    applicationId={appId}
    onUpload={handleUpload}
  />
  
  {/* UPI Statement */}
  <FileUpload 
    label="UPI Transaction Statement (PDF)"
    evidenceType="upi_statement"
    applicationId={appId}
    onUpload={handleUpload}
  />
  
  {/* Rental Agreement */}
  <FileUpload 
    label="Rental Agreement or Proof (PDF)"
    evidenceType="rental_agreement"
    applicationId={appId}
    onUpload={handleUpload}
  />
  
  {/* Progress Indicator */}
  <EvidenceProgress 
    applicationId={appId}
    applicationType="Individual"
  />
</section>
```

---

## Benefits

### For Users
- 📱 Easy document upload during application
- 📊 Track upload progress
- 🔄 Can update documents later
- ✅ Proof of claims

### For Lenders
- 📁 Audit trail of all evidence
- 🔍 Manual review capability before automation
- 🤖 Later: Compare against APIs for fraud detection
- 💾 Compliance: Document retention

### For System
- 🎯 Phased rollout without breaking changes
- 🔄 Easy migration from manual to automated
- 📈 Build confidence in automated verification
- 🛡️ Fraud detection layer

---

## Security Notes

1. **File Validation**: Check MIME type, file size, virus scan
2. **Encryption**: Store files with encryption at rest
3. **Access Control**: Only authorized staff can view evidence
4. **Retention**: Auto-delete after N days per compliance
5. **Cloud Storage**: Use managed services with built-in security

---

## Example Usage

### Backend Test
```bash
# Start with evidence enabled
cd backend
uvicorn app_ml_integrated:app --reload

# Upload evidence
curl -X POST http://localhost:8000/api/evidence/upload/IND-TEST-001?evidence_type=utility_bill \
  -F "file=@sample_bill.pdf"

# Check status
curl http://localhost:8000/api/evidence/IND-TEST-001

# Check completeness
curl "http://localhost:8000/api/evidence/IND-TEST-001/check?application_type=Individual"
```

---

**Ready to go live!** This system bridges the gap between immediate user verification (uploads) and future automated verification (live APIs).
