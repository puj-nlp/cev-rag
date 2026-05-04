import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box, IconButton, Drawer, List, ListItemButton, ListItemText, Divider } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { GitHub, Menu as MenuIcon, Close as CloseIcon } from '@mui/icons-material';

const LogoVentana = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="40" height="50" viewBox="0 0 400 500" style={{ verticalAlign: 'middle' }}>
    <g fill="none" stroke="#003366" strokeWidth="16">
      <rect x="100" y="150" width="200" height="300"></rect>
      <path d="M100,150 A100,100 0 0 1 300,150"></path>
      <path d="M100,150 L50,100 L50,400 L100,450"></path>
      <path d="M300,150 L350,100 L350,400 L300,450"></path>
      <line x1="200" y1="150" x2="200" y2="450"></line>
      <line x1="100" y1="250" x2="300" y2="250"></line>
    </g>
    <g>
      <polygon points="200,250 300,400 200,450 200,250" fill="#FCD116"></polygon>
      <polygon points="200,250 250,400 200,450 200,250" fill="#003366"></polygon>
    </g>
  </svg>
);

const Header = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => setMobileOpen((prev) => !prev);
  const handleDrawerClose = () => setMobileOpen(false);

  const navLinks = [
    { label: 'Home', to: '/' },
    { label: 'About', to: '/about' },
  ];

  return (
    <AppBar position="fixed" elevation={0} sx={{ backgroundColor: '#e6e6e6', zIndex: 1300 }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
          {/* Logo and title */}
          <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
            <LogoVentana/>
            <Typography
              noWrap
              sx={{
                fontFamily: '"Cinzel", serif !important',
                fontWeight: 700,
                color: 'primary.main',
                marginLeft: 1,
                fontSize: { xs: '0.85rem', sm: '1rem' }
              }}
            >
              VENTANA A LA VERDAD
            </Typography>
          </Box>

          {/* Desktop navigation */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
            {navLinks.map(({ label, to }) => (
              <Button
                key={label}
                component={Link}
                to={to}
                sx={{ 
                  mx: 1.5, 
                  color: 'primary.main', 
                  opacity: location.pathname === to ? 1 : 0.7,
                  '&:hover': { opacity: 1, backgroundColor: '#917D26' }
                }}
              >
                {label}
              </Button>
            ))}
            <IconButton 
              component="a"
              href="https://github.com/puj-nlp/cev-rag"
              target="_blank"
              rel="noopener noreferrer"
              sx={{ 
                mx: 1.5, 
                color: 'primary.main', 
                opacity: 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              <GitHub sx={{ fontSize: '1.2rem' }} />
            </IconButton>
          </Box>

          {/* Mobile hamburger button */}
          <IconButton
            aria-label="open menu"
            onClick={handleDrawerToggle}
            sx={{ display: { xs: 'flex', md: 'none' }, color: 'primary.main' }}
          >
            <MenuIcon />
          </IconButton>
        </Toolbar>
      </Container>

      {/* Mobile drawer */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerClose}
        ModalProps={{ keepMounted: true }}
        PaperProps={{ sx: { width: 240, backgroundColor: '#e6e6e6' } }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 1 }}>
          <IconButton onClick={handleDrawerClose} sx={{ color: 'primary.main' }}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <List>
          {navLinks.map(({ label, to }) => (
            <ListItemButton
              key={label}
              component={Link}
              to={to}
              onClick={handleDrawerClose}
              selected={location.pathname === to}
              sx={{
                color: 'primary.main',
                fontFamily: '"Cinzel", serif',
                '&.Mui-selected': { backgroundColor: 'rgba(0,51,102,0.1)' }
              }}
            >
              <ListItemText primary={label} primaryTypographyProps={{ fontFamily: '"Cinzel", serif', fontWeight: 600 }} />
            </ListItemButton>
          ))}
          <ListItemButton
            component="a"
            href="https://github.com/puj-nlp/cev-rag"
            target="_blank"
            rel="noopener noreferrer"
            onClick={handleDrawerClose}
            sx={{ color: 'primary.main' }}
          >
            <GitHub sx={{ mr: 1, fontSize: '1.2rem' }} />
            <ListItemText primary="GitHub" primaryTypographyProps={{ fontFamily: '"Cinzel", serif', fontWeight: 600 }} />
          </ListItemButton>
        </List>
      </Drawer>
    </AppBar>
  );
};

export default Header;
