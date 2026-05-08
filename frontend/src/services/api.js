/**
 * Crededge — Centralized API Service (v2 — 7 Engines)
 * All backend communication goes through here.
 * JWT is automatically attached for protected routes.
 */

import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE_URL });

// ── JWT interceptor ────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('crededge_admin_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('crededge_admin_token');
      localStorage.removeItem('crededge_admin_user');
      if (window.location.pathname !== '/dashboard' && window.location.pathname !== '/engines') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ── Applications ───────────────────────────────────────────
export const submitIndividualApplication = (data) =>
  api.post('/api/applications/individual', data).then((r) => r.data);

export const submitSMEApplication = (data) =>
  api.post('/api/applications/sme', data).then((r) => r.data);

export const getApplicationById = (id) =>
  api.get(`/api/applications/${id}`).then((r) => r.data);

// ── Admin ──────────────────────────────────────────────────
export const adminLogin = (username, password) => {
  const body = new URLSearchParams({ username, password });
  return api.post('/api/admin/token', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  }).then((r) => r.data);
};

export const getAdminApplications = (params = {}) =>
  api.get('/api/admin/applications', { params }).then((r) => r.data);

export const reviewApplication = (id, action) =>
  api.put(`/api/admin/applications/${id}/review`, { action }).then((r) => r.data);

export const getAdminStats = () =>
  api.get('/api/admin/stats').then((r) => r.data);

// ── Engine Status ──────────────────────────────────────────
export const getEnginesStatus = () =>
  api.get('/api/engines/status').then((r) => r.data);

export const getScoreArchitecture = () =>
  api.get('/api/engines/score-architecture').then((r) => r.data);

// ── Engine 2: Psychometric ─────────────────────────────────
export const getPsychometricQuestions = () =>
  api.get('/api/engines/psychometric/questions').then((r) => r.data);

export const submitPsychometric = (applicationId, responses) =>
  api.post('/api/engines/psychometric/submit', { applicationId, responses }).then((r) => r.data);

// ── Engine 5: Bank Statement ───────────────────────────────
export const uploadBankStatement = (applicationId, file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post(`/api/engines/bank-statement/${applicationId}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data);
};

// ── Engine 6: OCR Documents ────────────────────────────────
export const uploadDocument = (applicationId, docType, file) => {
  const form = new FormData();
  form.append('doc_type', docType);
  form.append('file', file);
  return api.post(`/api/engines/documents/${applicationId}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data);
};

export const getDocumentTypes = () =>
  api.get('/api/engines/documents/types').then((r) => r.data);

// ── Engine 7: Account Aggregator ───────────────────────────
export const initiateAAConsent = (applicationId, phone) =>
  api.post(`/api/engines/aa/initiate/${applicationId}`, null, {
    params: { user_phone: phone },
  }).then((r) => r.data);

export const simulateAAApproval = (consentHandle, applicationId) =>
  api.post(`/api/engines/aa/simulate-approve/${consentHandle}`, null, {
    params: { application_id: applicationId },
  }).then((r) => r.data);

export default api;
