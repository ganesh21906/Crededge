import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Tag, Progress, Button, Badge, Divider, Collapse, Alert, Statistic } from 'antd';
import { CheckCircleOutlined, ThunderboltOutlined, RocketOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { getEnginesStatus } from '../services/api';
import './Engines.css';

const CATEGORY_COLORS = {
  Core: '#6366f1',
  Risk: '#ef4444',
  Behavioral: '#8b5cf6',
  Transparency: '#0ea5e9',
  Analytics: '#14b8a6',
  Document: '#f97316',
  'Open Finance': '#22c55e',
};

const STATUS_CONFIG = {
  active: { color: 'success', label: 'Active' },
  beta:   { color: 'warning', label: 'Beta' },
};

export default function EnginesPage() {
  const navigate = useNavigate();
  const [data, setData]       = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    getEnginesStatus().then(setData).catch(() => {});
  }, []);

  const engines = data?.engines || FALLBACK_ENGINES;

  return (
    <div className="engines-page">
      {/* ── Hero ── */}
      <div className="engines-hero">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="engines-hero-content"
        >
          <div className="engines-hero-badge">
            <ThunderboltOutlined /> 7-Engine Decision Pipeline
          </div>
          <h1 className="engines-hero-title">
            AI Credit Intelligence
          </h1>
          <p className="engines-hero-sub">
            The most comprehensive alternative credit assessment system for unbanked and underserved populations.
            Each engine provides a unique signal — together they create a 360° credit profile.
          </p>
          <Row justify="center" gutter={32} style={{ marginTop: 24 }}>
            {[
              { label: 'Max Score Boost', value: '+475 pts' },
              { label: 'Score Range', value: '300–975' },
              { label: 'Engines Active', value: '7/7' },
              { label: 'Processing Time', value: '< 1 sec' },
            ].map((s) => (
              <Col key={s.label}>
                <div className="engines-stat">
                  <div className="engines-stat-value">{s.value}</div>
                  <div className="engines-stat-label">{s.label}</div>
                </div>
              </Col>
            ))}
          </Row>
        </motion.div>
      </div>

      <div className="engines-body">
        {/* ── Pipeline Visual ── */}
        <Card className="pipeline-card" bordered={false}>
          <h2 style={{ textAlign: 'center', marginBottom: 24 }}>🔄 How the 7-Engine Pipeline Works</h2>
          <div className="pipeline-flow">
            {['Form Submit', 'Rule Engine', 'Fraud Check', 'SHAP Waterfall', 'Peer Benchmark', '+ Optional Engines', 'Final Score'].map((step, i, arr) => (
              <React.Fragment key={step}>
                <div className={`pipeline-step ${i === 0 ? 'start' : i === arr.length - 1 ? 'end' : ''}`}>
                  {step}
                </div>
                {i < arr.length - 1 && <div className="pipeline-arrow">→</div>}
              </React.Fragment>
            ))}
          </div>
          <p style={{ textAlign: 'center', color: '#6b7280', marginTop: 16, fontSize: '0.9rem' }}>
            Optional engines (Psychometric, Bank Statement, OCR, AA) can be added at any time to boost the score
          </p>
        </Card>

        {/* ── Engine Cards ── */}
        <Row gutter={[20, 20]} style={{ marginTop: 24 }}>
          {engines.map((engine, idx) => (
            <Col xs={24} md={12} lg={8} key={engine.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.07 }}
                whileHover={{ y: -4 }}
              >
                <Card
                  bordered={false}
                  className={`engine-card ${selected === engine.id ? 'selected' : ''}`}
                  style={{ borderTop: `4px solid ${CATEGORY_COLORS[engine.category] || '#6366f1'}` }}
                  onClick={() => setSelected(selected === engine.id ? null : engine.id)}
                >
                  <div className="engine-card-header">
                    <span className="engine-card-icon">{engine.icon}</span>
                    <div className="engine-card-meta">
                      <div className="engine-card-name">{engine.name}</div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        <Tag color={CATEGORY_COLORS[engine.category]} style={{ fontSize: '10px' }}>
                          {engine.category}
                        </Tag>
                        <Badge status={STATUS_CONFIG[engine.status]?.color} text={STATUS_CONFIG[engine.status]?.label} />
                        {engine.auto !== undefined && (
                          <Tag color={engine.auto ? 'blue' : 'purple'} style={{ fontSize: '10px' }}>
                            {engine.auto ? '⚡ Auto' : '👤 Optional'}
                          </Tag>
                        )}
                      </div>
                    </div>
                  </div>

                  <p className="engine-card-desc">{engine.description}</p>

                  {engine.maxBonus > 0 && (
                    <div className="engine-bonus-bar">
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontSize: '12px', color: '#6b7280' }}>Max Score Contribution</span>
                        <strong style={{ color: CATEGORY_COLORS[engine.category] }}>+{engine.maxBonus} pts</strong>
                      </div>
                      <Progress
                        percent={Math.round(engine.maxBonus / 475 * 100)}
                        strokeColor={CATEGORY_COLORS[engine.category]}
                        size="small"
                        showInfo={false}
                      />
                    </div>
                  )}

                  {engine.maxPenalty && (
                    <div style={{ marginTop: 8, fontSize: '12px', color: '#ef4444' }}>
                      ⚠️ Penalty for anomalies: up to {engine.maxPenalty} pts
                    </div>
                  )}

                  {/* Requirements — expanded */}
                  {selected === engine.id && engine.requirements && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      style={{ marginTop: 12 }}
                    >
                      <Divider style={{ margin: '12px 0' }} />
                      <div style={{ fontSize: '12px', fontWeight: 600, color: '#374151', marginBottom: 8 }}>
                        ✅ Requirements & Points
                      </div>
                      {engine.requirements.map((req) => (
                        <div key={req.signal} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #f3f4f6' }}>
                          <span style={{ fontSize: '12px', color: '#6b7280' }}>{req.signal}</span>
                          <Tag color={req.points.startsWith('+') ? 'green' : 'default'} style={{ fontSize: '10px' }}>
                            {req.points}
                          </Tag>
                        </div>
                      ))}
                      {engine.id === 'psychometric' && (
                        <Button
                          type="primary"
                          size="small"
                          block
                          style={{ marginTop: 12 }}
                          onClick={(e) => { e.stopPropagation(); navigate('/psychometric/demo'); }}
                        >
                          Try Sample Quiz →
                        </Button>
                      )}
                    </motion.div>
                  )}

                  <div style={{ marginTop: 8, fontSize: '11px', color: '#9ca3af', textAlign: 'right' }}>
                    {selected === engine.id ? '▲ Click to collapse' : '▼ Click for requirements'}
                  </div>
                </Card>
              </motion.div>
            </Col>
          ))}
        </Row>

        {/* ── Score Architecture Table ── */}
        <Card bordered={false} className="arch-table-card" style={{ marginTop: 32 }}>
          <h2 style={{ margin: '0 0 20px' }}>🏆 Score Tiers — What Score Gets What Loan</h2>
          <div className="score-arch-table">
            <div className="sat-header">
              <div>Score Range</div>
              <div>Risk Tier</div>
              <div>Interest Rate</div>
              <div>Individual Max</div>
              <div>SME Max</div>
              <div>Decision</div>
            </div>
            {[
              { range: '850–975', tier: 'Excellent', color: '#10b981', rate: '10.5% p.a.', ind: '₹5,00,000', sme: '₹25,00,000', decision: 'Auto-Approved' },
              { range: '750–849', tier: 'Good',      color: '#3b82f6', rate: '12.5% p.a.', ind: '₹3,50,000', sme: '₹18,00,000', decision: 'Approved' },
              { range: '650–749', tier: 'Fair',      color: '#f59e0b', rate: '15.0% p.a.', ind: '₹2,00,000', sme: '₹12,00,000', decision: 'Under Review' },
              { range: '300–649', tier: 'Poor',      color: '#ef4444', rate: '18.0% p.a.', ind: '₹1,00,000', sme: '₹8,00,000',  decision: 'Extra Review' },
            ].map((row) => (
              <div key={row.tier} className="sat-row">
                <div style={{ fontWeight: 700, color: row.color }}>{row.range}</div>
                <div><Tag color={row.color} style={{ fontWeight: 700 }}>{row.tier}</Tag></div>
                <div style={{ fontWeight: 600 }}>{row.rate}</div>
                <div style={{ fontWeight: 600 }}>{row.ind}</div>
                <div style={{ fontWeight: 600 }}>{row.sme}</div>
                <div><Tag color={row.color === '#10b981' ? 'success' : row.color === '#ef4444' ? 'error' : 'warning'}>{row.decision}</Tag></div>
              </div>
            ))}
          </div>

          <Alert
            style={{ marginTop: 20 }}
            type="info"
            message="How to move from Poor to Excellent"
            description={
              <div>
                Start at 500 (baseline) → Complete Psychometric Quiz (+60) → Upload Bank Statement (+up to 120) →
                Upload ITR + Utility Bill (+up to 80) → Connect Account Aggregator (+up to 100) = potential total: <strong>860+ (Excellent)</strong>
              </div>
            }
            showIcon
          />
        </Card>

        {/* ── CTA ── */}
        <div className="engines-cta">
          <h2>Ready to get your AI Credit Assessment?</h2>
          <p>Our 7-engine pipeline gives credit to those the traditional system ignores</p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button type="primary" size="large" icon={<RocketOutlined />} onClick={() => navigate('/individual')}>
              Apply as Individual
            </Button>
            <Button size="large" onClick={() => navigate('/sme')}>Apply as SME Business</Button>
            <Button size="large" onClick={() => navigate('/track')}>Track Application</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Fallback data if API is unavailable
