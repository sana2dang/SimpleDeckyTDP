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
    # i18n 디렉토리 경로: py_modules/../src/i18n
    # py_modules/i18n_py.py에서 src/i18n으로 이동
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
    Get the current language (Steam Deck compatible)
    
    This function detects the language from Steam's settings on Steam Deck.
    
    Returns:
        str: Language code (e.g., 'ko', 'en', 'ja', 'zh')
    
    Priority:
        1. Steam language config file (~/.steam/registry.vdf)
        2. Environment variable STEAM_COMPAT_CLIENT_INSTALL_PATH
        3. Environment variable LANGUAGE
        4. Environment variable LANG
        5. System locale
        6. Default to 'en'
    """
    global _cached_lang
    
    # 캐시된 언어가 있으면 반환
    if _cached_lang:
        return _cached_lang
    
    lang = None
    
    # 1. Steam 설정 파일에서 언어 읽기 (가장 정확)
    try:
        steam_config_paths = [
            os.path.expanduser('~/.steam/registry.vdf'),
            os.path.expanduser('~/.local/share/Steam/registry.vdf'),
            os.path.expanduser('~/snap/steam/common/.steam/registry.vdf'),
        ]
        
        for config_path in steam_config_paths:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # "language" "korean" 또는 "language" "english" 형식 찾기
                    import re
                    match = re.search(r'"language"\s+"(\w+)"', content, re.IGNORECASE)
                    if match:
                        steam_lang = match.group(1).lower()
                        # Steam 언어 코드를 표준 언어 코드로 변환
                        steam_lang_map = {
                            'korean': 'ko',
                            'koreana': 'ko',
                            'english': 'en',
                            'japanese': 'ja',
                            'schinese': 'zh',  # Simplified Chinese
                            'tchinese': 'zh',  # Traditional Chinese
                            'spanish': 'es',
                            'french': 'fr',
                            'german': 'de',
                            'italian': 'it',
                            'portuguese': 'pt',
                            'russian': 'ru',
                        }
                        lang_code = steam_lang_map.get(steam_lang, steam_lang[:2])
                        if lang_code in LANGS:
                            lang = lang_code
                            break
    except Exception as e:
        # Steam 설정 파일 읽기 실패 시 무시
        pass
    
    # 2. Steam 관련 환경변수 확인
    if not lang:
        steam_lang = os.environ.get('STEAM_COMPAT_CLIENT_INSTALL_PATH', '')
        if 'korean' in steam_lang.lower():
            lang = 'ko'
    
    # 3. LANGUAGE 환경변수 확인
    if not lang:
        lang_env = os.environ.get('LANGUAGE', '').split(':')[0].split('_')[0].lower()
        if lang_env in LANGS:
            lang = lang_env
    
    # 4. LANG 환경변수 확인
    if not lang:
        lang_env = os.environ.get('LANG', '').split('.')[0].split('_')[0].lower()
        if lang_env in LANGS:
            lang = lang_env
    
    # 5. 시스템 locale 확인
    if not lang:
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                if lang_code in LANGS:
                    lang = lang_code
        except:
            pass
    
    # 6. 기본값: 영어
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

def reset_language():
    """
    Reset language cache to force re-detection
    
    Example:
        reset_language()  # Next call to get_current_language() will re-detect
    """
    global _cached_lang
    _cached_lang = None

def reload_translations():
    """Reload translation files (useful for development)"""
    global TRANSLATIONS
    TRANSLATIONS = load_translations()
