import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, Row, Col, Statistic, Button, Tag } from 'antd';
import { 
  RocketOutlined, 
  ThunderboltOutlined, 
  SafetyOutlined,
  UserOutlined,
  ShopOutlined,
  MobileOutlined,
  BulbOutlined,
  HomeOutlined,
  FileTextOutlined,
  BookOutlined,
  BankOutlined
} from '@ant-design/icons';
import './Home.css';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 100
    }
  }
};

const cardHover = {
  scale: 1.05,
  boxShadow: "0 20px 50px rgba(0,0,0,0.15)",
  transition: { type: "spring", stiffness: 300 }
};

function Home() {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <motion.div 
        className="hero-section"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Tag color="blue" style={{ fontSize: '14px', padding: '8px 16px', marginBottom: '20px' }}>
          <ThunderboltOutlined /> AI-Powered Platform
        </Tag>
        <h1>AI-Powered Credit Risk Assessment</h1>
        <p className="subtitle">Empowering Financial Inclusion Through Alternative Data</p>
        <p className="description">
          Traditional credit scoring systems exclude millions of creditworthy individuals and 
          businesses. Our AI-driven platform uses alternative data sources to provide fair, 
          accurate credit assessments for underserved segments.
        </p>
      </motion.div>

      {/* Features Section */}
      <div className="features-section">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          How It Works
        </motion.h2>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <Row gutter={[24, 24]}>
            <Col xs={24} md={8}>
              <motion.div variants={itemVariants} whileHover={cardHover}>
                <Card className="feature-card-modern" hoverable>
                  <RocketOutlined className="feature-icon-modern" />
                  <h3>Apply Online</h3>
                  <p>Submit your application with alternative data sources like utility bills, UPI transactions, and employment history</p>
                </Card>
              </motion.div>
            </Col>
            <Col xs={24} md={8}>
              <motion.div variants={itemVariants} whileHover={cardHover}>
                <Card className="feature-card-modern" hoverable>
                  <SafetyOutlined className="feature-icon-modern" />
                  <h3>AI Analysis</h3>
                  <p>Our ML models analyze multiple data points to assess creditworthiness beyond traditional scores</p>
                </Card>
              </motion.div>
            </Col>
            <Col xs={24} md={8}>
              <motion.div variants={itemVariants} whileHover={cardHover}>
                <Card className="feature-card-modern" hoverable>
                  <ThunderboltOutlined className="feature-icon-modern" />
                  <h3>Instant Decision</h3>
                  <p>Get your credit score and eligibility results in real-time with transparent explanations</p>
                </Card>
              </motion.div>
            </Col>
          </Row>
        </motion.div>
      </div>

      {/* CTA Section */}
      <div className="cta-section">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          Get Started
        </motion.h2>
        <p>Choose your application type or track an existing application</p>
        <Row gutter={[32, 32]} style={{ marginTop: '2rem' }}>
          <Col xs={24} md={8}>
            <motion.div
              whileHover={{ scale: 1.03, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Link to="/individual">
                <Card className="cta-card-modern" hoverable>
                  <UserOutlined className="cta-icon-modern" />
                  <h3>Individual Application</h3>
                  <p>For first-time borrowers, gig workers, and individuals with limited credit history</p>
                  <Button type="primary" size="large" block icon={<RocketOutlined />}>
                    Apply Now
                  </Button>
                </Card>
              </Link>
            </motion.div>
          </Col>
          <Col xs={24} md={8}>
            <motion.div
              whileHover={{ scale: 1.03, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Link to="/sme">
                <Card className="cta-card-modern" hoverable>
                  <ShopOutlined className="cta-icon-modern" />
                  <h3>SME Application</h3>
                  <p>For small and medium enterprises seeking working capital and business loans</p>
                  <Button type="primary" size="large" block icon={<RocketOutlined />}>
                    Apply Now
                  </Button>
                </Card>
              </Link>
            </motion.div>
          </Col>
          <Col xs={24} md={8}>
            <motion.div
              whileHover={{ scale: 1.03, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Link to="/track">
                <Card className="cta-card-modern" hoverable style={{ borderTop: '3px solid #722ed1' }}>
                  <FileTextOutlined className="cta-icon-modern" style={{ color: '#722ed1' }} />
                  <h3>Track Application</h3>
                  <p>Already applied? Enter your Application ID to check real-time status and credit score</p>
                  <Button size="large" block>
                    Track Status
                  </Button>
                </Card>
              </Link>
            </motion.div>
          </Col>
        </Row>
      </div>

      {/* Data Sources Section */}
      <div className="data-sources-section">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          Alternative Data Sources We Consider
        </motion.h2>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <Row gutter={[16, 16]}>
            {[
              { icon: <MobileOutlined />, title: 'Digital Payments', desc: 'UPI transactions, mobile wallets, payment regularity' },
              { icon: <BulbOutlined />, title: 'Utility Bills', desc: 'Electricity, water, mobile bill payment history' },
              { icon: <HomeOutlined />, title: 'Rental Payments', desc: 'Consistent rent payment records' },
              { icon: <FileTextOutlined />, title: 'GST Records', desc: 'Business registration and tax compliance' },
              { icon: <BookOutlined />, title: 'Education', desc: 'Qualifications and skill certifications' },
              { icon: <BankOutlined />, title: 'Employment', desc: 'Job stability and income verification' }
            ].map((item, index) => (
              <Col xs={24} sm={12} md={8} key={index}>
                <motion.div variants={itemVariants} whileHover={{ scale: 1.05 }}>
                  <Card className="data-card-modern" hoverable>
                    <div className="data-icon-modern">{item.icon}</div>
                    <h4>{item.title}</h4>
                    <p>{item.desc}</p>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>
        </motion.div>
      </div>

      {/* Stats Section */}
      <motion.div 
        className="stats-section"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <Row gutter={[32, 32]}>
          <Col xs={24} md={8}>
            <Card className="stat-card-modern">
              <Statistic
                title="Applications Processed"
                value={850}
                suffix="+"
                valueStyle={{ color: '#3f8600', fontSize: '3rem' }}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="stat-card-modern">
              <Statistic
                title="Approval Rate"
                value={78}
                suffix="%"
                valueStyle={{ color: '#1890ff', fontSize: '3rem' }}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="stat-card-modern">
              <Statistic
                title="Average Processing Time"
                value="< 5"
                suffix="min"
                valueStyle={{ color: '#cf1322', fontSize: '3rem' }}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>
    </div>
  );
}

export default Home;
