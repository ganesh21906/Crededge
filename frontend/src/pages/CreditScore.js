import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Card, Row, Col, Progress, Tag, Statistic, List,
  Divider, Button, Alert, Spin, Space, Collapse, Badge, Timeline, Modal, Upload, Select, message, Form, Input
} from 'antd';
import {
  CheckCircleOutlined, WarningOutlined, InfoCircleOutlined,
  TrophyOutlined, RocketOutlined, HomeOutlined, ThunderboltOutlined,
  BulbOutlined, ClockCircleOutlined, ArrowUpOutlined, UploadOutlined, LockOutlined, FilePdfOutlined, BankOutlined, FileTextOutlined
} from '@ant-design/icons';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';
import { 
  getApplicationById, uploadBankStatement, uploadDocument, 
  initiateAAConsent, simulateAAApproval 
} from '../services/api';
import { RISK_CATEGORIES, SCORE_THRESHOLDS } from '../constants';
import './CreditScore.css';

const { Panel } = Collapse;

// Animated counter
const AnimatedNumber = ({ value, duration = 2000 }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start;
    const step = (ts) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      setDisplay(Math.floor(progress * value));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [value, duration]);
  return <span>{display}</span>;
};

// Impact badge color
const impactColor = { 'Very High': '#f5222d', High: '#fa8c16', Medium: '#1890ff', Low: '#52c41a' };

