import * as ko from '../i18n/ko.json';

export const LANGS: {
  [key: string]: {
    name: string,
    strings: {
      [key: string]: string
    },
    credit: string[]
  }
} = {
  ko: {
    name: '한국어',
    strings: ko,
    credit: ['yor42', 'sua (sua_owo)'],
  },  
};

let cachedLang: string | undefined;
const getCurrentLanguage = (): string => {
  if (cachedLang) return cachedLang;

  const lang = window.LocalizationManager.m_rgLocalesToUse[0];
  cachedLang = lang;
  return lang;
};

export const getCredits = (lang?: string) => {
  if (lang) return LANGS[lang]?.credit;
  return LANGS[getCurrentLanguage()]?.credit;
};

export const getLanguageName = (lang?: string): string => {
  if (lang) return LANGS[lang]?.name;
  return LANGS[getCurrentLanguage()]?.name;
};

/**
 * Very basic translation cause theres like 20 strings and i don't need anything more complex.
 *
 * @param {string} key Locale key
 * @param {string} originalString Original text
 * @param {boolean} steamToken If true, uses the key to query Steams token store.
 *    Good for actions like "Back" or "Cancel". Won't be dumped with the rest of the strings.
 *
 * @example
 * t('TITLE_FILTER_MODAL', 'Asset Filters')
 * @example
 * // if you need variables use .replace()
 * t('ACTION_REMOVE_GAME', 'Delete {gameName}').replaceAll('{gameName}', gameName)
 * @example
 * // Original Steam string
 * t('Button_Back', 'Back', true);
 */
const trans_string = (key: string, originalString: string, steamToken = false): string => {
  const lang = getCurrentLanguage();
  if (steamToken) {
    return window.LocalizationManager.m_mapTokens.get(key) ?? window.LocalizationManager.m_mapFallbackTokens.get(key) ?? originalString;
  }
  if (lang === 'en') return originalString;

  return LANGS[lang]?.strings?.[key] ?? originalString;
};

// using "trans_string" so it can be found by dump-strings
export default trans_string;
