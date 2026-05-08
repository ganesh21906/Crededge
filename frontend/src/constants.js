// ============================================================
// Crededge — Single source of truth for all config constants
// Change values here; never hardcode in components
// ============================================================

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Score thresholds (must match backend THRESHOLD_* values)
export const SCORE_THRESHOLDS = {
  EXCELLENT: 850,
  GOOD: 750,
  FAIR: 650,
};

// Risk category metadata
export const RISK_CATEGORIES = {
  Excellent: { color: '#52c41a', antColor: 'success',  bgColor: '#f6ffed', label: 'Excellent' },
  Good:      { color: '#1890ff', antColor: 'processing', bgColor: '#e6f7ff', label: 'Good' },
  Fair:      { color: '#fa8c16', antColor: 'warning',  bgColor: '#fff7e6', label: 'Fair' },
  Poor:      { color: '#f5222d', antColor: 'error',    bgColor: '#fff1f0', label: 'Poor' },
};

// Interest rates per category (display only — backend is authoritative)
export const INTEREST_RATES = {
  Excellent: '10.5% p.a.',
  Good:      '12.5% p.a.',
  Fair:      '15.0% p.a.',
  Poor:      '18.0% p.a.',
};

// Max loan amounts (display hints on forms)
export const MAX_LOAN_INDIVIDUAL = {
  Excellent: 500000,
  Good:      350000,
  Fair:      200000,
  Poor:      100000,
};

export const MAX_LOAN_SME = {
  Excellent: 2500000,
  Good:      1800000,
  Fair:      1200000,
  Poor:       800000,
};

// Admin credentials info (username stored here for display; password NEVER)
export const ADMIN_USERNAME_HINT = 'admin';
export const ADMIN_PASSWORD_HINT = 'admin123';

// Approval status display
export const APPROVAL_STATUS_META = {
  'Approved':                   { type: 'success', icon: '✅' },
  'Under Review':               { type: 'warning', icon: '⏳' },
  'Requires Additional Review': { type: 'error',   icon: '🔍' },
};