const FALLBACK_ENGINES = [
  { id: 'rule_engine', name: 'Rule-Based Scoring Engine', icon: '⚡', status: 'active', category: 'Core', description: 'Deterministic scoring using 5 weighted factors: payment history, income stability, alternative data, employment, and debt burden.', maxBonus: 475, auto: true, requirements: [] },
  { id: 'fraud_detection', name: 'Fraud & Anomaly Detection', icon: '🛡️', status: 'active', category: 'Risk', description: 'Multi-layer fraud analysis including income-lifestyle mismatch, round-number heuristics, and DTI validation.', maxBonus: 0, maxPenalty: -50, auto: true, requirements: [] },
  { id: 'psychometric', name: 'Psychometric Assessment', icon: '🧠', status: 'active', category: 'Behavioral', description: '15-question behavioral assessment. Financial IQ + Future Orientation + Risk Attitude + Integrity.', maxBonus: 60, auto: false, requirements: [] },
  { id: 'explainability', name: 'AI Explainability (SHAP)', icon: '📊', status: 'active', category: 'Transparency', description: 'Auto-generated waterfall showing each factor\'s exact contribution in plain language.', maxBonus: 0, auto: true, requirements: [] },
  { id: 'peer_benchmark', name: 'Peer Benchmarking', icon: '📈', status: 'active', category: 'Analytics', description: 'Compare your score against similar applicants. Shows percentile and context.', maxBonus: 0, auto: true, requirements: [] },
  { id: 'bank_statement', name: 'Bank Statement Analyzer', icon: '🏦', status: 'active', category: 'Document', description: 'Upload 6-month bank statement. Extracts income regularity, savings rate, balance level.', maxBonus: 120, auto: false, requirements: [] },
  { id: 'ocr_document', name: 'OCR Document Intelligence', icon: '📄', status: 'active', category: 'Document', description: 'Verify ITR, GST returns, utility bills, MSME certificate via AI-powered OCR.', maxBonus: 80, auto: false, requirements: [] },
  { id: 'account_aggregator', name: 'Account Aggregator (AA)', icon: '🔗', status: 'beta', category: 'Open Finance', description: 'RBI-approved consent-based real-time bank data fetching for the most accurate income verification.', maxBonus: 100, auto: false, requirements: [] },
];
