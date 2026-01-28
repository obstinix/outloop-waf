import { useState, useEffect } from 'react';

/**
 * GravityStatus Component
 * 
 * Displays the current gravity state from the API.
 * Includes subtle animation effects based on status.
 */
export default function GravityStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGravityStatus = async () => {
      try {
        const response = await fetch('/api/gravity');
        const data = await response.json();
        setStatus(data);
        setLoading(false);
      } catch (err) {
        setError('Unable to fetch gravity status');
        setLoading(false);
      }
    };

    fetchGravityStatus();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchGravityStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingPulse}></div>
        <span style={styles.loadingText}>Checking gravitational field...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={{...styles.indicator, ...styles.indicatorError}}></div>
        <span style={styles.errorText}>{error}</span>
      </div>
    );
  }

  const isAntigravity = status?.status === 'disabled 🚀';
  
  return (
    <div style={{
      ...styles.container,
      ...(isAntigravity ? styles.containerAntigravity : {})
    }}>
      <div style={styles.statusHeader}>
        <div style={{
          ...styles.indicator,
          ...(isAntigravity ? styles.indicatorAntigravity : styles.indicatorNormal)
        }}></div>
        <span style={styles.label}>Gravity Status</span>
      </div>
      
      <div style={styles.statusValue}>
        {status?.status || 'Unknown'}
      </div>
      
      <div style={styles.details}>
        <div style={styles.detailRow}>
          <span style={styles.detailLabel}>Constant</span>
          <span style={styles.detailValue}>
            {status?.gravity_constant} {status?.unit}
          </span>
        </div>
        {status?.source && (
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>Source</span>
            <span style={styles.detailValue}>{status.source}</span>
          </div>
        )}
      </div>
      
      {isAntigravity && (
        <div style={styles.specialMessage}>
          {status?.message}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    background: 'rgba(255, 255, 255, 0.02)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    borderRadius: '1rem',
    padding: '1.5rem',
    transition: 'all 0.5s ease',
  },
  containerAntigravity: {
    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
    borderColor: 'rgba(168, 85, 247, 0.3)',
    animation: 'floatUp 3s ease-in-out infinite',
  },
  statusHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    marginBottom: '1rem',
  },
  indicator: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    transition: 'all 0.3s',
  },
  indicatorNormal: {
    background: '#22c55e',
    boxShadow: '0 0 10px rgba(34, 197, 94, 0.5)',
  },
  indicatorAntigravity: {
    background: '#a855f7',
    boxShadow: '0 0 20px rgba(168, 85, 247, 0.7)',
    animation: 'glow 1.5s ease-in-out infinite alternate',
  },
  indicatorError: {
    background: '#ef4444',
    boxShadow: '0 0 10px rgba(239, 68, 68, 0.5)',
  },
  label: {
    fontSize: '0.875rem',
    color: '#94a3b8',
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  statusValue: {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: '#f1f5f9',
    marginBottom: '1.25rem',
  },
  details: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.875rem',
  },
  detailLabel: {
    color: '#64748b',
  },
  detailValue: {
    color: '#94a3b8',
    fontFamily: 'monospace',
  },
  specialMessage: {
    marginTop: '1rem',
    padding: '0.75rem',
    background: 'rgba(168, 85, 247, 0.1)',
    borderRadius: '0.5rem',
    fontSize: '0.875rem',
    color: '#c4b5fd',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  loadingPulse: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: 'rgba(59, 130, 246, 0.2)',
    margin: '0 auto 1rem',
    animation: 'pulse 1.5s ease-in-out infinite',
  },
  loadingText: {
    color: '#64748b',
    fontSize: '0.875rem',
    textAlign: 'center',
    display: 'block',
  },
  errorText: {
    color: '#f87171',
    fontSize: '0.875rem',
    textAlign: 'center',
    display: 'block',
  },
};

// Add keyframes via style injection
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes floatUp {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-8px); }
    }
    @keyframes glow {
      0% { box-shadow: 0 0 10px rgba(168, 85, 247, 0.5); }
      100% { box-shadow: 0 0 25px rgba(168, 85, 247, 0.9); }
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 0.5; }
      50% { transform: scale(1.1); opacity: 1; }
    }
  `;
  document.head.appendChild(styleSheet);
}
