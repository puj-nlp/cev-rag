import React from 'react';
import { Box, Container, Typography, Link, Grid } from '@mui/material';

const Footer = () => {
  return (
    <Box 
      component="footer" 
      sx={{ 
        backgroundColor: '#101986',
        color: '#FFFFFF',
        py: 2,
        width: '100%',
        position: 'fixed',
        left: 0,
        bottom: 0,
        zIndex: 1200
      }}
    >
      <Container maxWidth={false} sx={{ px: 2 }}>
        <Grid container spacing={2} alignItems="center" justifyContent="center" sx={{ minHeight: '48px' }}>
          {/* Contenido centrado del footer */}
          <Grid item xs={12}>
            <Box 
              sx={{ 
                display: 'flex',
                flexDirection: { xs: 'column', sm: 'row' },
                alignItems: 'center',
                justifyContent: 'center',
                gap: { xs: 2, sm: 3 },
                textAlign: 'center'
              }}
            >
              {/* Texto principal */}
              <Typography 
                variant="body2" 
                sx={{ 
                  fontSize: '14px',
                  fontFamily: '"Inter", sans-serif'
                }}
              >
                Proyecto financiado por el Notre Dame–IBM Technology Ethics Lab @2024
              </Typography>
              
              {/* Separador visual */}
              <Box sx={{ display: { xs: 'none', sm: 'block' }, color: '#FFFFFF', mx: 1 }}>|</Box>
              
              {/* Logos de cooperantes */}
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  gap: 3,
                  flexWrap: 'wrap',
                  justifyContent: 'center'
                }}
              >
                <Link 
                  href="https://www.javeriana.edu.co/inicio"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ 
                    display: 'flex',
                    alignItems: 'center',
                    '&:hover': { opacity: 0.8 }
                  }}
                >
                  <img 
                    src="/logo_javeriana.png"
                    alt="Universidad Javeriana"
                    style={{ 
                      height: '40px',
                      filter: 'brightness(0) invert(1)' // Hace el logo blanco
                    }}
                  />
                </Link>
                
                <Link 
                  href="https://legacyproject.nd.edu/"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ 
                    display: 'flex',
                    alignItems: 'center',
                    '&:hover': { opacity: 0.8 }
                  }}
                >
                  <img 
                    src="/logo_legacy_project.svg"
                    alt="Legacy Project Notre Dame"
                    style={{ 
                      height: '40px',
                      filter: 'brightness(0) invert(1)' // Hace el logo blanco
                    }}
                  />
                </Link>
                
                <Link 
                  href="https://lucyinstitute.nd.edu"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ 
                    display: 'flex',
                    alignItems: 'center',
                    '&:hover': { opacity: 0.8 }
                  }}
                >
                  <img 
                    src="/logo_lucy.svg"
                    alt="Lucy Institute Notre Dame"
                    style={{ 
                      height: '40px',
                      filter: 'brightness(0) invert(1)' // Hace el logo blanco
                    }}
                  />
                </Link>
                
                <Link 
                  href="https://kroc.nd.edu/"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ 
                    display: 'flex',
                    alignItems: 'center',
                    '&:hover': { opacity: 0.8 }
                  }}
                >
                  <img 
                    src="/logo_kroc.svg"
                    alt="Notre Dame IBM Technology Ethics Lab"
                    style={{ 
                      height: '40px',
                      filter: 'brightness(0) invert(1)' // Hace el logo blanco
                    }}
                  />
                </Link>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Footer;
