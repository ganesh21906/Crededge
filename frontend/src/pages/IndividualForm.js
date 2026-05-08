import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { submitIndividualApplication } from '../services/api';
import {
  Form,
  Input,
  Button,
  Select,
  DatePicker,
  InputNumber,
  Card,
  Steps,
  message,
  Radio,
  Checkbox,
  Alert,
  Divider,
  Space,
  Tag
} from 'antd';
import {
  UserOutlined,
  HomeOutlined,
  BankOutlined,
  FileTextOutlined,
  SafetyOutlined,
  RocketOutlined
} from '@ant-design/icons';
import './Form.css';

const { Option } = Select;
const { TextArea } = Input;

function IndividualForm() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const steps = [
    { title: 'Personal', icon: <UserOutlined /> },
    { title: 'Address', icon: <HomeOutlined /> },
    { title: 'Employment', icon: <BankOutlined /> },
    { title: 'Alternative Data', icon: <FileTextOutlined /> },
    { title: 'Loan Details', icon: <SafetyOutlined /> }
  ];

  const containerVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.4 }
    }
  };

  const onFinish = async () => {
    setLoading(true);
    try {
      const allValues = form.getFieldsValue(true);
      const payload = {
        ...allValues,
        dateOfBirth: allValues.dateOfBirth ? allValues.dateOfBirth.format('YYYY-MM-DD') : '',
        dependents: allValues.dependents ?? 0,
        hasBankAccount: allValues.hasBankAccount ?? false,
        hasUtilityBills: allValues.hasUtilityBills ?? false,
        hasRentalAgreement: allValues.hasRentalAgreement ?? false,
        hasUPIHistory: allValues.hasUPIHistory ?? false,
        hasSocialMedia: allValues.hasSocialMedia ?? false,
        repaymentPeriod: parseInt(allValues.repaymentPeriod) || 12,
      };
      const response = await submitIndividualApplication(payload);
      message.success('Application submitted successfully!');
      // ✅ Pass real score data to CreditScore via navigate state
      navigate(`/score/${response.applicationId}`, { state: { scoreData: response } });
    } catch (error) {
      let detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        detail = detail.map(e => `${e.loc?.slice(-1)}: ${e.msg}`).join(', ');
      } else if (typeof detail === 'object') {
        detail = JSON.stringify(detail);
      }
      message.error(detail || 'Failed to submit application. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><UserOutlined /> Personal Information</>} bordered={false}>
              <Form.Item
                name="fullName"
                label="Full Name"
                rules={[{ required: true, message: 'Please enter your full name' }]}
              >
                <Input size="large" placeholder="Enter your full name" />
              </Form.Item>

              <Form.Item
                name="dateOfBirth"
                label="Date of Birth"
                rules={[{ required: true, message: 'Please select your date of birth' }]}
              >
                <DatePicker size="large" style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="gender"
                label="Gender"
                rules={[{ required: true, message: 'Please select your gender' }]}
              >
                <Radio.Group size="large">
                  <Radio value="male">Male</Radio>
                  <Radio value="female">Female</Radio>
                  <Radio value="other">Other</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                name="maritalStatus"
                label="Marital Status"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select marital status">
                  <Option value="single">Single</Option>
                  <Option value="married">Married</Option>
                  <Option value="divorced">Divorced</Option>
                  <Option value="widowed">Widowed</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="dependents"
                label="Number of Dependents"
                rules={[{ required: true }]}
              >
                <InputNumber size="large" min={0} max={10} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="mobileNumber"
                label="Mobile Number"
                rules={[
                  { required: true, message: 'Please enter your mobile number' },
                  { pattern: /^[0-9]{10}$/, message: 'Please enter a valid 10-digit mobile number' }
                ]}
              >
                <Input size="large" placeholder="10-digit mobile number" />
              </Form.Item>

              <Form.Item
                name="email"
                label="Email Address"
                rules={[
                  { required: true, message: 'Please enter your email' },
                  { type: 'email', message: 'Please enter a valid email' }
                ]}
              >
                <Input size="large" placeholder="your.email@example.com" />
              </Form.Item>
            </Card>
          </motion.div>
        );

      case 1:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><HomeOutlined /> Address Information</>} bordered={false}>
              <Form.Item
                name="address"
                label="Street Address"
                rules={[{ required: true, message: 'Please enter your address' }]}
              >
                <TextArea size="large" rows={3} placeholder="Enter your complete address" />
              </Form.Item>

              <Form.Item
                name="city"
                label="City"
                rules={[{ required: true }]}
              >
                <Input size="large" placeholder="City" />
              </Form.Item>

              <Form.Item
                name="state"
                label="State"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select state" showSearch>
                  <Option value="Andhra Pradesh">Andhra Pradesh</Option>
                  <Option value="Karnataka">Karnataka</Option>
                  <Option value="Maharashtra">Maharashtra</Option>
                  <Option value="Tamil Nadu">Tamil Nadu</Option>
                  <Option value="Delhi">Delhi</Option>
                  {/* Add more states */}
                </Select>
              </Form.Item>

              <Form.Item
                name="pincode"
                label="Pincode"
                rules={[
                  { required: true },
                  { pattern: /^[0-9]{6}$/, message: 'Please enter a valid 6-digit pincode' }
                ]}
              >
                <Input size="large" placeholder="6-digit pincode" />
              </Form.Item>

              <Form.Item
                name="residenceType"
                label="Residence Type"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select residence type">
                  <Option value="owned">Owned</Option>
                  <Option value="rented">Rented</Option>
                  <Option value="parental">Parental Home</Option>
                  <Option value="company">Company Provided</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="yearsAtAddress"
                label="Years at Current Address"
                rules={[{ required: true }]}
              >
                <InputNumber size="large" min={0} max={100} style={{ width: '100%' }} />
              </Form.Item>
            </Card>
          </motion.div>
        );

      case 2:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><BankOutlined /> Employment & Income</>} bordered={false}>
              <Form.Item
                name="employmentType"
                label="Employment Type"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select employment type">
                  <Option value="salaried">Salaried</Option>
                  <Option value="self-employed">Self Employed</Option>
                  <Option value="freelancer">Freelancer</Option>
                  <Option value="business">Business Owner</Option>
                  <Option value="student">Student</Option>
                  <Option value="homemaker">Homemaker</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="employerName"
                label="Employer/Company Name"
                rules={[{ required: true }]}
              >
                <Input size="large" placeholder="Company name" />
              </Form.Item>

              <Form.Item
                name="monthlyIncome"
                label="Monthly Income (₹)"
                rules={[{ required: true, message: 'Please enter your monthly income' }]}
              >
                <InputNumber
                  size="large"
                  min={0}
                  style={{ width: '100%' }}
                  formatter={value => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/₹\s?|(,*)/g, '')}
                  placeholder="Enter monthly income"
                />
              </Form.Item>

              <Form.Item
                name="yearsEmployed"
                label="Years in Current Employment"
                rules={[{ required: true }]}
              >
                <InputNumber size="large" min={0} max={50} step={0.5} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="industryType"
                label="Industry"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select industry">
                  <Option value="it">Information Technology</Option>
                  <Option value="finance">Finance & Banking</Option>
                  <Option value="healthcare">Healthcare</Option>
                  <Option value="education">Education</Option>
                  <Option value="manufacturing">Manufacturing</Option>
                  <Option value="retail">Retail</Option>
                  <Option value="other">Other</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="qualification"
                label="Highest Qualification"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select qualification">
                  <Option value="10th">10th Pass</Option>
                  <Option value="12th">12th Pass</Option>
                  <Option value="diploma">Diploma</Option>
                  <Option value="graduate">Graduate</Option>
                  <Option value="postgraduate">Post Graduate</Option>
                  <Option value="professional">Professional Degree</Option>
                </Select>
              </Form.Item>

              <Divider />

              <Form.Item
                name="hasBankAccount"
                valuePropName="checked"
              >
                <Checkbox>I have a bank account</Checkbox>
              </Form.Item>

              <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => 
                  prevValues.hasBankAccount !== currentValues.hasBankAccount
                }
              >
                {({ getFieldValue }) =>
                  getFieldValue('hasBankAccount') ? (
                    <>
                      <Form.Item name="bankName" label="Bank Name">
                        <Input size="large" placeholder="Bank name" />
                      </Form.Item>
                      <Form.Item name="accountType" label="Account Type">
                        <Select size="large" placeholder="Select account type">
                          <Option value="savings">Savings</Option>
                          <Option value="current">Current</Option>
                        </Select>
                      </Form.Item>
                      <Form.Item name="averageBalance" label="Average Monthly Balance (₹)">
                        <InputNumber
                          size="large"
                          min={0}
                          style={{ width: '100%' }}
                          formatter={value => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                          parser={value => value.replace(/₹\s?|(,*)/g, '')}
                        />
                      </Form.Item>
                    </>
                  ) : null
                }
              </Form.Item>
            </Card>
          </motion.div>
        );

      case 3:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><FileTextOutlined /> Alternative Data Sources</>} bordered={false}>
              <Alert
                message="Boost Your Credit Score!"
                description="Providing alternative data sources can significantly improve your credit assessment and approval chances."
                type="info"
                showIcon
                style={{ marginBottom: '24px' }}
              />

              <Form.Item name="hasUtilityBills" valuePropName="checked">
                <Checkbox>
                  <Space>
                    <span><strong>Utility Bill Payments</strong></span>
                    <Tag color="green">+50 points</Tag>
                  </Space>
                  <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                    Regular electricity, water, mobile bill payments
                  </div>
                </Checkbox>
              </Form.Item>

              <Form.Item name="hasRentalAgreement" valuePropName="checked">
                <Checkbox>
                  <Space>
                    <span><strong>Rental Payment History</strong></span>
                    <Tag color="green">+40 points</Tag>
                  </Space>
                  <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                    Consistent rent payment records
                  </div>
                </Checkbox>
              </Form.Item>

              <Form.Item name="hasUPIHistory" valuePropName="checked">
                <Checkbox>
                  <Space>
                    <span><strong>UPI/Digital Payments</strong></span>
                    <Tag color="green">+60 points</Tag>
                  </Space>
                  <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                    Regular digital transaction history
                  </div>
                </Checkbox>
              </Form.Item>

              <Form.Item name="hasSocialMedia" valuePropName="checked">
                <Checkbox>
                  <Space>
                    <span><strong>Social Media Verification</strong></span>
                    <Tag color="blue">+30 points</Tag>
                  </Space>
                  <div style={{ color: '#8c8c8c', fontSize: '12px' }}>
                    LinkedIn, professional profiles
                  </div>
                </Checkbox>
              </Form.Item>

              <Divider />

              <Alert
                message="Data Privacy"
                description="All your data is encrypted and used only for credit assessment. We never share your information with third parties."
                type="success"
                showIcon
              />
            </Card>
          </motion.div>
        );

      case 4:
        return (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Card title={<><SafetyOutlined /> Loan Details</>} bordered={false}>
              <Form.Item
                name="loanAmount"
                label="Loan Amount Required (₹)"
                rules={[{ required: true, message: 'Please enter loan amount' }]}
              >
                <InputNumber
                  size="large"
                  min={10000}
                  max={10000000}
                  style={{ width: '100%' }}
                  formatter={value => `₹ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/₹\s?|(,*)/g, '')}
                  placeholder="Enter loan amount"
                />
              </Form.Item>

              <Form.Item
                name="loanPurpose"
                label="Loan Purpose"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select loan purpose">
                  <Option value="personal">Personal Use</Option>
                  <Option value="education">Education</Option>
                  <Option value="medical">Medical Emergency</Option>
                  <Option value="home">Home Improvement</Option>
                  <Option value="vehicle">Vehicle Purchase</Option>
                  <Option value="business">Business/Entrepreneurship</Option>
                  <Option value="debt">Debt Consolidation</Option>
                  <Option value="other">Other</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="repaymentPeriod"
                label="Preferred Repayment Period (Months)"
                rules={[{ required: true }]}
              >
                <Select size="large" placeholder="Select repayment period">
                  <Option value="6">6 Months</Option>
                  <Option value="12">12 Months</Option>
                  <Option value="24">24 Months</Option>
                  <Option value="36">36 Months</Option>
                  <Option value="48">48 Months</Option>
                  <Option value="60">60 Months</Option>
                </Select>
              </Form.Item>

              <Divider />

              <Alert
                message="Next Steps"
                description="After submission, our AI will analyze your application using the provided data. You'll receive your credit score and decision within minutes!"
                type="warning"
                showIcon
              />
            </Card>
          </motion.div>
        );

      default:
        return null;
    }
  };

  const next = () => {
    form.validateFields().then(() => {
      setCurrentStep(currentStep + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }).catch(() => {
      message.error('Please fill in all required fields');
    });
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{ background: '#f0f2f5', minHeight: '100vh', padding: '24px' }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ maxWidth: '900px', margin: '0 auto' }}
      >
        <Card style={{ marginBottom: '24px' }}>
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <h1 style={{ fontSize: '2rem', marginBottom: '8px', color: '#1f2937' }}>
              Individual Loan Application
            </h1>
            <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
              Complete the form to assess your creditworthiness using alternative data
            </p>
          </div>

          <Steps current={currentStep} items={steps} />
        </Card>

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          scrollToFirstError
        >
          {renderStepContent()}

          <Card style={{ marginTop: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              {currentStep > 0 && (
                <Button size="large" onClick={prev}>
                  Previous
                </Button>
              )}
              {currentStep < steps.length - 1 && (
                <Button type="primary" size="large" onClick={next} style={{ marginLeft: 'auto' }}>
                  Next
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
                  Submit Application
                </Button>
              )}
            </div>
          </Card>
        </Form>
      </motion.div>
    </div>
  );
}

export default IndividualForm;
