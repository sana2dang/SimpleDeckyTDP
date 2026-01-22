/**
 * i18n (Internationalization) module for TypeScript/React
 * 
 * Automatically detects Steam language and loads translations from JSON files.
 * 
 * Usage:
 *   import t from '../../utils/i18n';
 *   const label = t('TDP_PROFILE_ENABLE_DESKTOP', 'Enable Desktop Profile');
 */

// Type definitions
interface Translations {
  [key: string]: string;
}

interface LanguageInfo {
  name: string;
  strings: Translations;
}

interface Languages {
  [key: string]: LanguageInfo;
}

// Import translation files
import * as ko from '../../i18n/ko.json';

// Language metadata
export const LANGS: Languages = {
  ko: {
    name: '한국어',
    strings: ko as Translations,
  },
  en: {
    name: 'English',
    strings: {},
  },
};

// Cached language
let cachedLang: string | undefined;

/**
 * Get the current language from Steam's LocalizationManager
 * 
 * @returns Language code (e.g., 'ko', 'en', 'ja')
 */
export const getCurrentLanguage = (): string => {
  if (cachedLang) return cachedLang;

  try {
    // Get language from Steam's LocalizationManager
    const lang = (window as any).LocalizationManager?.m_rgLocalesToUse?.[0];
    
    if (lang && lang in LANGS) {
      cachedLang = lang;
      return lang;
    }
  } catch (e) {
    console.warn('[i18n] Failed to get language from LocalizationManager:', e);
  }

  // Fallback to browser language
  try {
    const browserLang = navigator.language.split('-')[0].toLowerCase();
    if (browserLang in LANGS) {
      cachedLang = browserLang;
      return browserLang;
    }
  } catch (e) {
    // Ignore error
  }

  // Default to English
  cachedLang = 'en';
  return 'en';
};

/**
 * Get the display name of the current or specified language
 * 
 * @param lang - Optional language code
 * @returns Language display name (e.g., '한국어', 'English')
 */
export const getLanguageName = (lang?: string): string => {
  const targetLang = lang || getCurrentLanguage();
  return LANGS[targetLang]?.name || targetLang;
};

/**
 * Reset the cached language to force re-detection
 */
export const resetLanguage = (): void => {
  cachedLang = undefined;
};

/**
 * Manually set the current language
 * 
 * @param lang - Language code to set
 */
export const setLanguage = (lang: string): void => {
  if (lang in LANGS) {
    cachedLang = lang;
  } else {
    console.warn(`[i18n] Language '${lang}' not supported. Available: ${Object.keys(LANGS).join(', ')}`);
  }
};

/**
 * Translate a key to the current language
 * 
 * @param key - Translation key
 * @param defaultText - Default text (fallback, usually English)
 * @returns Translated string or default text if translation not found
 * 
 * @example
 * t('TDP_PROFILE_ENABLE_DESKTOP', 'Enable Desktop Profile')
 * // Korean system → "데스크톱 프로필 활성화"
 * // English system → "Enable Desktop Profile"
 */
const t = (key: string, defaultText: string): string => {
  const lang = getCurrentLanguage();

  // English always returns the default text
  if (lang === 'en') return defaultText;

  // Return translation if exists, otherwise return default text
  return LANGS[lang]?.strings?.[key] ?? defaultText;
};

export default t;
export { t };
