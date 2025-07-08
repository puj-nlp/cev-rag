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
              variant="h6"
              noWrap
              component={Link}
              to="/"
              sx={{
                fontWeight: 700,
                color: '#B8860B',
                textDecoration: 'none',
                fontFamily: 'oblique sans-serif',
                fontSize: '28px',
                letterSpacing: '0.5px',
                textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
                '&:hover': {
                  color: '#DAA520',
                }
              }}
            >
              WINDOW TO TRUTH
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
                opacity: location.pathname === '/about' ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              About
            </Button>
            <IconButton 
              color="inherit" 
              sx={{ ml: 1.5 }}
              component={Link}
              to="/help"
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
