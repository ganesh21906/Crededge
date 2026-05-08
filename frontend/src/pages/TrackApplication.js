import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, Input, Button, Alert, Spin, Tag, Divider, Row, Col, Progress, List, Statistic } from 'antd';
import { SearchOutlined, CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined, BankOutlined, RocketOutlined } from '@ant-design/icons';
import { getApplicationById } from '../services/api';
import { RISK_CATEGORIES, SCORE_THRESHOLDS } from '../constants';
import { Link } from 'react-router-dom';
import './TrackApplication.css';

function TrackApplication() {
  const [appId, setAppId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    const id = appId.trim().toUpperCase();
    if (!id) { setError('Please enter your Application ID'); return; }
    if (!id.startsWith('IND-') && !id.startsWith('SME-')) {
      setError('Application ID must start with IND- or SME-');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await getApplicationById(id);
      setResult(data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`Application "${id}" not found. Please check your Application ID.`);
      } else {
        setError('Unable to fetch application. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    if (status === 'approved') return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />;
    if (status === 'rejected') return <CloseCircleOutlined style={{ color: '#f5222d', fontSize: 20 }} />;
    return <ClockCircleOutlined style={{ color: '#fa8c16', fontSize: 20 }} />;
  };

  const getStatusTag = (status) => {
    const map = {
      approved: { color: 'success', text: '✅ Approved' },
      rejected: { color: 'error',   text: '❌ Rejected' },
      pending:  { color: 'warning', text: '⏳ Under Review' },
    };
    const s = map[status] || { color: 'default', text: status };
    return <Tag color={s.color} style={{ fontSize: 14, padding: '4px 16px', borderRadius: 20 }}>{s.text}</Tag>;
  };

  const scoreColor = result ? (RISK_CATEGORIES[result.riskCategory]?.color || '#1890ff') : '#1890ff';
  const scorePercent = result ? Math.round((result.creditScore / 1000) * 100) : 0;

  return (
    <div className="track-page">
      <motion.div
        className="track-hero"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <BankOutlined className="track-hero-icon" />
        <h1>Track Your Application</h1>
        <p>Enter your Application ID to check real-time status and credit score</p>

        <div className="track-search-box">
          <Input
            size="large"
            value={appId}
            onChange={(e) => setAppId(e.target.value)}
            onPressEnter={handleSearch}
            placeholder="e.g., IND-A1B2C3D4 or SME-E5F6G7H8"
            prefix={<SearchOutlined style={{ color: '#94a3b8' }} />}
            className="track-input"
            style={{ borderRadius: '12px 0 0 12px', height: 54 }}
          />
          <Button
            type="primary"
            size="large"
            loading={loading}
            onClick={handleSearch}
            icon={<SearchOutlined />}
            style={{ borderRadius: '0 12px 12px 0', height: 54, minWidth: 130 }}
          >
            Search
          </Button>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            onClose={() => setError('')}
            style={{ marginTop: 16, borderRadius: 12 }}
          />
        )}
      </motion.div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
          <p style={{ marginTop: 16, color: '#6b7280' }}>Fetching your application details...</p>
        </div>
      )}

      {result && !loading && (
        <motion.div
          className="track-result"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Header Card */}
          <Card className="track-card track-header-card">
            <Row align="middle" gutter={24}>
              <Col xs={24} md={12}>
                <div className="track-app-info">
                  <h2>{result.applicantName}</h2>
                  <Tag color="blue" style={{ marginBottom: 8 }}>{result.applicationId}</Tag>
                  <Tag color="purple">{result.applicationType} Application</Tag>
                  <div style={{ marginTop: 12 }}>
                    {getStatusTag(result.status)}
                  </div>
                  {result.submittedAt && (
                    <p className="track-date">
                      Submitted: {new Date(result.submittedAt).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                  )}
                </div>
              </Col>
              <Col xs={24} md={12}>
                <div className="track-score-display">
                  <Progress
                    type="dashboard"
                    percent={scorePercent}
                    strokeColor={scoreColor}
                    strokeWidth={10}
                    width={160}
                    format={() => (
                      <div>
                        <div style={{ fontSize: '2.2rem', fontWeight: 800, color: scoreColor }}>{result.creditScore}</div>
                        <div style={{ fontSize: 12, color: '#8c8c8c' }}>/ 1000</div>
                      </div>
                    )}
                  />
                  <Tag
                    style={{
                      marginTop: 12,
                      fontSize: 14,
                      padding: '4px 20px',
                      borderRadius: 20,
                      color: scoreColor,
                      border: `1px solid ${scoreColor}`,
                      background: RISK_CATEGORIES[result.riskCategory]?.bgColor || '#f0f2f5',
                    }}
                  >
                    {result.riskCategory} Credit Score
                  </Tag>
                </div>
              </Col>
            </Row>
          </Card>

          {/* Loan Details */}
          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            <Col xs={12} sm={6}>
              <Card className="track-card track-stat-card">
                <Statistic title="Loan Requested" value={result.loanAmount} valueStyle={{ color: '#1890ff', fontSize: '1.2rem' }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card className="track-card track-stat-card">
                <Statistic title="Max Eligible" value={result.maxLoanEligible} valueStyle={{ color: '#52c41a', fontSize: '1.2rem' }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card className="track-card track-stat-card">
                <Statistic title="Interest Rate" value={result.interestRate} valueStyle={{ color: '#fa8c16', fontSize: '1.2rem' }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card className="track-card track-stat-card">
                <Statistic title="AI Confidence" value={`${Math.round(result.aiConfidence || 0)}%`} valueStyle={{ color: '#722ed1', fontSize: '1.2rem' }} />
              </Card>
            </Col>
          </Row>

          {/* Strengths & Improvements */}
          {(result.strengths?.length > 0 || result.improvements?.length > 0) && (
            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              {result.strengths?.length > 0 && (
                <Col xs={24} md={12}>
                  <Card
                    className="track-card"
                    title={<><CheckCircleOutlined style={{ color: '#52c41a' }} /> Your Strengths</>}
                    style={{ borderTop: '3px solid #52c41a' }}
                  >
                    <List
                      dataSource={result.strengths}
                      renderItem={(item) => (
                        <List.Item style={{ borderBottom: 'none', padding: '6px 0' }}>
                          <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                          {item}
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
              )}
              {result.improvements?.length > 0 && (
                <Col xs={24} md={12}>
                  <Card
                    className="track-card"
                    title={<>⚠️ Areas to Improve</>}
                    style={{ borderTop: '3px solid #fa8c16' }}
                  >
                    <List
                      dataSource={result.improvements}
                      renderItem={(item) => (
                        <List.Item style={{ borderBottom: 'none', padding: '6px 0' }}>
                          <span style={{ color: '#fa8c16', marginRight: 8 }}>⚠️</span>
                          {item}
                        </List.Item>
                      )}
                    />
                  </Card>
                </Col>
              )}
            </Row>
          )}

          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Link to="/">
              <Button type="primary" icon={<RocketOutlined />} size="large" style={{ marginRight: 12 }}>
                Apply Again
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button size="large">View Dashboard</Button>
            </Link>
          </div>
        </motion.div>
      )}

      {!result && !loading && !error && (
        <motion.div
          className="track-empty"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="track-empty-cards">
            {['IND-A1B2C3D4', 'SME-E5F6G7H8'].map((id) => (
              <Card
                key={id}
                className="track-example-card"
                hoverable
                onClick={() => setAppId(id)}
              >
                <Tag color={id.startsWith('IND') ? 'blue' : 'purple'}>{id}</Tag>
                <p>{id.startsWith('IND') ? 'Individual Application example' : 'SME Application example'}</p>
              </Card>
            ))}
          </div>
          <p style={{ color: '#9ca3af', marginTop: 8, fontSize: 13 }}>
            💡 Tip: Your Application ID was shown after form submission
          </p>
        </motion.div>
      )}
    </div>
  );
}

export default TrackApplication;
