"""
Crededge — Pydantic Schemas (v2 — 7-Engine)
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


# ── Request Schemas ───────────────────────────────────────────

class IndividualApplication(BaseModel):
    fullName: str
    dateOfBirth: Optional[str] = None
    gender: str
    maritalStatus: str
    dependents: int = 0
    mobileNumber: str
    email: str
    address: str
    city: str
    state: str
    pincode: str
    residenceType: str
    yearsAtAddress: float = 0
    employmentType: str
    employerName: Optional[str] = None
    monthlyIncome: float
    yearsEmployed: Optional[float] = None
    industryType: Optional[str] = None
    qualification: str
    hasBankAccount: bool = False
    bankName: Optional[str] = None
    accountType: Optional[str] = None
    averageBalance: Optional[float] = None
    hasUtilityBills: bool = False
    hasRentalAgreement: bool = False
    hasUPIHistory: bool = False
    hasSocialMedia: bool = False
    loanAmount: float
    loanPurpose: str
    repaymentPeriod: int = 12


class SMEApplication(BaseModel):
    businessName: str
    businessType: str
    registrationType: str
    yearOfEstablishment: int
    gstNumber: Optional[str] = None
    panNumber: str
    industryType: str
    numberOfEmployees: str
    ownerName: str
    designation: str
    mobileNumber: str
    email: str
    address: str
    city: str
    state: str
    pincode: str
    annualRevenue: float
    monthlyRevenue: float
    averageMonthlyProfit: float
    hasGSTReturns: bool = False
    hasITReturns: bool = False
    hasBankAccount: bool = False
    bankName: Optional[str] = None
    accountType: Optional[str] = None
    averageBalance: Optional[float] = None
    monthlyTransactions: Optional[int] = None
    hasBusinessWebsite: bool = False
    websiteUrl: Optional[str] = None
    hasDigitalPresence: bool = False
    socialMediaLinks: Optional[str] = None
    hasUtilityBills: bool = False
    hasRentalAgreement: bool = False
    customerBase: Optional[str] = None
    supplierCount: Optional[str] = None
    hasInventory: bool = False
    inventoryValue: Optional[float] = None
    loanAmount: float
    loanPurpose: str
    repaymentPeriod: int = 12


class AdminActionRequest(BaseModel):
    action: str
    note: Optional[str] = None


class PsychometricSubmission(BaseModel):
    applicationId: str
    responses: dict  # {question_id: answer_index}


# ── Inner Schemas ─────────────────────────────────────────────

class ScoreFactor(BaseModel):
    name: str
    score: int
    weight: int
    description: str


class CoachTip(BaseModel):
    icon: str
    title: str
    tip: str
    impact: str
    timeframe: str


class WaterfallItem(BaseModel):
    factor: str
    contribution: int
    direction: str
    explanation: str
    category: str


# ── Response Schemas ──────────────────────────────────────────

class ApplicationResponse(BaseModel):
    applicationId: str
    applicationType: str
    applicantName: str
    loanAmount: str
    submittedAt: str
    status: str = "success"
    creditScore: int
    riskCategory: str
    approvalStatus: str
    interestRate: str
    maxLoanEligible: str
    aiConfidence: float
    modelUsed: str
    factors: List[ScoreFactor] = []
    strengths: List[str] = []
    improvements: List[str] = []
    recommendations: List[str] = []
    coachTips: List[CoachTip] = []
    # Engine results
    fraudRisk: str = "Low"
    fraudFlags: List[str] = []
    shapWaterfall: List[WaterfallItem] = []
    peerBenchmark: Optional[dict] = None
    engineContributions: dict = {}


class ApplicationSummary(BaseModel):
    id: str
    applicationType: str
    applicantName: str
    email: Optional[str]
    phone: Optional[str]
    loanAmount: str
    loanAmountRaw: float
    loanPurpose: Optional[str]
    creditScore: int
    riskCategory: str
    approvalStatus: str
    interestRate: str
    maxLoanEligible: str
    status: str
    aiConfidence: float
    modelUsed: Optional[str]
    submittedAt: Optional[str]
    reviewedAt: Optional[str]
    reviewedBy: Optional[str]
    factors: List[ScoreFactor] = []
    strengths: List[str] = []
    improvements: List[str] = []
    recommendations: List[str] = []
    coachTips: List[CoachTip] = []
    # Engine fields
    fraudRisk: str = "Low"
    fraudFlags: List[str] = []
    fraudScore: int = 100
    psychometricScore: Optional[int] = None
    psychometricBonus: int = 0
    psychometricCompleted: bool = False
    shapWaterfall: List[WaterfallItem] = []
    peerPercentile: Optional[float] = None
    peerAvgScore: Optional[int] = None
    peerCount: Optional[int] = None
    peerGroupLabel: Optional[str] = None
    bankStatementUploaded: bool = False
    bankStatementScore: Optional[int] = None
    bankStatementBonus: int = 0
    ocrDocsVerified: int = 0
    ocrBonus: int = 0
    aaVerified: bool = False
    aaBonus: int = 0
    engineContributions: dict = {}


class ApplicationListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    applications: List[ApplicationSummary]


class AdminStatsResponse(BaseModel):
    totalApplications: int
    approvedApplications: int
    pendingApplications: int
    rejectedApplications: int
    averageScore: int
    totalDisbursed: str
    approvalRate: float
    avgProcessingTime: str
    individualCount: int
    smeCount: int
    riskDistribution: dict
    # Engine-specific stats
    fraudHighCount: int = 0
    fraudMediumCount: int = 0
    psychometricCompletedCount: int = 0
    bankStatementCount: int = 0
    aaVerifiedCount: int = 0
    enginePerformance: dict = {}
