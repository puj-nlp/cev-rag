import React from 'react';
import { Box, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

const WindowRoot = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
  border: '2px solid #cbd5e1',
  borderRadius: '12px',
  boxShadow: `
    0 10px 25px rgba(30, 58, 138, 0.1),
    0 4px 10px rgba(30, 58, 138, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.6)
  `,
  backdropFilter: 'blur(10px)',
  position: 'relative',
  overflow: 'hidden',
  margin: theme.spacing(2),
  [theme.breakpoints.down('md')]: {
    margin: theme.spacing(1),
  }
}));

const WindowHeader = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%)',
  padding: theme.spacing(1.5, 2),
  borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between'
}));

const WindowTitle = styled(Box)(({ theme }) => ({
  color: 'white',
  fontWeight: 600,
  fontSize: '14px',
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1)
}));

const WindowControls = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1)
}));

const WindowControl = styled(Box)(({ theme, color }) => ({
  width: '12px',
  height: '12px',
  borderRadius: '50%',
  cursor: 'pointer',
  transition: 'opacity 0.2s ease',
  backgroundColor: color,
  '&:hover': {
    opacity: 0.8
  }
}));

const WindowContent = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2.5),
  minHeight: '70vh',
  background: 'rgba(255, 255, 255, 0.95)',
  position: 'relative',
  display: 'flex',
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    padding: theme.spacing(2)
  }
}));

const TruthIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
  </svg>
);

const WindowContainer = ({ children }) => {
  return (
    <WindowRoot>
      {/* Window Header */}
      <WindowHeader>
        <WindowTitle>
          <TruthIcon />
          <Typography component="span" sx={{ fontSize: 'inherit', fontWeight: 'inherit', color: 'inherit' }}>
            Ventana a la Verdad
          </Typography>
        </WindowTitle>
        <WindowControls>
          <WindowControl color="#ef4444" />
          <WindowControl color="#f59e0b" />
          <WindowControl color="#10b981" />
        </WindowControls>
      </WindowHeader>

      {/* Main Content */}
      <WindowContent>
        {children}
      </WindowContent>
    </WindowRoot>
  );
};

export default WindowContainer;
