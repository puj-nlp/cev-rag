import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box, Avatar, IconButton } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { Diamond as DiamondIcon, QuestionMark } from '@mui/icons-material';

const Header = () => {
  const location = useLocation();

  return (
    <AppBar position="static" elevation={0} sx={{ backgroundColor: 'primary.main' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
          {/* Logo y título */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <DiamondIcon sx={{ mr: 1, transform: 'rotate(45deg)' }} />
            <Typography
              variant="h6"
              noWrap
              component={Link}
              to="/"
              sx={{
                fontWeight: 700,
                color: 'inherit',
                textDecoration: 'none',
              }}
            >
              Ventana a la Verdad
            </Typography>
          </Box>
          
          {/* Enlaces de navegación */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              component={Link}
              to="/"
              sx={{ 
                mx: 1.5, 
                color: 'white', 
                opacity: location.pathname === '/' ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: 'rgba(255,255,255,0.1)' }
              }}
            >
              Home
            </Button>
            <Button
              component={Link}
              to="/about"
              sx={{ 
                mx: 1.5, 
                color: 'white', 
                opacity: location.pathname === '/about' ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: 'rgba(255,255,255,0.1)' }
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
            <Avatar 
              alt="User Profile" 
              src="/avatar.jpg" 
              sx={{ ml: 2, width: 35, height: 35 }}
            />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
