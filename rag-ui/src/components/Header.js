import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box, Avatar, IconButton, Menu, MenuItem } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { GitHub, Menu as MenuIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import LanguageSelector from './LanguageSelector';
import useLocalizedPath from '../i18n/useLocalizedPath';

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
  const { t } = useTranslation();
  const localizedPath = useLocalizedPath();
  const isActive = (path) => location.pathname === localizedPath(path)
    || (path !== '/' && location.pathname.startsWith(localizedPath(path)));
  const [menuAnchor, setMenuAnchor] = useState(null);
  const closeMenu = () => setMenuAnchor(null);

  const navItems = [
    { path: '/', label: t('header.home') },
    { path: '/como-funciona', label: t('header.howItWorks') },
    { path: '/chat', label: t('header.chat') },
    { path: '/about', label: t('header.about') },
  ];

  return (
    <AppBar position="static" elevation={0} sx={{ backgroundColor: '#e6e6e6' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
          {/* Logo and title */}
          <Box component={Link} to={localizedPath('/')} sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none', minWidth: 0 }}>
            <LogoVentana/>
            <Typography
              noWrap
              sx={{
                fontFamily: '"Cinzel", serif !important',
                fontWeight: 700,
                color: 'primary.main',
                marginLeft: 1,
                fontSize: { xs: '0.95rem', sm: '1rem' }
              }}
            >
              {t('header.brand')}
            </Typography>
          </Box>
          
          {/* Phones: navigation collapses into a menu */}
          <Box sx={{ display: { xs: 'flex', sm: 'none' }, alignItems: 'center', flexShrink: 0 }}>
            <LanguageSelector />
            <IconButton
              onClick={(event) => setMenuAnchor(event.currentTarget)}
              aria-label={t('header.menu')}
              aria-controls={menuAnchor ? 'header-menu' : undefined}
              aria-haspopup="true"
              sx={{ color: 'primary.main' }}
            >
              <MenuIcon />
            </IconButton>
            <Menu id="header-menu" anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={closeMenu}>
              {navItems.map(({ path, label }) => (
                <MenuItem
                  key={path}
                  component={Link}
                  to={localizedPath(path)}
                  selected={isActive(path)}
                  aria-current={isActive(path) ? 'page' : undefined}
                  onClick={closeMenu}
                >
                  {label}
                </MenuItem>
              ))}
              <MenuItem
                component="a"
                href="https://github.com/puj-nlp/cev-rag"
                target="_blank"
                rel="noopener noreferrer"
                onClick={closeMenu}
              >
                <GitHub sx={{ fontSize: '1.2rem', mr: 1 }} />
                {t('header.github')}
              </MenuItem>
            </Menu>
          </Box>

          {/* Navigation links (tablet and desktop) */}
          <Box sx={{ display: { xs: 'none', sm: 'flex' }, alignItems: 'center', flexShrink: 0 }}>
            <Button
              component={Link}
              to={localizedPath('/')}
              aria-current={isActive('/') ? 'page' : undefined}
              sx={{ 
                mx: { sm: 0.5, md: 1.5 }, 
                color: 'primary.main', 
                opacity: isActive('/') ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              {t('header.home')}
            </Button>
            <Button
              component={Link}
              to={localizedPath('/como-funciona')}
              aria-current={isActive('/como-funciona') ? 'page' : undefined}
              sx={{ 
                mx: { sm: 0.5, md: 1.5 }, 
                color: 'primary.main', 
                opacity: isActive('/como-funciona') ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              {t('header.howItWorks')}
            </Button>
            <Button
              component={Link}
              to={localizedPath('/chat')}
              aria-current={isActive('/chat') ? 'page' : undefined}
              sx={{ 
                mx: { sm: 0.5, md: 1.5 }, 
                color: 'primary.main', 
                opacity: isActive('/chat') ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              {t('header.chat')}
            </Button>
            <Button
              component={Link}
              to={localizedPath('/about')}
              aria-current={isActive('/about') ? 'page' : undefined}
              sx={{ 
                mx: { sm: 0.5, md: 1.5 }, 
                color: 'primary.main', 
                opacity: isActive('/about') ? 1 : 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              {t('header.about')}
            </Button>
            <IconButton 
              component="a"
              href="https://github.com/puj-nlp/cev-rag"
              target="_blank"
              rel="noopener noreferrer"
              aria-label={t('header.github')}
              sx={{ 
                mx: { sm: 0.5, md: 1.5 }, 
                color: 'primary.main', 
                opacity: 0.7,
                '&:hover': { opacity: 1, backgroundColor: '#917D26' }
              }}
            >
              <GitHub sx={{ fontSize: '1.2rem' }} />
            </IconButton>
            <LanguageSelector />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
