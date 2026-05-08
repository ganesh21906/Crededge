import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Row, Col, Card, Statistic, Table, Tag, Button, Badge,
  Progress, Alert, Tabs, Tooltip, Space, Divider, message
} from 'antd';
import {
  ThunderboltOutlined, SafetyOutlined, BrainOutlined,
  FileTextOutlined, BankOutlined, ApiOutlined, BarChartOutlined,
  CheckCircleOutlined, WarningOutlined, CloseCircleOutlined,
  RiseOutlined, TeamOutlined, DashboardOutlined, AlertOutlined,
  LineChartOutlined, PieChartOutlined
} from '@ant-design/icons';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip as RechartTooltip, Legend,
  ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, LineChart, Line
} from 'recharts';
import { getAdminStats, getAdminApplications, getScoreArchitecture } from '../services/api';
import './Dashboard.css';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];
const RISK_COLORS = { Excellent: '#10b981', Good: '#3b82f6', Fair: '#f59e0b', Poor: '#ef4444' };
const FRAUD_COLORS = { Low: '#10b981', Medium: '#f59e0b', High: '#ef4444' };

const ENGINE_META = [
  { id: 'rule_engine',       name: 'Rule-Based Scoring', icon: '⚡', color: '#6366f1', maxBonus: 475, auto: true },
  { id: 'fraud_detection',   name: 'Fraud Detection',    icon: '🛡️', color: '#ef4444', maxBonus: 0,   auto: true },
  { id: 'psychometric',      name: 'Psychometric',       icon: '🧠', color: '#8b5cf6', maxBonus: 60,  auto: false },
  { id: 'explainability',    name: 'Explainability',     icon: '📊', color: '#0ea5e9', maxBonus: 0,   auto: true },
  { id: 'peer_benchmark',    name: 'Peer Benchmark',     icon: '📈', color: '#14b8a6', maxBonus: 0,   auto: true },
  { id: 'bank_statement',    name: 'Bank Statement',     icon: '🏦', color: '#f97316', maxBonus: 120, auto: false },
  { id: 'ocr_document',      name: 'OCR / Documents',    icon: '📄', color: '#ec4899', maxBonus: 80,  auto: false },
  { id: 'account_aggregator',name: 'Account Aggregator', icon: '🔗', color: '#22c55e', maxBonus: 100, auto: false },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats]             = useState(null);
  const [applications, setApps]       = useState([]);
  const [architecture, setArch]       = useState(null);
  const [loading, setLoading]         = useState(true);
  const [activeTab, setActiveTab]     = useState('overview');

  useEffect(() => {
    loadAll();
    const interval = setInterval(loadAll, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadAll = async () => {
    try {
      const [s, arch] = await Promise.all([
        getAdminStats(),
        getScoreArchitecture(),
      ]);
      setStats(s);
      setArch(arch);

      const token = localStorage.getItem('crededge_admin_token');
      if (token) {
        const a = await getAdminApplications({ limit: 8 });
        setApps(a.applications || []);
      }
    } catch (e) {
      // Show stats even if partial failure
    } finally {
      setLoading(false);
    }
  };

  const riskData = stats ? Object.entries(stats.riskDistribution || {}).map(([name, value]) => ({ name, value })) : [];

  const engineBarData = ENGINE_META.filter(e => e.maxBonus > 0).map(e => ({
    name: e.name.split(' ')[0],
    maxBonus: e.maxBonus,
    fill: e.color,
  }));

  const columns = [
    {
      title: 'Application ID', dataIndex: 'id', key: 'id', width: 140,
      render: (id) => (
        <Button type="link" size="small" onClick={() => navigate(`/track?id=${id}`)}>
          {id}
        </Button>
      ),
    },
    { title: 'Applicant', dataIndex: 'applicantName', key: 'applicantName', width: 160,
      render: (n, r) => <><div style={{fontWeight:600}}>{n}</div><Tag color="blue" style={{fontSize:'10px'}}>{r.applicationType}</Tag></> },
    {
      title: 'Score', dataIndex: 'creditScore', key: 'creditScore', width: 80, align: 'center',
      render: (s, r) => (
        <span style={{ fontWeight: 700, fontSize: '1.1rem', color: RISK_COLORS[r.riskCategory] }}>
          {s}
        </span>
      ),
      sorter: (a, b) => a.creditScore - b.creditScore,
    },
    {
      title: 'Risk', dataIndex: 'riskCategory', key: 'riskCategory', width: 90,
      render: (r) => <Tag color={RISK_COLORS[r]}>{r}</Tag>,
    },
    {
      title: 'Fraud', dataIndex: 'fraudRisk', key: 'fraudRisk', width: 80,
      render: (f) => {
        const icon = f === 'Low' ? <CheckCircleOutlined /> : f === 'Medium' ? <WarningOutlined /> : <AlertOutlined />;
        return <Tag color={FRAUD_COLORS[f]} icon={icon}>{f}</Tag>;
      },
    },
    {
      title: 'Engines Active', key: 'engines', width: 160,
      render: (_, r) => (
        <Space size={2} wrap>
          {r.psychometricCompleted && <Tooltip title="Psychometric ✓"><Tag color="purple" style={{fontSize:'10px'}}>🧠</Tag></Tooltip>}
          {r.bankStatementUploaded && <Tooltip title="Bank Statement ✓"><Tag color="orange" style={{fontSize:'10px'}}>🏦</Tag></Tooltip>}
          {r.aaVerified && <Tooltip title="AA Verified ✓"><Tag color="green" style={{fontSize:'10px'}}>🔗</Tag></Tooltip>}
          {r.ocrDocsVerified > 0 && <Tooltip title={`${r.ocrDocsVerified} docs OCR verified`}><Tag color="pink" style={{fontSize:'10px'}}>📄×{r.ocrDocsVerified}</Tag></Tooltip>}
          {!r.psychometricCompleted && !r.bankStatementUploaded && !r.aaVerified && <span style={{color:'#9ca3af',fontSize:'12px'}}>Base only</span>}
        </Space>
      ),
    },
    {
      title: 'Loan Amount', dataIndex: 'loanAmount', key: 'loanAmount', width: 120, align: 'right',
    },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 110,
      render: (s) => {
        const cfg = { pending: ['default','Pending'], approved: ['success','Approved'], rejected: ['error','Rejected'], under_review: ['warning','Under Review'] };
        const [color, label] = cfg[s] || ['default', s];
        return <Badge status={color} text={label} />;
      },
    },
  ];

  return (
    <div className="dashboard-wrapper">
      {/* ── Header ── */}
      <div className="dashboard-header-band">
        <div className="dashboard-header-content">
          <div>
            <h1 className="dashboard-title">
              <DashboardOutlined /> Decision Intelligence Platform
            </h1>
            <p className="dashboard-subtitle">
              B2B Credit Analytics · 7-Engine Pipeline · Real-Time Processing
            </p>
          </div>
          <div className="dashboard-live-indicator">
            <span className="live-dot" /> LIVE
          </div>
        </div>
      </div>

      <div className="dashboard-body">
        {/* ── KPI Row ── */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          {[
            { title: 'Total Applications', value: stats?.totalApplications ?? 0, icon: <TeamOutlined />, color: '#6366f1' },
            { title: 'Approved', value: stats?.approvedApplications ?? 0, icon: <CheckCircleOutlined />, color: '#10b981', suffix: `(${stats?.approvalRate ?? 0}%)` },
            { title: 'Average Score', value: stats?.averageScore ?? 0, icon: <LineChartOutlined />, color: '#3b82f6' },
            { title: 'Total Disbursed', value: stats?.totalDisbursed ?? '₹0', icon: <BankOutlined />, color: '#f59e0b', isStr: true },
            { title: 'Fraud Flagged', value: (stats?.fraudHighCount ?? 0) + (stats?.fraudMediumCount ?? 0), icon: <SafetyOutlined />, color: '#ef4444' },
            { title: 'Psychometric Done', value: stats?.psychometricCompletedCount ?? 0, icon: '🧠', color: '#8b5cf6' },
            { title: 'AA Verified', value: stats?.aaVerifiedCount ?? 0, icon: '🔗', color: '#22c55e' },
            { title: 'Bank Statements', value: stats?.bankStatementCount ?? 0, icon: '🏦', color: '#f97316' },
          ].map((kpi) => (
            <Col xs={12} sm={8} md={6} lg={3} key={kpi.title}>
              <Card className="kpi-card" bordered={false}>
                <div className="kpi-icon" style={{ background: kpi.color + '20', color: kpi.color }}>
                  {typeof kpi.icon === 'string' ? kpi.icon : kpi.icon}
                </div>
                <div className="kpi-value" style={{ color: kpi.color }}>
                  {kpi.isStr ? kpi.value : kpi.value.toLocaleString()}
                </div>
                <div className="kpi-label">{kpi.title}</div>
                {kpi.suffix && <div className="kpi-suffix">{kpi.suffix}</div>}
              </Card>
            </Col>
          ))}
        </Row>

        <Tabs activeKey={activeTab} onChange={setActiveTab} size="large" className="dashboard-tabs"
          items={[
            {
              key: 'overview',
              label: <><BarChartOutlined /> Overview</>,
              children: <OverviewTab stats={stats} riskData={riskData} engineBarData={engineBarData} />,
            },
            {
              key: 'engines',
              label: <><ThunderboltOutlined /> Engine Health</>,
              children: <EngineHealthTab stats={stats} />,
            },
            {
              key: 'score_arch',
              label: <><PieChartOutlined /> Score Architecture</>,
              children: <ScoreArchTab architecture={architecture} engineBarData={engineBarData} />,
            },
            {
              key: 'applications',
              label: <><FileTextOutlined /> Applications</>,
              children: (
                <Table
                  dataSource={applications}
                  columns={columns}
                  rowKey="id"
                  loading={loading}
                  pagination={{ pageSize: 8 }}
                  scroll={{ x: 900 }}
                  size="middle"
                />
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}

/* ─── Overview Tab ────────────────────────────────────────── */
function OverviewTab({ stats, riskData, engineBarData }) {
  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} md={10}>
        <Card title={<><PieChartOutlined /> Risk Distribution</>} bordered={false} className="chart-card">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={riskData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {riskData.map((entry, i) => (
                  <Cell key={i} fill={['#10b981','#3b82f6','#f59e0b','#ef4444'][i]} />
                ))}
              </Pie>
              <RechartTooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </Col>
      <Col xs={24} md={14}>
        <Card title={<><BarChartOutlined /> Engine Max Bonus Points</>} bordered={false} className="chart-card">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={engineBarData} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={110} tick={{ fontSize: 12 }} />
              <RechartTooltip formatter={(v) => [`+${v} pts`, 'Max Bonus']} />
              <Bar dataKey="maxBonus" radius={[0, 4, 4, 0]}>
                {engineBarData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </Col>
      <Col xs={24}>
        <Card title="📋 Fraud Detection Summary" bordered={false} className="chart-card">
          <Row gutter={16}>
            {[
              { label: 'Low Risk', value: (stats?.totalApplications ?? 0) - (stats?.fraudHighCount ?? 0) - (stats?.fraudMediumCount ?? 0), color: '#10b981' },
              { label: 'Medium Risk', value: stats?.fraudMediumCount ?? 0, color: '#f59e0b' },
              { label: 'High Risk (Flagged)', value: stats?.fraudHighCount ?? 0, color: '#ef4444' },
            ].map((f) => (
              <Col key={f.label} xs={8}>
                <div style={{ textAlign: 'center', padding: '16px 0' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: f.color }}>{f.value}</div>
                  <div style={{ color: '#6b7280' }}>{f.label}</div>
                </div>
              </Col>
            ))}
          </Row>
          <Progress
            percent={Math.round(((stats?.totalApplications ?? 0) - (stats?.fraudHighCount ?? 0) - (stats?.fraudMediumCount ?? 0)) / Math.max(stats?.totalApplications ?? 1, 1) * 100)}
            strokeColor={{ '0%': '#10b981', '100%': '#3b82f6' }}
            format={(p) => `${p}% Clean`}
          />
        </Card>
      </Col>
    </Row>
  );
}

/* ─── Engine Health Tab ───────────────────────────────────── */
function EngineHealthTab({ stats }) {
  const perf = stats?.enginePerformance || {};

  return (
    <Row gutter={[16, 16]}>
      {ENGINE_META.map((engine) => {
        const ep = perf[engine.name] || { count: 0, avgBonus: 0 };
        const isAuto = engine.auto;
        return (
          <Col xs={24} sm={12} lg={8} key={engine.id}>
            <Card
              bordered={false}
              className="engine-health-card"
              style={{ borderLeft: `4px solid ${engine.color}` }}
            >
              <div className="engine-health-header">
                <span className="engine-health-icon" style={{ fontSize: '2rem' }}>{engine.icon}</span>
                <div>
                  <div className="engine-health-name">{engine.name}</div>
                  <Tag color={isAuto ? 'blue' : 'purple'} style={{ fontSize: '10px' }}>
                    {isAuto ? '⚡ Auto-Run' : '👤 User-Triggered'}
                  </Tag>
                </div>
                <Badge status="success" text="Active" style={{ marginLeft: 'auto' }} />
              </div>

              {engine.maxBonus > 0 ? (
                <div style={{ marginTop: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: '12px', color: '#6b7280' }}>Max Bonus</span>
                    <span style={{ fontWeight: 700, color: engine.color }}>+{engine.maxBonus} pts</span>
                  </div>
                  <Progress percent={100} strokeColor={engine.color} showInfo={false} size="small" />
                  {ep.count > 0 && (
                    <div style={{ marginTop: 8, fontSize: '12px', color: '#6b7280' }}>
                      Used by {ep.count} applications · avg +{ep.avgBonus} pts
                    </div>
                  )}
                </div>
              ) : engine.id === 'fraud_detection' ? (
                <div style={{ marginTop: 12, fontSize: '12px', color: '#6b7280' }}>
                  Penalty: up to <strong style={{ color: '#ef4444' }}>-50 pts</strong> for High Risk<br />
                  Auto-applied to every submission
                </div>
              ) : (
                <div style={{ marginTop: 12, fontSize: '12px', color: '#6b7280' }}>
                  Informational — no direct score change<br />
                  Provides transparency and context
                </div>
              )}
            </Card>
          </Col>
        );
      })}

      {/* Engine Performance Summary */}
      <Col xs={24}>
        <Card title="🏆 Engine Adoption Rates" bordered={false} className="chart-card">
          <Alert
            message="B2B Insight: More engines used = higher score accuracy and lower default risk"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Row gutter={16}>
            {[
              { label: 'Psychometric', value: stats?.psychometricCompletedCount ?? 0, total: stats?.totalApplications ?? 0, color: '#8b5cf6' },
              { label: 'Bank Statement', value: stats?.bankStatementCount ?? 0, total: stats?.totalApplications ?? 0, color: '#f97316' },
              { label: 'AA Verified', value: stats?.aaVerifiedCount ?? 0, total: stats?.totalApplications ?? 0, color: '#22c55e' },
            ].map((a) => (
              <Col xs={24} md={8} key={a.label}>
                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{a.label}</span>
                    <span style={{ color: a.color, fontWeight: 700 }}>
                      {a.value}/{a.total}
                    </span>
                  </div>
                  <Progress
                    percent={a.total > 0 ? Math.round(a.value / a.total * 100) : 0}
                    strokeColor={a.color}
                    size="small"
                  />
                </div>
              </Col>
            ))}
          </Row>
        </Card>
      </Col>
    </Row>
  );
}

/* ─── Score Architecture Tab ──────────────────────────────── */
function ScoreArchTab({ architecture, engineBarData }) {
  if (!architecture) return <div style={{ padding: 40, textAlign: 'center', color: '#9ca3af' }}>Loading...</div>;

  return (
    <Row gutter={[16, 16]}>
      {/* Score Tiers */}
      <Col xs={24}>
        <Card title={<><BarChartOutlined /> Score Tiers — What Score Gets What</>} bordered={false} className="chart-card">
          <div className="score-tier-grid">
            {architecture.tiers.map((tier) => (
              <div key={tier.name} className="score-tier-card" style={{ borderTop: `4px solid ${tier.color}` }}>
                <div className="tier-score-range" style={{ color: tier.color }}>
                  {tier.min} – {tier.max}
                </div>
                <div className="tier-name" style={{ color: tier.color }}>{tier.name}</div>
                <Divider style={{ margin: '8px 0' }} />
                <table className="tier-details-table">
                  <tbody>
                    <tr><td>Interest Rate</td><td><strong>{tier.interestRate}</strong></td></tr>
                    <tr><td>Individual Max</td><td><strong>{tier.individualMax}</strong></td></tr>
                    <tr><td>SME Max</td><td><strong>{tier.smeMax}</strong></td></tr>
                    <tr><td>Decision</td><td><strong>{tier.approval}</strong></td></tr>
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        </Card>
      </Col>

      {/* How Score is Built */}
      <Col xs={24} md={14}>
        <Card title="🏗️ How Score is Built (Engine Contributions)" bordered={false} className="chart-card">
          <div style={{ marginBottom: 16, padding: '12px 16px', background: '#f0f9ff', borderRadius: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Baseline Score</span><strong>500 pts</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Maximum Possible Score</span><strong>975 pts</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Max Bonus from Engines</span><strong style={{ color: '#10b981' }}>+475 pts</strong>
            </div>
          </div>
          {architecture.engineContributions.map((e) => (
            <div key={e.engine} style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: '13px' }}>
                  {e.engine}
                  {e.optional && <Tag style={{ marginLeft: 8, fontSize: '10px' }} color="blue">Optional</Tag>}
                  {e.auto && <Tag style={{ marginLeft: 8, fontSize: '10px' }} color="green">Auto</Tag>}
                </span>
                <span style={{ fontWeight: 700, color: e.maxPoints > 0 ? '#10b981' : '#ef4444' }}>
                  {e.maxPoints > 0 ? `+${e.maxPoints}` : e.maxPenalty || '0'} pts
                </span>
              </div>
              <Progress
                percent={e.maxPoints > 0 ? Math.round(e.maxPoints / 475 * 100) : 0}
                strokeColor={e.maxPoints > 0 ? '#10b981' : '#ef4444'}
                size="small"
              />
            </div>
          ))}
        </Card>
      </Col>

      {/* Requirements */}
      <Col xs={24} md={10}>
        <Card title="✅ What to Provide for Max Score" bordered={false} className="chart-card">
          {[
            { icon: '💼', label: 'Salaried employment', pts: '+45' },
            { icon: '💰', label: 'Monthly income > ₹75k', pts: '+80' },
            { icon: '💡', label: 'Utility bills on record', pts: '+50' },
            { icon: '📱', label: 'Active UPI history', pts: '+40' },
            { icon: '🏦', label: 'Bank account > ₹1L balance', pts: '+50' },
            { icon: '🧠', label: 'Complete psychometric quiz', pts: '+60' },
            { icon: '📋', label: 'Upload bank statement', pts: '+120' },
            { icon: '📄', label: 'Upload ITR + utility bill', pts: '+80' },
            { icon: '🔗', label: 'AA-verify bank account', pts: '+100' },
            { icon: '📊', label: 'File GST returns (SME)', pts: '+50' },
          ].map((r) => (
            <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #f3f4f6' }}>
              <span>{r.icon} {r.label}</span>
              <Tag color="green">{r.pts}</Tag>
            </div>
          ))}
        </Card>
      </Col>
    </Row>
  );
}
