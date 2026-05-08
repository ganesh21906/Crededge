import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card, Table, Tag, Button, Input, Select, Space,
  Modal, Descriptions, Progress, Statistic, Row, Col,
  Badge, Avatar, Spin, message, Popconfirm, Divider
} from 'antd';
import {
  SettingOutlined, CheckCircleOutlined, CloseCircleOutlined,
  ReloadOutlined, UserOutlined, ShopOutlined,
  EyeOutlined, LogoutOutlined, ThunderboltOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { getAdminApplications, getAdminStats, reviewApplication } from '../services/api';
import { RISK_CATEGORIES } from '../constants';
import './AdminPanel.css';

const { Option } = Select;

function AdminPanel() {
  const navigate = useNavigate();
  const { adminUser, logout } = useAuth();

  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [filters, setFilters] = useState({ search: '', appType: 'all', reviewStatus: 'all' });
  const [loading, setLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [selectedApp, setSelectedApp] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [reviewLoading, setReviewLoading] = useState('');

  const loadData = useCallback(async (page = 1, f = filters) => {
    setTableLoading(true);
    try {
      const [appsData, statsData] = await Promise.all([
        getAdminApplications({
          skip: (page - 1) * pagination.pageSize,
          limit: pagination.pageSize,
          search: f.search,
          appType: f.appType,
          reviewStatus: f.reviewStatus,
        }),
        getAdminStats(),
      ]);
      setApplications(appsData.applications || []);
      setPagination((p) => ({ ...p, current: page, total: appsData.total || 0 }));
      setStats(statsData);
    } catch (err) {
      message.error('Failed to load data');
    } finally {
      setLoading(false);
      setTableLoading(false);
    }
  }, [pagination.pageSize, filters]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { loadData(1); }, []);

  const handleReview = async (appId, action) => {
    setReviewLoading(appId + action);
    try {
      await reviewApplication(appId, action);
      message.success(`Application ${action} successfully!`);
      setDetailVisible(false);
      loadData(pagination.current);
    } catch {
      message.error('Action failed. Please try again.');
    } finally {
      setReviewLoading('');
    }
  };

  const handleSearch = () => loadData(1, filters);
  const handleReset = () => {
    const f = { search: '', appType: 'all', reviewStatus: 'all' };
    setFilters(f);
    loadData(1, f);
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 160,
      render: (id) => <Tag style={{ fontFamily: 'monospace', fontSize: 11 }}>{id}</Tag>,
    },
    {
      title: 'Applicant',
      dataIndex: 'applicantName',
      key: 'name',
      render: (name, row) => (
        <Space>
          <Avatar size="small" icon={row.applicationType === 'Individual' ? <UserOutlined /> : <ShopOutlined />}
            style={{ background: row.applicationType === 'Individual' ? '#1890ff' : '#722ed1' }}
          />
          <div>
            <div style={{ fontWeight: 600, fontSize: 13 }}>{name}</div>
            <div style={{ fontSize: 11, color: '#9ca3af' }}>{row.email}</div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'applicationType',
      key: 'type',
      width: 110,
      render: (t) => <Tag color={t === 'Individual' ? 'geekblue' : 'purple'}>{t}</Tag>,
    },
    {
      title: 'Loan',
      dataIndex: 'loanAmount',
      key: 'loan',
      width: 130,
      render: (l) => <strong>{l}</strong>,
    },
    {
      title: 'Score',
      dataIndex: 'creditScore',
      key: 'score',
      width: 130,
      sorter: (a, b) => a.creditScore - b.creditScore,
      render: (score, row) => {
        const meta = RISK_CATEGORIES[row.riskCategory] || {};
        return (
          <Space direction="vertical" size={2}>
            <strong style={{ color: meta.color, fontSize: 16 }}>{score}</strong>
            <Tag color={meta.antColor} style={{ fontSize: 10 }}>{row.riskCategory}</Tag>
          </Space>
        );
      },
    },
    {
      title: 'AI Confidence',
      dataIndex: 'aiConfidence',
      key: 'confidence',
      width: 120,
      render: (c) => (
        <Progress
          percent={Math.round(c || 0)}
          size="small"
          strokeColor={c >= 85 ? '#52c41a' : c >= 70 ? '#1890ff' : '#fa8c16'}
          format={(p) => `${p}%`}
        />
      ),
    },
    {
      title: 'Review Status',
      dataIndex: 'status',
      key: 'status',
      width: 140,
      render: (s) => {
        const map = {
          pending:  { color: 'warning', dot: 'orange', label: 'Pending Review' },
          approved: { color: 'success', dot: 'green',  label: 'Approved' },
          rejected: { color: 'error',   dot: 'red',    label: 'Rejected' },
        };
        const m = map[s] || { color: 'default', dot: 'gray', label: s };
        return <Badge status={m.dot} text={<Tag color={m.color}>{m.label}</Tag>} />;
      },
    },
    {
      title: 'Date',
      dataIndex: 'submittedAt',
      key: 'date',
      width: 100,
      render: (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : '—',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 220,
      render: (_, row) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => { setSelectedApp(row); setDetailVisible(true); }}
          >
            Details
          </Button>
          {row.status === 'pending' && (
            <>
              <Popconfirm title="Approve this application?" onConfirm={() => handleReview(row.id, 'approved')} okText="Yes, Approve" cancelText="Cancel">
                <Button size="small" type="primary" icon={<CheckCircleOutlined />} loading={reviewLoading === row.id + 'approved'}>
                  Approve
                </Button>
              </Popconfirm>
              <Popconfirm title="Reject this application?" onConfirm={() => handleReview(row.id, 'rejected')} okText="Yes, Reject" okButtonProps={{ danger: true }} cancelText="Cancel">
                <Button size="small" danger icon={<CloseCircleOutlined />} loading={reviewLoading === row.id + 'rejected'}>
                  Reject
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}><Spin size="large" /></div>;
  }

  return (
    <div className="admin-page">
      {/* Header */}
      <motion.div className="admin-header" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div>
          <h1><SettingOutlined /> Admin Panel</h1>
          <p>Logged in as <strong>{adminUser}</strong></p>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => loadData(1)}>Refresh</Button>
          <Button icon={<LogoutOutlined />} danger onClick={() => { logout(); navigate('/'); }}>
            Sign Out
          </Button>
        </Space>
      </motion.div>

      {/* Stats */}
      {stats && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            {[
              { title: 'Total',         value: stats.totalApplications,   color: '#1890ff' },
              { title: 'Pending',       value: stats.pendingApplications, color: '#fa8c16' },
              { title: 'Approved',      value: stats.approvedApplications,color: '#52c41a' },
              { title: 'Rejected',      value: stats.rejectedApplications,color: '#f5222d' },
              { title: 'Approval Rate', value: `${stats.approvalRate}%`, color: '#722ed1' },
              { title: 'Avg Score',     value: stats.averageScore,        color: '#1890ff' },
            ].map((s) => (
              <Col xs={12} sm={8} md={4} key={s.title}>
                <Card className="admin-stat-card" hoverable>
                  <Statistic title={s.title} value={s.value} valueStyle={{ color: s.color, fontSize: '1.4rem', fontWeight: 700 }} />
                </Card>
              </Col>
            ))}
          </Row>
        </motion.div>
      )}

      {/* Table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Card title={<><ThunderboltOutlined /> Application Queue</>}>
          {/* Filters */}
          <Space wrap style={{ marginBottom: 16 }}>
            <Input.Search
              placeholder="Search name, ID, or email..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              onSearch={handleSearch}
              onPressEnter={handleSearch}
              style={{ width: 300 }}
              allowClear
            />
            <Select
              value={filters.appType}
              onChange={(v) => { const f = { ...filters, appType: v }; setFilters(f); loadData(1, f); }}
              style={{ width: 150 }}
            >
              <Option value="all">All Types</Option>
              <Option value="Individual">Individual</Option>
              <Option value="SME">SME</Option>
            </Select>
            <Select
              value={filters.reviewStatus}
              onChange={(v) => { const f = { ...filters, reviewStatus: v }; setFilters(f); loadData(1, f); }}
              style={{ width: 150 }}
            >
              <Option value="all">All Status</Option>
              <Option value="pending">Pending</Option>
              <Option value="approved">Approved</Option>
              <Option value="rejected">Rejected</Option>
            </Select>
            <Button onClick={handleReset}>Reset</Button>
          </Space>

          <Table
            columns={columns}
            dataSource={applications}
            rowKey="id"
            loading={tableLoading}
            scroll={{ x: 1200 }}
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: pagination.total,
              showTotal: (t) => `${t} total applications`,
              onChange: (page) => loadData(page),
              showSizeChanger: false,
            }}
            locale={{ emptyText: 'No applications match the current filters.' }}
          />
        </Card>
      </motion.div>

      {/* Detail Modal */}
      <Modal
        title={selectedApp ? `Application — ${selectedApp.id}` : ''}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        width={720}
        footer={
          selectedApp?.status === 'pending' ? (
            <Space>
              <Popconfirm title="Approve this application?" onConfirm={() => handleReview(selectedApp.id, 'approved')} okText="Yes, Approve">
                <Button type="primary" icon={<CheckCircleOutlined />} loading={reviewLoading === selectedApp?.id + 'approved'}>
                  Approve Application
                </Button>
              </Popconfirm>
              <Popconfirm title="Reject this application?" onConfirm={() => handleReview(selectedApp.id, 'rejected')} okText="Yes, Reject" okButtonProps={{ danger: true }}>
                <Button danger icon={<CloseCircleOutlined />} loading={reviewLoading === selectedApp?.id + 'rejected'}>
                  Reject Application
                </Button>
              </Popconfirm>
              <Button onClick={() => setDetailVisible(false)}>Close</Button>
            </Space>
          ) : (
            <Button type="primary" onClick={() => setDetailVisible(false)}>Close</Button>
          )
        }
      >
        {selectedApp && (
          <div>
            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Statistic title="Credit Score" value={selectedApp.creditScore}
                  valueStyle={{ color: RISK_CATEGORIES[selectedApp.riskCategory]?.color }}
                  suffix={<Tag color={RISK_CATEGORIES[selectedApp.riskCategory]?.antColor}>{selectedApp.riskCategory}</Tag>}
                />
              </Col>
              <Col span={12}>
                <Statistic title="AI Confidence" value={`${Math.round(selectedApp.aiConfidence || 0)}%`}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
            </Row>

            <Descriptions column={2} bordered size="small">
              <Descriptions.Item label="Applicant">{selectedApp.applicantName}</Descriptions.Item>
              <Descriptions.Item label="Type">{selectedApp.applicationType}</Descriptions.Item>
              <Descriptions.Item label="Email">{selectedApp.email}</Descriptions.Item>
              <Descriptions.Item label="Phone">{selectedApp.phone}</Descriptions.Item>
              <Descriptions.Item label="Loan Amount">{selectedApp.loanAmount}</Descriptions.Item>
              <Descriptions.Item label="Loan Purpose">{selectedApp.loanPurpose}</Descriptions.Item>
              <Descriptions.Item label="Max Eligible">{selectedApp.maxLoanEligible}</Descriptions.Item>
              <Descriptions.Item label="Interest Rate">{selectedApp.interestRate}</Descriptions.Item>
              <Descriptions.Item label="Approval Status">{selectedApp.approvalStatus}</Descriptions.Item>
              <Descriptions.Item label="Review Status">
                <Tag color={selectedApp.status === 'approved' ? 'success' : selectedApp.status === 'rejected' ? 'error' : 'warning'}>
                  {selectedApp.status?.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              {selectedApp.reviewedBy && (
                <Descriptions.Item label="Reviewed By" span={2}>{selectedApp.reviewedBy}</Descriptions.Item>
              )}
            </Descriptions>

            {selectedApp.strengths?.length > 0 && (
              <>
                <Divider>Strengths</Divider>
                {selectedApp.strengths.map((s, i) => (
                  <div key={i} style={{ marginBottom: 6 }}>
                    <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />{s}
                  </div>
                ))}
              </>
            )}

            {selectedApp.improvements?.length > 0 && (
              <>
                <Divider>Areas to Improve</Divider>
                {selectedApp.improvements.map((s, i) => (
                  <div key={i} style={{ marginBottom: 6 }}>
                    <span style={{ color: '#fa8c16', marginRight: 8 }}>⚠️</span>{s}
                  </div>
                ))}
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

export default AdminPanel;
