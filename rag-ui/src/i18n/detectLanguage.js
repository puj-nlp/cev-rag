/**
 * Client-side language detection.
 *
 * In production nginx resolves the language before the SPA loads (cookie >
 * Accept-Language > CF-IPCountry) and redirects "/" to "/es/" or "/en/".
 * This module mirrors that order for environments without nginx (npm start)
 * and for in-app redirects of unprefixed routes.
 */

export const SUPPORTED_LANGUAGES = ['es', 'en'];
export const DEFAULT_LANGUAGE = 'en';
export const STORAGE_KEY = 'cev_lang';

export const isSupportedLanguage = (lang) => SUPPORTED_LANGUAGES.includes(lang);

const readStoredLanguage = () => {
  try {
    return window.localStorage.getItem(STORAGE_KEY);
  } catch (e) {
    return null;
  }
};

export const storeLanguage = (lang) => {
  try {
    window.localStorage.setItem(STORAGE_KEY, lang);
  } catch (e) {
    // Storage may be unavailable (private mode); the URL prefix still carries the language
  }
};

/** First supported language in a browser preference list such as navigator.languages. */
export const languageFromPreferences = (preferences = []) => {
  for (const tag of preferences) {
    const primary = String(tag).toLowerCase().split(/[-_]/)[0];
    if (isSupportedLanguage(primary)) return primary;
  }
  return null;
};

export const detectLanguage = ({
  stored = readStoredLanguage(),
  preferences = typeof navigator !== 'undefined' ? navigator.languages || [navigator.language] : [],
} = {}) => {
  if (isSupportedLanguage(stored)) return stored;
  return languageFromPreferences(preferences) || DEFAULT_LANGUAGE;
};
