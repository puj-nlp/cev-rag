import React from 'react';
import { Container, Typography, Box, Grid, Paper, Link } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet-async';
import WindowContainer from '../components/WindowContainer';

const About = () => {
  const { t } = useTranslation();
  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Helmet><title>{t('seo.aboutTitle')}</title></Helmet>
      <WindowContainer>
        <Grid container spacing={6}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, borderRadius: 2 }}>
            <Typography variant="h4" paragraph>
              {t('about.intro')}
            </Typography>
            
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4 }}>
              {t('about.howTitle')}
            </Typography>
            
            <Typography variant="body1" paragraph>
              {t('about.how1')}
            </Typography>
            
            <Typography variant="body1" paragraph>
              {t('about.how2')}
            </Typography>
            
            <Typography variant="body1" paragraph>
              {t('about.how3')}
            </Typography>
            
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              {t('about.commissionTitle')}
            </Typography>
            
            <Typography variant="body1" paragraph>
              {t('about.commission1')}
            </Typography>
            
            <Typography variant="body1">
              {t('about.commission2')}
            </Typography>

          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 4, borderRadius: 2, mb: 4 }}>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4 }}>
              {t('about.resourcesTitle')}
            </Typography>
            
            <Typography variant="body1" paragraph>
              {t('about.resourcesLead')}{' '}
              <Link 
                href={t('about.reportUrl')} 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ fontWeight: 500 }}
              >
                {t('about.reportLink')}
              </Link>
              {' '}{t('about.and')}{' '}
              <Link 
                href="https://legacyproject.nd.edu/" 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ fontWeight: 500 }}
              >
                {t('about.legacyLink')}
              </Link>.
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 3, mt: 4 }}>
              {t('about.contactTitle')}
            </Typography>
            
            <Typography variant="body1" paragraph>
              Luis Gabriel Moreno Sandoval
              morenoluis@javeriana.edu.co
            </Typography>
          </Paper>
          
    
        </Grid>
      </Grid>
      </WindowContainer>
    </Container>
  );
};

export default About;
