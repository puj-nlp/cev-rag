import React from 'react';
import { Box, Button, Container, Paper, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';

import useLocalizedPath from '../i18n/useLocalizedPath';

const VIMEO_SRC = 'https://player.vimeo.com/video/1239903383?dnt=1&title=0&byline=0&portrait=0';

/** Home page: landing with the project's presentation video. */
const HomePage = () => {
  const { t } = useTranslation();
  const localizedPath = useLocalizedPath();

  return (
    <Box sx={{ bgcolor: '#f1f5f9', pb: 6 }}>
      <Helmet>
        <title>{t('seo.homeTitle')}</title>
      </Helmet>

      <Container maxWidth="lg" sx={{ pt: { xs: 4, md: 6 }, pb: 3, textAlign: 'center' }}>
        <Typography variant="overline" sx={{ color: '#917D26', fontFamily: '"Inter", sans-serif', fontWeight: 700 }}>
          {t('home.eyebrow')}
        </Typography>
        <Typography variant="h3" component="h1" sx={{ color: '#1e3a8a', fontFamily: '"Cinzel", serif !important', fontSize: { xs: '1.9rem', md: '2.8rem' } }}>
          {t('home.title')}
        </Typography>
        <Typography variant="body1" sx={{ maxWidth: 820, mx: 'auto', mt: 1.5, color: '#475569', fontFamily: '"Inter", sans-serif' }}>
          {t('home.subtitle')}
        </Typography>
      </Container>

      <Container maxWidth="lg">
        <Paper elevation={3} sx={{ overflow: 'hidden', borderRadius: 3, aspectRatio: '16 / 9', bgcolor: '#0b1437' }}>
          <Box
            component="iframe"
            src={VIMEO_SRC}
            title={t('home.videoTitle')}
            allow="fullscreen; picture-in-picture; encrypted-media"
            allowFullScreen
            loading="lazy"
            referrerPolicy="strict-origin-when-cross-origin"
            sx={{ display: 'block', width: '100%', height: '100%', border: 0 }}
          />
        </Paper>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 2, mt: 4 }}>
          <Button
            component={RouterLink}
            to={localizedPath('/chat')}
            variant="contained"
            size="large"
            sx={{ bgcolor: '#1e3a8a', '&:hover': { bgcolor: '#1e40af' } }}
          >
            {t('home.ctaChat')}
          </Button>
          <Button
            component={RouterLink}
            to={localizedPath('/como-funciona')}
            variant="outlined"
            size="large"
            sx={{ color: '#1e3a8a', borderColor: '#1e3a8a' }}
          >
            {t('home.ctaHowItWorks')}
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default HomePage;