function CreditScore() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // ✅ CRITICAL FIX: Use data passed from form submission first
  // Falls back to API fetch if accessed directly via URL
  const [scoreData, setScoreData] = useState(location.state?.scoreData || null);
  const [loading, setLoading] = useState(!location.state?.scoreData);
  const [error, setError] = useState('');

  // Optional Engines State
  const [bankModalVisible, setBankModalVisible] = useState(false);
  const [ocrModalVisible, setOcrModalVisible] = useState(false);
  const [aaModalVisible, setAaModalVisible] = useState(false);
  const [aaWaitActive, setAaWaitActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [aaPhone, setAaPhone] = useState('');
  const [ocrType, setOcrType] = useState('itr');

  // Trigger re-fetch for fresh score
  const refreshScoreData = () => {
    setLoading(true);
    getApplicationById(id).then(d => processData(d)).finally(() => setLoading(false));
  };

  const processData = (data) => {
    setScoreData({
      applicationId: data.id || data.applicationId,
      applicationType: data.applicationType,
      creditScore: data.creditScore,
      riskCategory: data.riskCategory,
      approvalStatus: data.approvalStatus,
      interestRate: data.interestRate,
      maxLoanEligible: data.maxLoanEligible,
      loanAmount: data.loanAmount || data.loanAmountRaw,
      factors: data.factors || [],
      strengths: data.strengths || [],
      improvements: data.improvements || [],
      recommendations: data.recommendations || [],
      coachTips: data.coachTips || [],
      aiConfidence: data.aiConfidence,
      modelUsed: data.modelUsed,
      shapWaterfall: data.shapWaterfall || [],
      aaVerified: data.aaVerified,
      bankStatementUploaded: data.bankStatementUploaded,
      ocrDocsVerified: data.ocrDocsVerified || 0,
      psychometricCompleted: data.psychometricCompleted,
    });
  };

  useEffect(() => {
    if (location.state?.scoreData) {
       processData(location.state.scoreData);
       return; 
    }
    setLoading(true);
    getApplicationById(id)
      .then(processData)
      .catch(() => {
        setError('Could not load assessment results. Please try tracking your application.');
      })
      .finally(() => setLoading(false));
  }, [id, scoreData, location.state]);

  const handleBankUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    try {
      setUploading(true);
      await uploadBankStatement(scoreData.applicationId, file);
      onSuccess('Ok');
      message.success('Bank Statement analyzed successfully! Score boosted.');
      setBankModalVisible(false);
      refreshScoreData();
    } catch (e) {
      onError(e);
      message.error(e.response?.data?.detail || 'Failed to analyze bank statement');
    } finally {
      setUploading(false);
    }
  };

  const handleOcrUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    try {
      setUploading(true);
      await uploadDocument(scoreData.applicationId, ocrType, file);
      onSuccess('Ok');
      message.success('Document verified successfully! Score boosted.');
      setOcrModalVisible(false);
      refreshScoreData();
    } catch (e) {
      onError(e);
      message.error(e.response?.data?.detail || 'OCR verification failed');
    } finally {
      setUploading(false);
    }
  };

  const handleAaInitiate = async () => {
    if (!aaPhone || aaPhone.length !== 10) return message.error('Valid 10-digit phone required');
    try {
      setAaWaitActive(true);
      const res = await initiateAAConsent(scoreData.applicationId, aaPhone);
      // Simulate waiting 3 seconds for approval
      setTimeout(async () => {
        try {
           await simulateAAApproval(res.consentHandle, scoreData.applicationId);
           message.success('Account Aggregator data fetched securely! Score boosted.');
           setAaModalVisible(false);
           refreshScoreData();
        } catch(e) {
           message.error(e.response?.data?.detail || 'AA Approval Simulation Failed');
        } finally {
           setAaWaitActive(false);
        }
      }, 3000);
    } catch (e) {
      setAaWaitActive(false);
      message.error(e.response?.data?.detail || 'Failed to initiate Account Aggregator consent');
    }
  };

  if (loading) {
    return (
      <div className="score-loading">
        <div className="score-loading-inner">
          <Spin size="large" />
          <h2>Analyzing Your Application...</h2>
          <p>Our AI is processing your alternative data</p>
          <div className="loading-steps">
            {['Income Verification', 'Payment History Analysis', 'Alternative Data Scoring', 'Generating Report'].map((s, i) => (
              <motion.div
                key={s}
                className="loading-step"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.5 }}
              >
                <ClockCircleOutlined style={{ color: '#1890ff' }} /> {s}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !scoreData) {
    return (
      <div style={{ padding: 48, textAlign: 'center' }}>
        <Alert
          message="Application Not Found"
          description={error || 'Please check your Application ID.'}
          type="error"
          showIcon
          style={{ maxWidth: 500, margin: '0 auto 24px' }}
        />
        <Space>
          <Button type="primary" onClick={() => navigate('/track')}>Track Application</Button>
          <Button onClick={() => navigate('/')}>Back to Home</Button>
        </Space>
      </div>
    );
  }

  const meta = RISK_CATEGORIES[scoreData.riskCategory] || RISK_CATEGORIES.Fair;
  const scorePercent = Math.round((scoreData.creditScore / 1000) * 100);

  const getStatusType = (s) => {
    if (s === 'Approved') return 'success';
    if (s === 'Under Review') return 'warning';
    return 'error';
  };

  return (
    <div style={{ background: '#f0f2f5', minHeight: '100vh', padding: '24px' }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ maxWidth: 1400, margin: '0 auto' }}
      >
        {/* ── Header ── */}
        <Card className="score-header-card" style={{ marginBottom: 24, textAlign: 'center' }}>
          <TrophyOutlined style={{ fontSize: 52, color: meta.color, marginBottom: 12 }} />
          <h1 style={{ fontSize: '2rem', margin: '0 0 8px' }}>Credit Assessment Results</h1>
          <Space wrap>
            <Tag color="blue">ID: {scoreData.applicationId}</Tag>
            <Tag color="purple">{scoreData.applicationType} Application</Tag>
            <Tag>{scoreData.modelUsed || 'Rule-Based Engine'}</Tag>
          </Space>
        </Card>

        {/* ── Score + Approval ── */}
        <Row gutter={[24, 24]}>
          <Col xs={24} lg={12}>
            <motion.div
              initial={{ scale: 0.85, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 100, delay: 0.1 }}
            >
              <Card
                style={{
                  height: '100%',
                  background: `linear-gradient(135deg, ${meta.bgColor} 0%, white 100%)`,
                }}
              >
                <div style={{ textAlign: 'center', padding: '16px 0' }}>
                  <h2 style={{ marginBottom: 28 }}>Your Credit Score</h2>
                  <Progress
                    type="dashboard"
                    percent={scorePercent}
                    strokeColor={meta.color}
                    trailColor="#e8e8e8"
                    strokeWidth={10}
                    width={260}
                    format={() => (
                      <div>
                        <div style={{ fontSize: '3.8rem', fontWeight: 900, color: meta.color, lineHeight: 1 }}>
                          <AnimatedNumber value={scoreData.creditScore} />
                        </div>
                        <div style={{ fontSize: '1rem', color: '#8c8c8c', marginTop: 4 }}>out of 1000</div>
                      </div>
                    )}
                  />
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.6, type: 'spring' }} style={{ marginTop: 24 }}>
                    <Tag
                      style={{
                        fontSize: 18, padding: '8px 28px', borderRadius: 24,
                        color: meta.color, border: `2px solid ${meta.color}`,
                        background: meta.bgColor, fontWeight: 600,
                      }}
                    >
                      {scoreData.riskCategory} Score
                    </Tag>
                  </motion.div>
                  <div style={{ marginTop: 12, color: '#8c8c8c', fontSize: 13 }}>
                    AI Confidence: <strong style={{ color: meta.color }}>{Math.round(scoreData.aiConfidence || 0)}%</strong>
                  </div>
                </div>
              </Card>
            </motion.div>
          </Col>

          <Col xs={24} lg={12}>
            <motion.div initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
              <Card title={<><InfoCircleOutlined /> Approval Details</>} style={{ height: '100%' }}>
                <Alert
                  message={scoreData.approvalStatus}
                  description={
                    scoreData.approvalStatus === 'Approved'
                      ? 'Congratulations! Your application meets our credit criteria.'
                      : scoreData.approvalStatus === 'Under Review'
                      ? 'Your application is being reviewed. We may contact you for additional information.'
                      : 'Your application requires additional review. Consider improving the areas listed below.'
                  }
                  type={getStatusType(scoreData.approvalStatus)}
                  showIcon
                  style={{ marginBottom: 20 }}
                />
                <Row gutter={[16, 20]}>
                  <Col span={12}>
                    <Statistic title="Interest Rate" value={scoreData.interestRate} valueStyle={{ color: '#1890ff' }} suffix="p.a." />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Max Loan Eligible" value={scoreData.maxLoanEligible} valueStyle={{ color: '#52c41a' }} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Requested Amount" value={scoreData.loanAmount} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Processing Time" value="< 1" suffix="min" valueStyle={{ color: '#fa8c16' }} />
                  </Col>
                </Row>
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* ── Progressive Profiling / Optional Engines ── */}
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.25 }}>
          <Card 
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <RocketOutlined style={{ color: '#eb2f96', fontSize: 20 }} /> <span style={{ fontSize: 18 }}>Boost Your Score</span>
              </div>
            }
            style={{ marginTop: 24, border: '2px solid #eb2f96' }}
            styles={{ header: { background: '#fff0f6' } }}
          >
            <p style={{ marginBottom: 16, color: '#666', fontSize: 15 }}>
              Complete these optional assessments to securely provide alternative data and potentially boost your score by up to <strong>360 points</strong>.
            </p>
            <Row gutter={[16, 16]}>
              <Col xs={24} md={6}>
                <Card size="small" hoverable={!scoreData.psychometricCompleted} style={{ background: scoreData.psychometricCompleted ? '#f6ffed' : '#fff', opacity: scoreData.psychometricCompleted ? 0.7 : 1 }}>
                  <Statistic title={<Space>🧠 Psychometric {scoreData.psychometricCompleted && <CheckCircleOutlined style={{color:'#52c41a'}}/>}</Space>} value="+60" valueStyle={{ color: '#8b5cf6', fontSize: 24, fontWeight: 700 }} suffix="pts" />
                  <Button type="primary" size="large" style={{ background: '#8b5cf6', width: '100%', marginTop: 12, border: 'none' }} disabled={scoreData.psychometricCompleted} onClick={() => navigate(`/psychometric?appId=${scoreData.applicationId}`)}>
                    {scoreData.psychometricCompleted ? 'Completed' : 'Take Quiz'}
                  </Button>
                </Card>
              </Col>
              
              <Col xs={24} md={6}>
                <Card size="small" hoverable={!scoreData.bankStatementUploaded} style={{ background: scoreData.bankStatementUploaded ? '#f6ffed' : '#fff', opacity: scoreData.bankStatementUploaded ? 0.7 : 1 }}>
                  <Statistic title={<Space>🏦 Bank Statement {scoreData.bankStatementUploaded && <CheckCircleOutlined style={{color:'#52c41a'}}/>}</Space>} value="+120" valueStyle={{ color: '#f97316', fontSize: 24, fontWeight: 700 }} suffix="pts" />
                  <Button type="primary" size="large" style={{ background: '#f97316', width: '100%', marginTop: 12, border: 'none' }} disabled={scoreData.bankStatementUploaded} onClick={() => setBankModalVisible(true)}>
                    {scoreData.bankStatementUploaded ? 'Uploaded' : 'Upload PDF'}
                  </Button>
                </Card>
              </Col>

              <Col xs={24} md={6}>
                 <Card size="small" hoverable style={{ background: scoreData.ocrDocsVerified > 0 ? '#f6ffed' : '#fff' }}>
                  <Statistic title={<Space>📄 OCR Documents {scoreData.ocrDocsVerified > 0 && <CheckCircleOutlined style={{color:'#52c41a'}}/>}</Space>} value="+80" valueStyle={{ color: '#ec4899', fontSize: 24, fontWeight: 700 }} suffix="pts" />
                  <Button type="primary" size="large" style={{ background: '#ec4899', width: '100%', marginTop: 12, border: 'none' }} onClick={() => setOcrModalVisible(true)}>
                    {scoreData.ocrDocsVerified > 0 ? 'Upload More' : 'Verify Docs'}
                  </Button>
                </Card>
              </Col>

              <Col xs={24} md={6}>
                <Card size="small" hoverable={!scoreData.aaVerified} style={{ background: scoreData.aaVerified ? '#f6ffed' : '#fff', opacity: scoreData.aaVerified ? 0.7 : 1 }}>
                  <Statistic title={<Space>🔗 Account Aggregator {scoreData.aaVerified && <CheckCircleOutlined style={{color:'#52c41a'}}/>}</Space>} value="+100" valueStyle={{ color: '#22c55e', fontSize: 24, fontWeight: 700 }} suffix="pts" />
                  <Button type="primary" size="large" style={{ background: '#22c55e', width: '100%', marginTop: 12, border: 'none' }} disabled={scoreData.aaVerified} onClick={() => setAaModalVisible(true)}>
                    {scoreData.aaVerified ? 'Securely Linked' : 'Link Bank'}
                  </Button>
                </Card>
              </Col>
            </Row>
          </Card>
        </motion.div>

        {/* ── Charts ── */}
        <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
          <Col xs={24} lg={12}>
            <motion.div initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }}>
              <Card title="Score Breakdown (Radar)">
                <ResponsiveContainer width="100%" height={280}>
                  <RadarChart data={scoreData.factors}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
                    <Radar name="Your Score" dataKey="score" stroke={meta.color} fill={meta.color} fillOpacity={0.5} />
                  </RadarChart>
                </ResponsiveContainer>
              </Card>
            </motion.div>
          </Col>
          <Col xs={24} lg={12}>
            <motion.div initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.4 }}>
              <Card title="Factor Contributions">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={scoreData.factors} margin={{ bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-20} textAnchor="end" height={70} tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 100]} />
                    <Tooltip formatter={(v, n, p) => [`${v}/100`, p.payload.name]} />
                    <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                      {scoreData.factors.map((f, i) => (
                        <Cell key={i} fill={f.score >= 80 ? '#52c41a' : f.score >= 65 ? '#1890ff' : f.score >= 50 ? '#fa8c16' : '#f5222d'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* ── Factor Details ── */}
        <motion.div initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.5 }}>
          <Card title="Detailed Factor Breakdown" style={{ marginTop: 24 }}>
            {scoreData.factors.map((f, i) => (
              <motion.div key={f.name} initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.5 + i * 0.1 }}>
                <div className="factor-row">
                  <div className="factor-header">
                    <div>
                      <strong>{f.name}</strong>
                      <div style={{ color: '#8c8c8c', fontSize: 12 }}>{f.description}</div>
                    </div>
                    <Space>
                      <Tag color={f.score >= 80 ? 'green' : f.score >= 65 ? 'blue' : f.score >= 50 ? 'orange' : 'red'}>
                        {f.score}/100
                      </Tag>
                      <Tag>Weight: {f.weight}%</Tag>
                    </Space>
                  </div>
                  <Progress
                    percent={f.score}
                    strokeColor={f.score >= 80 ? '#52c41a' : f.score >= 65 ? '#1890ff' : f.score >= 50 ? '#fa8c16' : '#f5222d'}
                    showInfo={false}
                    style={{ marginTop: 8 }}
                  />
                </div>
                {i < scoreData.factors.length - 1 && <Divider style={{ margin: '12px 0' }} />}
              </motion.div>
            ))}
          </Card>
        </motion.div>

        {/* ── Mathematical Explainability (SHAP Waterfall) ── */}
        {scoreData.shapWaterfall && scoreData.shapWaterfall.length > 0 && (
          <motion.div initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.55 }}>
            <Card 
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <ThunderboltOutlined style={{ color: '#722ed1' }} />
                  Mathematical Architecture
                  <Tag color="purple" style={{ marginLeft: 8 }}>AI Explainability Engine</Tag>
                </div>
              } 
              style={{ marginTop: 24, borderTop: '3px solid #722ed1' }}
            >
              <Alert 
                message="How your score was calculated" 
                description="This transparent log shows exactly how our AI weighted your alternative data factors to generate your final score."
                type="info" showIcon style={{ marginBottom: 24, borderRadius: 8 }}
              />
              <Timeline mode="alternate">
                {scoreData.shapWaterfall.map((item, i) => (
                  <Timeline.Item 
                    key={i} 
                    color={item.direction === 'positive' ? 'green' : item.direction === 'negative' ? 'red' : 'blue'}
                  >
                    <div style={{ padding: '4px 0' }}>
                      <strong style={{ fontSize: 16 }}>{item.factor}</strong>
                      <div style={{ margin: '4px 0' }}>
                        <Tag color={item.direction === 'positive' ? 'success' : item.direction === 'negative' ? 'error' : 'processing'}>
                          {item.contribution > 0 ? '+' : ''}{item.contribution} points
                        </Tag>
                      </div>
                      <div style={{ color: '#6b7280', fontSize: 13 }}>{item.explanation}</div>
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          </motion.div>
        )}

        {/* ── Strengths / Improvements / Recommendations ── */}
        <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
          <Col xs={24} md={8}>
            <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.6 }}>
              <Card
                title={<><CheckCircleOutlined style={{ color: '#52c41a' }} /> Strengths</>}
                style={{ height: '100%', borderTop: '3px solid #52c41a' }}
              >
                <List
                  dataSource={scoreData.strengths}
                  renderItem={(item) => (
                    <List.Item style={{ borderBottom: 'none', padding: '6px 0' }}>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />{item}
                    </List.Item>
                  )}
                />
              </Card>
            </motion.div>
          </Col>
          <Col xs={24} md={8}>
            <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.7 }}>
              <Card
                title={<><WarningOutlined style={{ color: '#fa8c16' }} /> Areas to Improve</>}
                style={{ height: '100%', borderTop: '3px solid #fa8c16' }}
              >
                <List
                  dataSource={scoreData.improvements}
                  renderItem={(item) => (
                    <List.Item style={{ borderBottom: 'none', padding: '6px 0' }}>
                      <WarningOutlined style={{ color: '#fa8c16', marginRight: 8 }} />{item}
                    </List.Item>
                  )}
                />
              </Card>
            </motion.div>
          </Col>
          <Col xs={24} md={8}>
            <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.8 }}>
              <Card
                title={<><InfoCircleOutlined style={{ color: '#1890ff' }} /> Recommendations</>}
                style={{ height: '100%', borderTop: '3px solid #1890ff' }}
              >
                <List
                  dataSource={scoreData.recommendations}
                  renderItem={(item) => (
                    <List.Item style={{ borderBottom: 'none', padding: '6px 0' }}>
                      <InfoCircleOutlined style={{ color: '#1890ff', marginRight: 8 }} />{item}
                    </List.Item>
                  )}
                />
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* ── 🔥 AI Financial Coach ── */}
        {scoreData.coachTips && scoreData.coachTips.length > 0 && (
          <motion.div initial={{ y: 40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.9 }}>
            <Card
              className="coach-card"
              style={{ marginTop: 24 }}
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div className="coach-avatar">🤖</div>
                  <div>
                    <div style={{ fontSize: 16, fontWeight: 700 }}>AI Financial Coach</div>
                    <div style={{ fontSize: 12, color: '#6b7280', fontWeight: 400 }}>
                      Personalized steps to improve your credit score
                    </div>
                  </div>
                  <Tag color="purple" style={{ marginLeft: 'auto' }}>
                    <ThunderboltOutlined /> AI-Powered
                  </Tag>
                </div>
              }
            >
              <Row gutter={[16, 16]}>
                {scoreData.coachTips.map((tip, i) => (
                  <Col xs={24} sm={12} lg={8} key={i}>
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 1.0 + i * 0.1 }}
                    >
                      <Card className="coach-tip-card" hoverable>
                        <div className="coach-tip-icon">{tip.icon}</div>
                        <h4 className="coach-tip-title">{tip.title}</h4>
                        <p className="coach-tip-text">{tip.tip}</p>
                        <div className="coach-tip-meta">
                          <Badge
                            color={impactColor[tip.impact] || '#1890ff'}
                            text={
                              <span style={{ fontSize: 12, color: impactColor[tip.impact] }}>
                                {tip.impact} Impact
                              </span>
                            }
                          />
                          <span className="coach-tip-time"><ClockCircleOutlined /> {tip.timeframe}</span>
                        </div>
                      </Card>
                    </motion.div>
                  </Col>
                ))}
              </Row>

              <Alert
                icon={<ArrowUpOutlined />}
                message="Following these steps consistently can improve your score by 80–150 points within 6 months."
                type="info"
                showIcon
                style={{ marginTop: 16, borderRadius: 12 }}
              />
            </Card>
          </motion.div>
        )}

        {/* ── Actions ── */}
        <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 1.1 }}>
          <Card style={{ marginTop: 24, textAlign: 'center' }}>
            <Space size="large" wrap>
              <Button type="primary" size="large" icon={<RocketOutlined />} onClick={() => navigate('/dashboard')}>
                View Dashboard
              </Button>
              <Button size="large" icon={<HomeOutlined />} onClick={() => navigate('/')}>
                Back to Home
              </Button>
              <Button size="large" icon={<BulbOutlined />} onClick={() => navigate('/track')}>
                Track Application
              </Button>
            </Space>
          </Card>
        </motion.div>
      </motion.div>

      {/* ── Optional Engines Modals ── */}
      <Modal
        title={<span><BankOutlined style={{color:'#f97316'}}/> Upload Bank Statement</span>}
        open={bankModalVisible}
        onCancel={() => setBankModalVisible(false)}
        footer={null}
      >
        <Alert message="Secured processing" description="Your 6-12 month PDF statement will be parsed for cash flow stability and deleted immediately." type="info" showIcon style={{marginBottom: 16}}/>
        <Upload.Dragger accept=".pdf" customRequest={handleBankUpload} showUploadList={false}>
          <p className="ant-upload-drag-icon"><FilePdfOutlined style={{color:'#f97316'}}/></p>
          <p className="ant-upload-text">Click or drag bank statement PDF to this area to upload</p>
          <p className="ant-upload-hint">Upload a 6+ month statement (up to 10MB) for +120 max points.</p>
          {uploading && <div style={{marginTop:16}}><Spin/> Analyzing Statement...</div>}
        </Upload.Dragger>
      </Modal>

      <Modal
        title={<span><FileTextOutlined style={{color:'#ec4899'}}/> Verify OCR Documents</span>}
        open={ocrModalVisible}
        onCancel={() => setOcrModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical">
          <Form.Item label="Document Type">
            <Select value={ocrType} onChange={setOcrType}>
              <Select.Option value="itr">ITR Acknowledgement (+45 pts)</Select.Option>
              <Select.Option value="gst">GST Return (+50 pts)</Select.Option>
              <Select.Option value="utility">Utility Bill (+35 pts)</Select.Option>
              <Select.Option value="msme">MSME Certificate (+40 pts)</Select.Option>
              <Select.Option value="salary">Salary Slip (+30 pts)</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="Upload Document/Image">
            <Upload.Dragger accept=".pdf,image/*" customRequest={handleOcrUpload} showUploadList={false}>
              <p className="ant-upload-drag-icon"><UploadOutlined style={{color:'#ec4899'}}/></p>
              <p className="ant-upload-text">Click or drag your document here</p>
              <p className="ant-upload-hint">AI validation takes ~3 seconds.</p>
              {uploading && <div style={{marginTop:16}}><Spin/> Extracting Data...</div>}
            </Upload.Dragger>
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title={<span><LockOutlined style={{color:'#22c55e'}}/> Account Aggregator Consent</span>}
        open={aaModalVisible}
        onCancel={() => !aaWaitActive && setAaModalVisible(false)}
        footer={null}
        closable={!aaWaitActive}
      >
        <div style={{textAlign:'center', padding:'16px 0'}}>
           <div style={{fontSize:48, marginBottom: 16}}>🏦 ↔️ 📱</div>
           <h3 style={{marginBottom: 24}}>RBI Regulated Data Sharing</h3>
           <Input size="large" prefix="+91" placeholder="Registered 10-digit Phone" value={aaPhone} onChange={e => setAaPhone(e.target.value)} maxLength={10} style={{marginBottom: 24}} disabled={aaWaitActive} />
           
           {!aaWaitActive ? (
             <Button type="primary" size="large" style={{background:'#22c55e', border:'none', width:'100%'}} onClick={handleAaInitiate}>
                Initiate Secure Consent
             </Button>
           ) : (
             <div style={{padding: '24px 0', background: '#f6ffed', borderRadius: 8, border: '1px solid #b7eb8f'}}>
               <Spin size="large" style={{marginBottom: 16}} />
               <h4>Awaiting Your Approval</h4>
               <p style={{color:'#666'}}>Please check your Setu/Finvu app to approve the data sharing request...</p>
             </div>
           )}
        </div>
      </Modal>

    </div>
  );
}

export default CreditScore;
