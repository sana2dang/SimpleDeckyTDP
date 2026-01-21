import json
import os
import locale

# 언어 메타데이터
LANGS = {
    'ko': {
        'name': '한국어',
        'credit': ['yor42', 'sua (sua_owo)']
    },
    'en': {
        'name': 'English',
        'credit': []
    },
    'ja': {
        'name': '日本語',
        'credit': []
    },
    'zh': {
        'name': '中文',
        'credit': []
    }
}

# 번역 파일 로드
def load_translations():
    """Load all translation files from the i18n directory"""
    translations = {}
    # i18n 디렉토리 경로 (파일과 같은 위치에 i18n 폴더가 있다고 가정)
    i18n_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'i18n')
    
    if os.path.exists(i18n_dir):
        for filename in os.listdir(i18n_dir):
            if filename.endswith('.json'):
                lang = filename.replace('.json', '')
                try:
                    with open(os.path.join(i18n_dir, filename), 'r', encoding='utf-8') as f:
                        translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {filename}: {e}")
    
    return translations

# 전역 번역 딕셔너리
TRANSLATIONS = load_translations()

# 캐시된 언어
_cached_lang = None

def get_current_language():
    """
    Get the current system language (Steam OS compatible)
    
    This function mimics the behavior of TypeScript's getCurrentLanguage()
    by detecting the system locale from Steam OS environment.
    
    Returns:
        str: Language code (e.g., 'ko', 'en', 'ja', 'zh')
    
    Priority:
        1. Environment variable STEAM_COMPAT_CLIENT_INSTALL_PATH (Steam language)
        2. Environment variable LANGUAGE
        3. Environment variable LANG
        4. System locale
        5. Default to 'en'
    """
    global _cached_lang
    
    # 캐시된 언어가 있으면 반환
    if _cached_lang:
        return _cached_lang
    
    lang = None
    
    # 1. Steam 환경 변수 확인 (Steam OS specific)
    # Steam은 LANGUAGE 환경변수를 설정함
    steam_lang = os.environ.get('LANGUAGE', '').split(':')[0].split('_')[0].lower()
    if steam_lang and steam_lang in LANGS:
        lang = steam_lang
    
    # 2. LANG 환경변수 확인
    if not lang:
        lang_env = os.environ.get('LANG', '').split('.')[0].split('_')[0].lower()
        if lang_env in LANGS:
            lang = lang_env
    
    # 3. 시스템 locale 확인
    if not lang:
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in LANGS:
                    lang = lang_code
        except:
            pass
    
    # 4. 기본값: 영어
    if not lang:
        lang = 'en'
    
    # 캐시
    _cached_lang = lang
    return lang

def get_language_name(lang=None):
    """
    Get the display name of a language
    
    Args:
        lang (str, optional): Language code. If None, uses current language
    
    Returns:
        str: Language display name (e.g., '한국어', 'English')
    
    Example:
        get_language_name('ko')  # Returns: '한국어'
        get_language_name()      # Returns: current language name
    """
    if lang is None:
        lang = get_current_language()
    
    return LANGS.get(lang, {}).get('name', lang)

def get_credits(lang=None):
    """
    Get the translation credits for a language
    
    Args:
        lang (str, optional): Language code. If None, uses current language
    
    Returns:
        list: List of translator names
    
    Example:
        get_credits('ko')  # Returns: ['yor42', 'sua (sua_owo)']
    """
    if lang is None:
        lang = get_current_language()
    
    return LANGS.get(lang, {}).get('credit', [])

def t(key, default_text, lang=None):
    """
    Translate a key to the target language
    
    Args:
        key (str): Translation key
        default_text (str): Default text (fallback, usually English)
        lang (str, optional): Language code. If None, uses current system language
    
    Returns:
        str: Translated string or default text if translation not found
    
    Example:
        # With explicit language
        t('ADVANCED_ENABLE_TDP_CONTROLS', 'Enable TDP Controls', 'ko')
        # Returns: 'TDP 제어 활성화'
        
        # With auto-detected language
        t('ADVANCED_ENABLE_TDP_CONTROLS', 'Enable TDP Controls')
        # Returns: translation based on system language
    """
    # 언어가 지정되지 않으면 시스템 언어 사용
    if lang is None:
        lang = get_current_language()
    
    # 영어는 항상 기본 텍스트 반환
    if lang == 'en':
        return default_text
    
    # 번역 찾기, 없으면 기본 텍스트 반환
    return TRANSLATIONS.get(lang, {}).get(key, default_text)

def set_language(lang):
    """
    Manually set the current language (overrides auto-detection)
    
    Args:
        lang (str): Language code to set
    
    Example:
        set_language('ko')  # Force Korean
        set_language('en')  # Force English
    """
    global _cached_lang
    if lang in LANGS:
        _cached_lang = lang
    else:
        print(f"Warning: Language '{lang}' not supported. Available: {list(LANGS.keys())}")

def reload_translations():
    """Reload translation files (useful for development)"""
    global TRANSLATIONS
    TRANSLATIONS = load_translations()
