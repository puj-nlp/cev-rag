import React from 'react';
import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { SUPPORTED_LANGUAGES, storeLanguage } from '../i18n/detectLanguage';

/**
 * ES/EN switch. It performs a full navigation so nginx can persist the
 * choice in the HttpOnly `lang` cookie (localStorage is only a client mirror).
 */
const LanguageSelector = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();

  const handleChange = (_event, lang) => {
    if (!lang || lang === i18n.language) return;
    storeLanguage(lang);
    const rest = location.pathname.replace(/^\/(es|en)(?=\/|$)/, '');
    window.location.assign(`/${lang}${rest || '/'}${location.search}`);
  };

  return (
    <Tooltip title={t('header.switchTo')}>
      <ToggleButtonGroup
        size="small"
        exclusive
        value={i18n.language}
        onChange={handleChange}
        aria-label={t('header.language')}
        sx={{ mx: 1.5, '& .MuiToggleButton-root': { px: 1.2, py: 0.3, fontWeight: 700, color: 'primary.main' } }}
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <ToggleButton key={lang} value={lang} lang={lang} aria-label={lang === 'es' ? 'Español' : 'English'}>
            {lang.toUpperCase()}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Tooltip>
  );
};

export default LanguageSelector;
