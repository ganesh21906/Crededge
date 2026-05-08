import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from 'antd';
import { HomeOutlined, SearchOutlined } from '@ant-design/icons';
import './NotFound.css';

function NotFound() {
  return (
    <div className="notfound-page">
      <motion.div
        className="notfound-content"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, type: 'spring' }}
      >
        <motion.div
          className="notfound-number"
          initial={{ y: -20 }}
          animate={{ y: 0 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 120 }}
        >
          404
        </motion.div>
        <h1>Page Not Found</h1>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <div className="notfound-actions">
          <Link to="/">
            <Button type="primary" size="large" icon={<HomeOutlined />} className="notfound-btn-home">
              Back to Home
            </Button>
          </Link>
          <Link to="/track">
            <Button size="large" icon={<SearchOutlined />}>
              Track Application
            </Button>
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

export default NotFound;
