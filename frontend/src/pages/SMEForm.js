import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Form, Input, Button, Select, InputNumber, Card, Steps,
  message, Checkbox, Alert, Divider, Space, Tag, Row, Col
} from 'antd';
import {
  ShopOutlined, UserOutlined, HomeOutlined, BankOutlined,
  FileTextOutlined, SafetyOutlined, RocketOutlined, ThunderboltOutlined
} from '@ant-design/icons';
import { submitSMEApplication } from '../services/api';
import './Form.css';

const { Option } = Select;
const { TextArea } = Input;

const STATES = [
  'Andhra Pradesh','Bihar','Chhattisgarh','Delhi','Goa','Gujarat','Haryana',
  'Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh',
  'Maharashtra','Odisha','Punjab','Rajasthan','Tamil Nadu','Telangana',
  'Uttar Pradesh','Uttarakhand','West Bengal',
];

const containerVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.35 } },
};

function SMEForm() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);

  const steps = [
    { title: 'Business',   icon: <ShopOutlined /> },
    { title: 'Owner',      icon: <UserOutlined /> },
    { title: 'Address',    icon: <HomeOutlined /> },
    { title: 'Financials', icon: <BankOutlined /> },
    { title: 'Alt Data',   icon: <FileTextOutlined /> },
    { title: 'Loan',       icon: <SafetyOutlined /> },
  ];

  const onFinish = async () => {
    setLoading(true);
    try {
      const allValues = form.getFieldsValue(true);
      const payload = {
        ...allValues,
        yearOfEstablishment: parseInt(allValues.yearOfEstablishment) || new Date().getFullYear(),
        annualRevenue:        parseFloat(allValues.annualRevenue)       || 0,
        monthlyRevenue:       parseFloat(allValues.monthlyRevenue)      || 0,
        averageMonthlyProfit: parseFloat(allValues.averageMonthlyProfit)|| 0,
        averageBalance:       parseFloat(allValues.averageBalance)      || 0,
        monthlyTransactions:  parseInt(allValues.monthlyTransactions)   || 0,
        inventoryValue:       parseFloat(allValues.inventoryValue)      || 0,
        loanAmount:           parseFloat(allValues.loanAmount)          || 0,
        repaymentPeriod:      parseInt(allValues.repaymentPeriod)       || 12,
        hasGSTReturns:        allValues.hasGSTReturns   ?? false,
        hasITReturns:         allValues.hasITReturns    ?? false,
        hasBankAccount:       allValues.hasBankAccount  ?? false,
        hasBusinessWebsite:   allValues.hasBusinessWebsite ?? false,
        hasDigitalPresence:   allValues.hasDigitalPresence ?? false,
        hasUtilityBills:      allValues.hasUtilityBills ?? false,
        hasRentalAgreement:   allValues.hasRentalAgreement ?? false,
        hasInventory:         allValues.hasInventory    ?? false,
      };

      const response = await submitSMEApplication(payload);
      message.success('SME Application submitted successfully!');
      navigate(`/score/${response.applicationId}`, { state: { scoreData: response } });
    } catch (error) {
      let detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        detail = detail.map(e => `${e.loc?.slice(-1)}: ${e.msg}`).join(', ');
      } else if (typeof detail === 'object') {
        detail = JSON.stringify(detail);
      }
      message.error(detail || 'Failed to submit. Please check all required fields.');
    } finally {
      setLoading(false);
    }
  };

  const next = () => {
    form.validateFields().then(() => {
      setCurrentStep((s) => s + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }).catch(() => message.error('Please fill in all required fields'));
  };

  const prev = () => {
    setCurrentStep((s) => s - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderStep = () => {
    switch (currentStep) {
      // ── Step 0: Business Information ──────────────────────────
      case 0:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><ShopOutlined /> Business Information</>} bordered={false}>
              <Alert
                message="For Small & Medium Enterprises"
                description="We assess your business using alternative data — even without a traditional credit score."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item name="businessName" label="Business / Company Name" rules={[{ required: true }]}>
                    <Input size="large" placeholder="e.g., Kumar Traders Pvt Ltd" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="businessType" label="Business Type" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select type">
                      {['Retail Store', 'Manufacturing', 'Services', 'Wholesale Trading', 'Restaurant/Food', 'E-commerce', 'Other'].map((t) => (
                        <Option key={t} value={t.toLowerCase()}>{t}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="registrationType" label="Registration Type" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select registration">
                      <Option value="proprietorship">Proprietorship</Option>
                      <Option value="partnership">Partnership</Option>
                      <Option value="llp">LLP</Option>
                      <Option value="private-limited">Private Limited</Option>
                      <Option value="public-limited">Public Limited</Option>
                      <Option value="unregistered">Unregistered</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="yearOfEstablishment" label="Year of Establishment" rules={[{ required: true }]}>
                    <InputNumber size="large" min={1900} max={2026} style={{ width: '100%' }} placeholder="e.g., 2019" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="industryType" label="Industry Type" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select industry">
                      {['Retail','Manufacturing','IT/Technology','Healthcare','Education','Hospitality','Construction','Agriculture','Other'].map((i) => (
                        <Option key={i} value={i.toLowerCase()}>{i}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="numberOfEmployees" label="Number of Employees" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select range">
                      {['1-5','6-10','11-25','26-50','51-100','100+'].map((r) => (
                        <Option key={r} value={r}>{r}</Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="gstNumber" label="GST Number (if registered)">
                    <Input size="large" placeholder="e.g., 29ABCDE1234F1Z5" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="panNumber" label="Business PAN Number" rules={[{ required: true }, { pattern: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/, message: 'Invalid PAN format' }]}>
                    <Input size="large" placeholder="e.g., ABCDE1234F" style={{ textTransform: 'uppercase' }} />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </motion.div>
        );

      // ── Step 1: Owner / Contact ──────────────────────────────
      case 1:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><UserOutlined /> Owner / Contact Information</>} bordered={false}>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item name="ownerName" label="Owner / Authorized Person Name" rules={[{ required: true }]}>
                    <Input size="large" placeholder="e.g., Ramesh Kumar" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="designation" label="Designation" rules={[{ required: true }]}>
                    <Input size="large" placeholder="e.g., Proprietor, Managing Director" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="mobileNumber"
                    label="Mobile Number"
                    rules={[{ required: true }, { pattern: /^[0-9]{10}$/, message: 'Enter valid 10-digit number' }]}
                  >
                    <Input size="large" placeholder="10-digit mobile number" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="email" label="Email Address" rules={[{ required: true }, { type: 'email' }]}>
                    <Input size="large" placeholder="info@yourbusiness.com" />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </motion.div>
        );

      // ── Step 2: Business Address ─────────────────────────────
      case 2:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><HomeOutlined /> Business Address</>} bordered={false}>
              <Form.Item name="address" label="Registered / Business Address" rules={[{ required: true }]}>
                <TextArea size="large" rows={3} placeholder="Shop No 45, Commercial Complex, MG Road" />
              </Form.Item>
              <Row gutter={16}>
                <Col xs={24} md={8}>
                  <Form.Item name="city" label="City" rules={[{ required: true }]}>
                    <Input size="large" placeholder="City" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={8}>
                  <Form.Item name="state" label="State" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select state" showSearch>
                      {STATES.map((s) => <Option key={s} value={s}>{s}</Option>)}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={8}>
                  <Form.Item name="pincode" label="Pincode" rules={[{ required: true }, { pattern: /^[0-9]{6}$/, message: 'Enter valid 6-digit pincode' }]}>
                    <Input size="large" placeholder="6-digit pincode" />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </motion.div>
        );

      // ── Step 3: Financial Information ───────────────────────
      case 3:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><BankOutlined /> Financial Information</>} bordered={false}>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item name="annualRevenue" label="Annual Revenue (₹)" rules={[{ required: true }]}>
                    <InputNumber size="large" min={0} style={{ width: '100%' }}
                      formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
                      placeholder="e.g., 50,00,000"
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="monthlyRevenue" label="Average Monthly Revenue (₹)" rules={[{ required: true }]}>
                    <InputNumber size="large" min={0} style={{ width: '100%' }}
                      formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="averageMonthlyProfit" label="Average Monthly Profit (₹)" rules={[{ required: true }]}>
                    <InputNumber size="large" min={0} style={{ width: '100%' }}
                      formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Form.Item name="hasGSTReturns" valuePropName="checked" noStyle>
                  <Checkbox>
                    <Space>
                      <strong>GST Returns available (last 12 months)</strong>
                      <Tag color="green">+80 points</Tag>
                    </Space>
                  </Checkbox>
                </Form.Item>
                <Form.Item name="hasITReturns" valuePropName="checked" noStyle>
                  <Checkbox>
                    <Space>
                      <strong>Income Tax Returns available (last 2-3 years)</strong>
                      <Tag color="green">+40 points</Tag>
                    </Space>
                  </Checkbox>
                </Form.Item>
              </Space>

              <Divider />
              <h4 style={{ margin: '0 0 16px' }}>Banking</h4>
              <Form.Item name="hasBankAccount" valuePropName="checked">
                <Checkbox>Business has a bank account</Checkbox>
              </Form.Item>

              <Form.Item noStyle shouldUpdate={(p, c) => p.hasBankAccount !== c.hasBankAccount}>
                {({ getFieldValue }) => getFieldValue('hasBankAccount') ? (
                  <Row gutter={16}>
                    <Col xs={24} md={8}>
                      <Form.Item name="bankName" label="Bank Name">
                        <Input size="large" placeholder="e.g., HDFC Bank" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={8}>
                      <Form.Item name="accountType" label="Account Type">
                        <Select size="large" placeholder="Select type">
                          <Option value="current">Current Account</Option>
                          <Option value="cc-od">CC/OD Account</Option>
                          <Option value="savings">Savings Account</Option>
                        </Select>
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={8}>
                      <Form.Item name="averageBalance" label="Average Monthly Balance (₹)">
                        <InputNumber size="large" min={0} style={{ width: '100%' }}
                          formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                          parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
                        />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={8}>
                      <Form.Item name="monthlyTransactions" label="Monthly Transactions (count)">
                        <InputNumber size="large" min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>
                ) : null}
              </Form.Item>
            </Card>
          </motion.div>
        );

      // ── Step 4: Alternative Data ─────────────────────────────
      case 4:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><FileTextOutlined /> Alternative Data & Digital Presence</>} bordered={false}>
              <Alert
                message="More data = better score!"
                description="Each additional data source significantly improves your credit assessment accuracy."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Space direction="vertical" size={16} style={{ width: '100%' }}>
                <Form.Item name="hasBusinessWebsite" valuePropName="checked" noStyle>
                  <Checkbox>
                    <Space><strong>Business has a website</strong><Tag color="blue">+15 points</Tag></Space>
                  </Checkbox>
                </Form.Item>
                <Form.Item noStyle shouldUpdate={(p, c) => p.hasBusinessWebsite !== c.hasBusinessWebsite}>
                  {({ getFieldValue }) => getFieldValue('hasBusinessWebsite') ? (
                    <Form.Item name="websiteUrl" style={{ marginLeft: 24 }}>
                      <Input size="large" placeholder="https://www.yourbusiness.com" />
                    </Form.Item>
                  ) : null}
                </Form.Item>

                <Form.Item name="hasDigitalPresence" valuePropName="checked" noStyle>
                  <Checkbox>
                    <Space><strong>Active on social media (Facebook, Instagram, LinkedIn)</strong><Tag color="blue">+20 points</Tag></Space>
                  </Checkbox>
                </Form.Item>
                <Form.Item noStyle shouldUpdate={(p, c) => p.hasDigitalPresence !== c.hasDigitalPresence}>
                  {({ getFieldValue }) => getFieldValue('hasDigitalPresence') ? (
                    <Form.Item name="socialMediaLinks" style={{ marginLeft: 24 }}>
                      <Input size="large" placeholder="Facebook page link / Instagram handle" />
                    </Form.Item>
                  ) : null}
                </Form.Item>

                <Form.Item name="hasUtilityBills" valuePropName="checked" noStyle>
                  <Checkbox>
                    <Space><strong>Business utility bills available (last 6 months)</strong><Tag color="green">+40 points</Tag></Space>
                  </Checkbox>
                </Form.Item>

                <Form.Item name="hasRentalAgreement" valuePropName="checked" noStyle>
                  <Checkbox>
                    <Space><strong>Shop / office rental agreement available</strong><Tag color="green">+25 points</Tag></Space>
                  </Checkbox>
                </Form.Item>

                <Divider />
                <h4>Business Metrics</h4>
                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item name="customerBase" label="Approximate Customer Base">
                      <Select size="large" placeholder="Select range">
                        {['1-50','51-200','201-500','501-1000','1000+'].map((r) => <Option key={r} value={r}>{r}</Option>)}
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item name="supplierCount" label="Number of Suppliers">
                      <Select size="large" placeholder="Select range">
                        {['1-5','6-10','11-20','20+'].map((r) => <Option key={r} value={r}>{r}</Option>)}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item name="hasInventory" valuePropName="checked">
                  <Checkbox>Business maintains inventory</Checkbox>
                </Form.Item>
                <Form.Item noStyle shouldUpdate={(p, c) => p.hasInventory !== c.hasInventory}>
                  {({ getFieldValue }) => getFieldValue('hasInventory') ? (
                    <Form.Item name="inventoryValue" label="Approximate Inventory Value (₹)">
                      <InputNumber size="large" min={0} style={{ width: '100%' }}
                        formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
                      />
                    </Form.Item>
                  ) : null}
                </Form.Item>
              </Space>
            </Card>
          </motion.div>
        );

      // ── Step 5: Loan Requirements ────────────────────────────
      case 5:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><SafetyOutlined /> Loan Requirements</>} bordered={false}>
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item name="loanAmount" label="Loan Amount Required (₹)" rules={[{ required: true }]}>
                    <InputNumber size="large" min={50000} style={{ width: '100%' }}
                      formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="loanPurpose" label="Loan Purpose" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select purpose">
                      <Option value="working-capital">Working Capital</Option>
                      <Option value="expansion">Business Expansion</Option>
                      <Option value="equipment">Equipment Purchase</Option>
                      <Option value="inventory">Inventory Purchase</Option>
                      <Option value="renovation">Shop/Office Renovation</Option>
                      <Option value="debt">Debt Consolidation</Option>
                      <Option value="other">Other</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item name="repaymentPeriod" label="Preferred Repayment Period" rules={[{ required: true }]}>
                    <Select size="large" placeholder="Select period">
                      <Option value="12">12 Months (1 Year)</Option>
                      <Option value="24">24 Months (2 Years)</Option>
                      <Option value="36">36 Months (3 Years)</Option>
                      <Option value="60">60 Months (5 Years)</Option>
                      <Option value="84">84 Months (7 Years)</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Alert
                message="Ready to Submit!"
                description="Our AI will analyze your business using alternative data and provide an instant credit assessment."
                type="success"
                showIcon
                icon={<ThunderboltOutlined />}
              />
            </Card>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div style={{ background: '#f0f2f5', minHeight: '100vh', padding: '24px' }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ maxWidth: 900, margin: '0 auto' }}
      >
        <Card style={{ marginBottom: 24 }}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <h1 style={{ fontSize: '2rem', margin: '0 0 8px', color: '#1f2937' }}>
              SME Loan Application
            </h1>
            <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
              Complete all steps to get your AI-powered business credit assessment
            </p>
          </div>
          <Steps current={currentStep} items={steps} size="small" />
        </Card>

        <Form form={form} layout="vertical" onFinish={onFinish} scrollToFirstError>
          {renderStep()}

          <Card style={{ marginTop: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              {currentStep > 0 && (
                <Button size="large" onClick={prev}>← Previous</Button>
              )}
              {currentStep < steps.length - 1 && (
                <Button type="primary" size="large" onClick={next} style={{ marginLeft: 'auto' }}>
                  Next →
                </Button>
              )}
              {currentStep === steps.length - 1 && (
                <Button
                  type="primary"
                  size="large"
                  htmlType="submit"
                  loading={loading}
                  icon={<RocketOutlined />}
                  style={{ marginLeft: 'auto' }}
                >
                  Submit & Get Credit Score
                </Button>
              )}
            </div>
          </Card>
        </Form>
      </motion.div>
    </div>
  );
}

export default SMEForm;
