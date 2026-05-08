import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Dropdown, Space, Tag } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  ShopOutlined,
  DashboardOutlined,
  SettingOutlined,
  BankOutlined,
  SearchOutlined,
  LoginOutlined,
  LogoutOutlined,
  LockOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import 'antd/dist/reset.css';
import './App.css';

import { AuthProvider, useAuth } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';

import Home from './pages/Home';
import IndividualForm from './pages/IndividualForm';
import SMEForm from './pages/SMEForm';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import CreditScore from './pages/CreditScore';
import Login from './pages/Login';
import TrackApplication from './pages/TrackApplication';
import NotFound from './pages/NotFound';
import EnginesPage from './pages/Engines';
import PsychometricQuiz from './pages/PsychometricQuiz';

const { Header, Content, Footer } = Layout;

function AppContent() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, adminUser, logout } = useAuth();

  const menuItems = [
    { key: '/',           icon: <HomeOutlined />,          label: <Link to="/">Home</Link> },
    { key: '/individual', icon: <UserOutlined />,          label: <Link to="/individual">Apply (Individual)</Link> },
    { key: '/sme',        icon: <ShopOutlined />,          label: <Link to="/sme">Apply (SME)</Link> },
    { key: '/track',      icon: <SearchOutlined />,        label: <Link to="/track">Track</Link> },
    { key: '/engines',    icon: <ThunderboltOutlined />,   label: <Link to="/engines">7 Engines</Link> },
    { key: '/dashboard',  icon: <DashboardOutlined />,     label: <Link to="/dashboard">Dashboard</Link> },
  ];

  const adminDropdownItems = isAuthenticated
    ? [
        { key: 'panel',  icon: <SettingOutlined />,  label: <Link to="/admin">Admin Panel</Link> },
        { type: 'divider' },
        {
          key: 'logout',
          icon: <LogoutOutlined />,
          label: 'Sign Out',
          danger: true,
          onClick: () => { logout(); navigate('/'); },
        },
      ]
    : [{ key: 'login', icon: <LoginOutlined />, label: <Link to="/login">Admin Login</Link> }];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="app-header">
        {/* Logo */}
        <Link to="/" className="app-logo">
          <BankOutlined className="app-logo-icon" />
          <span className="app-logo-text">Crededge</span>
          <Tag color="blue" className="app-logo-tag">AI</Tag>
        </Link>

        {/* Nav */}
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ flex: 1, minWidth: 0, background: 'transparent', borderBottom: 'none' }}
        />

        {/* Admin button */}
        <Dropdown menu={{ items: adminDropdownItems }} placement="bottomRight" arrow>
          <Space className="app-admin-btn" style={{ cursor: 'pointer', marginLeft: 16 }}>
            <Avatar
              size="small"
              icon={<LockOutlined />}
              style={{ background: isAuthenticated ? '#52c41a' : '#434343' }}
            />
            <span style={{ color: '#ffffffaa', fontSize: 13 }}>
              {isAuthenticated ? adminUser : 'Admin'}
            </span>
          </Space>
        </Dropdown>
      </Header>

      <Content style={{ padding: 0, background: '#f0f2f5' }}>
        <Routes>
          <Route path="/"           element={<Home />} />
          <Route path="/individual" element={<IndividualForm />} />
          <Route path="/sme"        element={<SMEForm />} />
          <Route path="/track"                   element={<TrackApplication />} />
          <Route path="/engines"                  element={<EnginesPage />} />
          <Route path="/psychometric"             element={<PsychometricQuiz />} />
          <Route path="/psychometric/demo"        element={<PsychometricQuiz />} />
          <Route path="/dashboard"               element={<Dashboard />} />
          <Route path="/score/:id"               element={<CreditScore />} />
          <Route path="/login"                   element={<Login />} />
          <Route
            path="/admin"
            element={
              <PrivateRoute>
                <AdminPanel />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Content>

      <Footer className="app-footer">
        <div className="footer-content">
          <span className="footer-brand"><BankOutlined /> Crededge</span>
          <span className="footer-copy">AI Credit Risk Assessment © {new Date().getFullYear()} | 4th Semester Mini Project</span>
          <span className="footer-links">
            <Link to="/track">Track Application</Link>
            {' · '}
            <Link to="/dashboard">Dashboard</Link>
          </span>
        </div>
      </Footer>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
