"""
Updated Pydantic Models with Verification Data Support
Phase 1: Add optional verification fields
"""

from pydantic import BaseModel
from typing import Optional, List


# Verification data models
class UtilityBillVerification(BaseModel):
    electricityConsumerNumber: Optional[str] = None
    electricityProvider: Optional[str] = None
    gasConsumerNumber: Optional[str] = None
    waterConsumerNumber: Optional[str] = None


class RentalVerification(BaseModel):
    landlordMobile: Optional[str] = None
    monthlyRent: Optional[float] = None
    rentalAgreementNumber: Optional[str] = None


class UPIVerification(BaseModel):
    upiId: Optional[str] = None
    consentToken: Optional[str] = None  # For Account Aggregator


class EmploymentVerification(BaseModel):
    epfoUAN: Optional[str] = None
    linkedInProfile: Optional[str] = None
    employerEmail: Optional[str] = None


class GSTVerification(BaseModel):
    gstin: Optional[str] = None
    gstUsername: Optional[str] = None


# Main application models
class IndividualApplication(BaseModel):
    # Personal Information
    fullName: str
    dateOfBirth: str
    gender: str
    maritalStatus: str
    dependents: int
    mobileNumber: str
    email: str
    
    # Address Information
    address: str
    city: str
    state: str
    pincode: str
    residenceType: str
    yearsAtAddress: float
    
    # Employment Information
    employmentType: str
    employerName: Optional[str] = None
    monthlyIncome: float
    yearsEmployed: Optional[float] = None
    industryType: Optional[str] = None
    
    # Education
    qualification: str
    
    # Banking Information
    hasBankAccount: bool
    bankName: Optional[str] = None
    accountType: Optional[str] = None
    averageBalance: Optional[float] = None
    
    # Alternative Data (Checkboxes)
    hasUtilityBills: bool
    hasRentalAgreement: bool
    hasUPIHistory: bool
    hasSocialMedia: bool
    
    # Loan Details
    loanAmount: float
    loanPurpose: str
    repaymentPeriod: int
    
    # NEW: Verification Data (Phase 1)
    utilityVerification: Optional[UtilityBillVerification] = None
    rentalVerification: Optional[RentalVerification] = None
    upiVerification: Optional[UPIVerification] = None
    employmentVerification: Optional[EmploymentVerification] = None


class SMEApplication(BaseModel):
    # Business Information
    businessName: str
    businessType: str
    registrationType: str
    yearOfEstablishment: int
    gstNumber: Optional[str] = None
    panNumber: str
    industryType: str
    numberOfEmployees: str
    
    # Owner Information
    ownerName: str
    designation: str
    mobileNumber: str
    email: str
    
    # Address
    address: str
    city: str
    state: str
    pincode: str
    
    # Financial Information
    annualRevenue: float
    monthlyRevenue: float
    averageMonthlyProfit: float
    
    # Alternative Data
    hasGSTReturns: bool
    hasITReturns: bool
    hasBankAccount: bool
    bankName: Optional[str] = None
    accountType: Optional[str] = None
    averageBalance: Optional[float] = None
    monthlyTransactions: Optional[int] = None
    
    # Digital Presence
    hasBusinessWebsite: bool
    websiteUrl: Optional[str] = None
    hasDigitalPresence: bool
    socialMediaLinks: Optional[str] = None
    
    # Additional Data
    hasUtilityBills: bool
    hasRentalAgreement: bool
    customerBase: Optional[str] = None
    supplierCount: Optional[str] = None
    hasInventory: bool
    inventoryValue: Optional[float] = None
    
    # Loan Details
    loanAmount: float
    loanPurpose: str
    repaymentPeriod: int
    
    # NEW: Verification Data (Phase 1)
    gstVerification: Optional[GSTVerification] = None
    utilityVerification: Optional[UtilityBillVerification] = None
    rentalVerification: Optional[RentalVerification] = None


class CreditScoreResponse(BaseModel):
    applicationId: str
    applicationType: str
    creditScore: int
    riskCategory: str
    approvalStatus: str
    interestRate: str
    maxLoanEligible: str
    factors: List[dict]
    strengths: List[str]
    improvements: List[str]
    recommendations: List[str]
    
    # NEW: Verification status (Phase 1)
    verificationStatus: Optional[dict] = None
    dataQuality: Optional[dict] = None
