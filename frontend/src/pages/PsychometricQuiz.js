import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Button, Progress, Tag, Alert, Spin } from 'antd';
import { CheckCircleOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { getPsychometricQuestions, submitPsychometric } from '../services/api';
import './PsychometricQuiz.css';

const CATEGORY_COLORS = {
  'Financial IQ':       '#6366f1',
  'Future Orientation': '#8b5cf6',
  'Risk Attitude':      '#14b8a6',
  'Integrity':          '#f97316',
};

export default function PsychometricQuiz() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const appId     = location.state?.applicationId || new URLSearchParams(location.search).get('id') || '';

  const [questions, setQuestions] = useState([]);
  const [current,   setCurrent]   = useState(0);
  const [answers,   setAnswers]   = useState({});
  const [stage,     setStage]     = useState('intro');  // intro|quiz|result
  const [result,    setResult]    = useState(null);
  const [loading,   setLoading]   = useState(false);

  useEffect(() => {
    getPsychometricQuestions()
      .then((d) => setQuestions(d.questions || []))
      .catch(() => setQuestions(DEMO_QUESTIONS));
  }, []);

  const q = questions[current];
  const progress = questions.length > 0 ? Math.round((Object.keys(answers).length / questions.length) * 100) : 0;
  const answered = answers[q?.id] !== undefined;

  const handleAnswer = (idx) => {
    setAnswers((prev) => ({ ...prev, [q.id]: idx }));
  };

  const handleNext = () => {
    if (current < questions.length - 1) {
      setCurrent((c) => c + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrev = () => {
    if (current > 0) setCurrent((c) => c - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await submitPsychometric(appId, answers);
      setResult(res);
      setStage('result');
    } catch (e) {
      // Demo mode — show result without API
      const mockResult = {
        psychometricScore: 78,
        bonusAdded:        47,
        newScore:          null,
        breakdown:         { financialIQ: 82, futureOrientation: 76, riskAttitude: 71, integrity: 85, consistencyBonus: 10 },
      };
      setResult(mockResult);
      setStage('result');
    } finally {
      setLoading(false);
    }
  };

  /* ── Intro Screen ── */
  if (stage === 'intro') {
    return (
      <div className="quiz-wrapper">
        <motion.div className="quiz-intro-card" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
          <div className="quiz-intro-icon">🧠</div>
          <h1 className="quiz-intro-title">Psychometric Assessment</h1>
          <p className="quiz-intro-sub">
            15 questions assessing your Financial IQ, Future Orientation, Risk Attitude, and Integrity.
            Completing this quiz can add up to <strong>+60 points</strong> to your credit score.
          </p>
          {appId && (
            <div className="quiz-app-id">
              Application ID: <strong>{appId}</strong>
            </div>
          )}
          <div className="quiz-categories">
            {[
              { cat: 'Financial IQ', icon: '🧮', desc: '5 questions', pts: '+25 pts' },
              { cat: 'Future Orientation', icon: '🔮', desc: '4 questions', pts: '+18 pts' },
              { cat: 'Risk Attitude', icon: '⚖️', desc: '3 questions', pts: '+12 pts' },
              { cat: 'Integrity', icon: '🤝', desc: '3 questions', pts: '+8 pts' },
            ].map((c) => (
              <div key={c.cat} className="quiz-category-pill" style={{ borderColor: CATEGORY_COLORS[c.cat] }}>
                <span>{c.icon}</span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '13px' }}>{c.cat}</div>
                  <div style={{ fontSize: '11px', color: '#6b7280' }}>{c.desc} · <span style={{ color: CATEGORY_COLORS[c.cat] }}>{c.pts}</span></div>
                </div>
              </div>
            ))}
          </div>
          <div className="quiz-info-row">
            <span>⏱ About 5 minutes</span>
            <span>📖 No wrong answers, just be honest</span>
            <span>🔒 Responses are private</span>
          </div>
          <Button type="primary" size="large" block icon={<ArrowRightOutlined />}
            onClick={() => setStage('quiz')} disabled={questions.length === 0}>
            Start Assessment
          </Button>
        </motion.div>
      </div>
    );
  }

  /* ── Result Screen ── */
  if (stage === 'result') {
    const score     = result?.psychometricScore ?? 0;
    const bonus     = result?.bonusAdded ?? result?.psychometricBonus ?? 0;
    const newScore  = result?.newScore;
    const breakdown = result?.breakdown || {};
    const grade     = score >= 85 ? 'Excellent' : score >= 70 ? 'Good' : score >= 55 ? 'Fair' : 'Needs Improvement';
    const gradeColor = score >= 85 ? '#10b981' : score >= 70 ? '#3b82f6' : score >= 55 ? '#f59e0b' : '#ef4444';

    return (
      <div className="quiz-wrapper">
        <motion.div className="quiz-result-card" initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
          <div className="quiz-result-trophy">🏆</div>
          <h1 className="quiz-result-title">Assessment Complete!</h1>

          <div className="quiz-result-score-ring" style={{ borderColor: gradeColor }}>
            <div className="quiz-score-number" style={{ color: gradeColor }}>{score}</div>
            <div className="quiz-score-label">/ 100</div>
            <div className="quiz-grade" style={{ color: gradeColor }}>{grade}</div>
          </div>

          <div className="quiz-bonus-badge">
            +{bonus} pts added to your credit score
          </div>

          {newScore && (
            <div style={{ textAlign: 'center', margin: '8px 0 16px', color: '#6b7280' }}>
              Your new credit score: <strong style={{ fontSize: '1.3rem', color: '#1f2937' }}>{newScore}</strong>
            </div>
          )}

          <div className="quiz-breakdown">
            {[
              { key: 'financialIQ',       label: 'Financial IQ',       icon: '🧮', color: '#6366f1' },
              { key: 'futureOrientation', label: 'Future Orientation',  icon: '🔮', color: '#8b5cf6' },
              { key: 'riskAttitude',      label: 'Risk Attitude',       icon: '⚖️', color: '#14b8a6' },
              { key: 'integrity',         label: 'Integrity',           icon: '🤝', color: '#f97316' },
            ].map((cat) => (
              <div key={cat.key} className="quiz-breakdown-row">
                <span>{cat.icon} {cat.label}</span>
                <div style={{ flex: 1, margin: '0 12px' }}>
                  <Progress
                    percent={breakdown[cat.key] ?? 0}
                    strokeColor={cat.color}
                    size="small"
                    showInfo={false}
                  />
                </div>
                <span style={{ fontWeight: 700, color: cat.color, width: 36, textAlign: 'right' }}>
                  {breakdown[cat.key] ?? 0}%
                </span>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
            {appId && (
              <Button type="primary" block onClick={() => navigate(`/score/${appId}`)}>
                View Updated Score →
              </Button>
            )}
            <Button block onClick={() => navigate('/engines')}>
              Explore Other Engines
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  /* ── Quiz Screen ── */
  if (!q) return <div className="quiz-wrapper"><Spin size="large" /></div>;

  const catColor = CATEGORY_COLORS[q.category] || '#6366f1';

  return (
    <div className="quiz-wrapper">
      <div className="quiz-progress-bar">
        <Progress
          percent={progress}
          strokeColor={{ '0%': '#6366f1', '100%': '#8b5cf6' }}
          showInfo={false}
          style={{ width: '100%', maxWidth: 600 }}
        />
        <div className="quiz-progress-text">
          {current + 1} / {questions.length}
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={current}
          className="quiz-question-card"
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -50, opacity: 0 }}
          transition={{ duration: 0.25 }}
        >
          <div className="quiz-question-header">
            <Tag color={catColor} style={{ fontSize: '13px', padding: '3px 12px' }}>
              {q.icon} {q.category}
            </Tag>
          </div>

          <h2 className="quiz-question-text">{q.text}</h2>

          <div className="quiz-options">
            {q.options.map((opt, i) => (
              <motion.button
                key={i}
                className={`quiz-option ${answers[q.id] === i ? 'selected' : ''}`}
                style={answers[q.id] === i ? { borderColor: catColor, background: catColor + '15' } : {}}
                onClick={() => handleAnswer(i)}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
              >
                <span className="quiz-option-letter" style={{ background: answers[q.id] === i ? catColor : '#f3f4f6', color: answers[q.id] === i ? '#fff' : '#6b7280' }}>
                  {String.fromCharCode(65 + i)}
                </span>
                {opt}
              </motion.button>
            ))}
          </div>

          {q.explanation && answered && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Alert
                message={`💡 ${q.explanation}`}
                type="info"
                style={{ marginTop: 16, fontSize: '13px' }}
              />
            </motion.div>
          )}

          <div className="quiz-nav">
            <Button onClick={handlePrev} disabled={current === 0}>← Previous</Button>
            <Button
              type="primary"
              onClick={handleNext}
              disabled={!answered}
              loading={loading}
              icon={current === questions.length - 1 ? <CheckCircleOutlined /> : <ArrowRightOutlined />}
            >
              {current === questions.length - 1 ? 'Submit & Get Score' : 'Next Question'}
            </Button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

const DEMO_QUESTIONS = [
  { id: 'fin_01', category: 'Financial IQ', icon: '🧮', text: 'If you borrow ₹50,000 at 12% annual interest for 1 year, how much do you repay in total?', options: ['₹50,600', '₹56,000', '₹51,200', '₹50,120'], explanation: '12% of ₹50,000 = ₹6,000 interest → total ₹56,000' },
  { id: 'fut_02', category: 'Future Orientation', icon: '🔮', text: 'Would you prefer ₹1,000 today or ₹1,400 in 6 months?', options: ['₹1,000 today', '₹1,400 in 6 months'], explanation: '₹1,400 in 6 months is a 40% return — patience signals creditworthiness' },
  { id: 'risk_01', category: 'Risk Attitude', icon: '⚖️', text: 'A business idea promises 30% returns but 40% chance of failure. Would you invest?', options: ['Only if I can afford to lose', 'Absolutely — great returns', 'No, I prefer safer options', 'Invest half, keep half safe'], explanation: 'Balanced risk attitude is optimal for creditworthiness' },
  { id: 'int_01', category: 'Integrity', icon: '🤝', text: 'If you can\'t repay a loan EMI on time, what do you do?', options: ['Contact the lender immediately', 'Wait to see if lender notices', 'Ignore it and pay later', 'Avoid all contact'], explanation: 'Proactive communication with lenders is crucial for trust' },
];
