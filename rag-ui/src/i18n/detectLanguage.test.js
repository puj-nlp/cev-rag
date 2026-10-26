import { detectLanguage, languageFromPreferences } from './detectLanguage';

describe('languageFromPreferences', () => {
  it('returns the first supported primary tag', () => {
    expect(languageFromPreferences(['fr-FR', 'es-CO', 'en-US'])).toBe('es');
    expect(languageFromPreferences(['en-GB', 'es'])).toBe('en');
  });

  it('returns null when nothing is supported', () => {
    expect(languageFromPreferences(['fr', 'de-DE'])).toBeNull();
    expect(languageFromPreferences([])).toBeNull();
  });
});

describe('detectLanguage', () => {
  it('prefers the stored manual choice over the browser', () => {
    expect(detectLanguage({ stored: 'en', preferences: ['es-MX'] })).toBe('en');
  });

  it('ignores unsupported stored values', () => {
    expect(detectLanguage({ stored: 'pt', preferences: ['es-MX'] })).toBe('es');
  });

  it('falls back to English', () => {
    expect(detectLanguage({ stored: null, preferences: ['de-DE'] })).toBe('en');
  });
});
