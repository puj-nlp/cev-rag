import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box, Avatar, IconButton } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { QuestionMark } from '@mui/icons-material';

const Header = () => {
  const location = useLocation();

  return (
    <AppBar position="static" elevation={0} sx={{ backgroundColor: '#e6e6e6' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
          {/* Logo and title */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <img 
              src="/cev_icon.png" 
              alt="CEV Icon" 
              style={{ 
                width: '24px', 
                height: '24px', 
                marginRight: '8px',
                //filter: 'brightness(0) invert(1)' // Makes the icon white
              }} 
            />
            <Typography
              noWrap
              sx={{
                fontWeight: 700,
                color: 'primary.main'
              }}
            >
              Ventana a la Verdad!
            </Typography>
          </Box>
          
          {/* Navigation links */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              component={Link}
              to="/"
              sx={{ 
                mx: 1.5, 
                color: 'primary.main', 
                opacity: location.pathname === '/' ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              Home
            </Button>
            <Button
              component={Link}
              to="/about"
              sx={{ 
                mx: 1.5, 
                color: 'primary.main', 
                opacity: location.pathname === '/' ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              About
            </Button>
            <IconButton 
              component="a"
              href="https://github.com/puj-nlp/cev-rag"
              target="_blank"
              rel="noopener noreferrer"
              sx={{ 
                mx: 1.5, 
                color: 'primary.main', 
                opacity: location.pathname === '/' ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              <QuestionMark sx={{ fontSize: '1.2rem' }} />
            </IconButton>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
