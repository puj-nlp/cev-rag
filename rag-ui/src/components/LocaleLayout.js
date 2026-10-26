import React, { useEffect } from 'react';
import { Navigate, Outlet, useLocation, useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';

import { SUPPORTED_LANGUAGES, detectLanguage, isSupportedLanguage, storeLanguage } from '../i18n/detectLanguage';

const SITE_URL = (process.env.REACT_APP_SITE_URL || '').replace(/\/$/, '');

/**
 * Wraps every /:lang/* route: validates the prefix, syncs i18next and
 * emits the <html lang>, canonical and hreflang alternates for SEO.
 */
const LocaleLayout = () => {
  const { lang } = useParams();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const valid = isSupportedLanguage(lang);

  useEffect(() => {
    if (valid && i18n.language !== lang) {
      i18n.changeLanguage(lang);
    }
    if (valid) storeLanguage(lang);
  }, [lang, valid, i18n]);

  if (!valid) {
    // Unknown prefix (e.g. /chats/123 from an old link): keep the path under the detected language
    return <Navigate to={`/${detectLanguage()}${location.pathname}${location.search}`} replace />;
  }

  const rest = location.pathname.replace(/^\/(es|en)/, '') || '/';
  const origin = SITE_URL || (typeof window !== 'undefined' ? window.location.origin : '');

  return (
    <>
      <Helmet htmlAttributes={{ lang }}>
        <title>{t('seo.title')}</title>
        <meta name="description" content={t('seo.description')} />
        <link rel="canonical" href={`${origin}/${lang}${rest}`} />
        {SUPPORTED_LANGUAGES.map((code) => (
          <link key={code} rel="alternate" hrefLang={code} href={`${origin}/${code}${rest}`} />
        ))}
        <link rel="alternate" hrefLang="x-default" href={`${origin}/`} />
        <meta property="og:locale" content={lang === 'es' ? 'es_CO' : 'en_US'} />
      </Helmet>
      <Outlet />
    </>
  );
};

export default LocaleLayout;
