import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Card, Alert } from 'antd';
import { LockOutlined, UserOutlined, BankOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import './Login.css';

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loginError, loginLoading } = useAuth();
  const [form] = Form.useForm();

  const from = location.state?.from?.pathname || '/admin';

  const onFinish = async ({ username, password }) => {
    const success = await login(username, password);
    if (success) {
      navigate(from, { replace: true });
    }
  };

  return (
    <div className="login-page">
      {/* Animated background blobs */}
      <div className="login-bg">
        <div className="bg-blob blob-1" />
        <div className="bg-blob blob-2" />
        <div className="bg-blob blob-3" />
      </div>

      <motion.div
        className="login-container"
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, type: 'spring', stiffness: 100 }}
      >
        {/* Logo */}
        <motion.div
          className="login-logo"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
        >
          <BankOutlined className="login-logo-icon" />
        </motion.div>

        <h1 className="login-title">Crededge Admin</h1>
        <p className="login-subtitle">Secure access to application management</p>

        <Card className="login-card" bordered={false}>
          {loginError && (
            <Alert
              message={loginError}
              type="error"
              showIcon
              style={{ marginBottom: 24 }}
              closable
            />
          )}

          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            requiredMark={false}
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: 'Please enter your username' }]}
            >
              <Input
                size="large"
                prefix={<UserOutlined className="login-input-icon" />}
                placeholder="Admin username"
                className="login-input"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Please enter your password' }]}
            >
              <Input.Password
                size="large"
                prefix={<LockOutlined className="login-input-icon" />}
                placeholder="Password"
                className="login-input"
                iconRender={(visible) =>
                  visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                }
              />
            </Form.Item>

            <Button
              type="primary"
              htmlType="submit"
              size="large"
              loading={loginLoading}
              block
              className="login-btn"
            >
              {loginLoading ? 'Authenticating...' : 'Sign In to Admin Panel'}
            </Button>
          </Form>

          <div className="login-hint">
            <LockOutlined /> Demo credentials: <strong>admin</strong> / <strong>admin123</strong>
          </div>
        </Card>

        <p className="login-back">
          <a href="/">← Back to Crededge</a>
        </p>
      </motion.div>
    </div>
  );
}

export default Login;
