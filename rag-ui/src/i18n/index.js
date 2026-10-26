import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './locales/en.json';
import es from './locales/es.json';
import { DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, detectLanguage, isSupportedLanguage } from './detectLanguage';

// The URL prefix (/es/, /en/) is the source of truth; LocaleLayout keeps i18next in sync with it
const pathLanguage = typeof window !== 'undefined' ? window.location.pathname.split('/')[1] : null;

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, es: { translation: es } },
  lng: isSupportedLanguage(pathLanguage) ? pathLanguage : detectLanguage(),
  fallbackLng: DEFAULT_LANGUAGE,
  supportedLngs: SUPPORTED_LANGUAGES,
  interpolation: { escapeValue: false }, // React already escapes rendered values
});

export default i18n;
