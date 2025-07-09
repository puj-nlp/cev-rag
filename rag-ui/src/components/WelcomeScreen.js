import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Add as AddIcon } from '@mui/icons-material';

const WelcomeRoot = styled(Box)(({ theme }) => ({
  flex: 1,
  textAlign: 'center',
  padding: theme.spacing(7.5, 5),
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  [theme.breakpoints.down('md')]: {
    padding: theme.spacing(5, 2.5)
  }
}));

const WelcomeTitle = styled(Typography)(({ theme }) => ({
  fontSize: '2.5rem',
  fontWeight: 700,
  color: '#1e3a8a',
  marginBottom: theme.spacing(2.5),
  textShadow: '0 2px 4px rgba(30, 58, 138, 0.1)',
  lineHeight: 1.2,
  [theme.breakpoints.down('md')]: {
    fontSize: '2rem'
  }
}));

const WelcomeDescription = styled(Typography)(({ theme }) => ({
  color: '#475569',
  fontSize: '1.1rem',
  lineHeight: 1.6,
  marginBottom: theme.spacing(5),
  maxWidth: '500px',
  marginLeft: 'auto',
  marginRight: 'auto'
}));

const StartChatButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
  color: 'white',
  border: 'none',
  padding: theme.spacing(2, 4),
  borderRadius: '10px',
  fontWeight: 600,
  fontSize: '16px',
  transition: 'all 0.3s ease',
  boxShadow: '0 4px 15px rgba(30, 58, 138, 0.3)',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 6px 20px rgba(30, 58, 138, 0.4)',
    background: 'linear-gradient(135deg, #1e40af 0%, #2563eb 100%)'
  }
}));

const TruthIcon = styled('div')(({ theme }) => ({
  fontSize: '4rem',
  marginBottom: theme.spacing(3),
  color: '#1e3a8a',
  opacity: 0.8
}));

const WelcomeScreen = ({ onStartNewChat }) => {
  return (
    <WelcomeRoot>
      <TruthIcon>
        🏛️
      </TruthIcon>
      <WelcomeTitle variant="h1">
        Welcome to Window to Truth!
      </WelcomeTitle>
      <WelcomeDescription variant="body1">
        Explore testimonies from Colombia's Truth Commission. Ask questions and get answers based on the compiled information.
      </WelcomeDescription>
      <StartChatButton 
        variant="contained"
        onClick={onStartNewChat}
        startIcon={
          <AddIcon sx={{ 
            fontSize: '20px !important',
            strokeWidth: 2 
          }} />
        }
      >
        Start New Chat
      </StartChatButton>
    </WelcomeRoot>
  );
};

export default WelcomeScreen;
