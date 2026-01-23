import json
import os
import locale

# 언어 메타데이터
LANGS = {
    'ko': {'name': '한국어'},
    'en': {'name': 'English'},
    'ja': {'name': '日本語'}
}

# 번역 파일 로드
def load_translations():
    """Load all translation files from the i18n directory"""
    translations = {}
    
    # i18n 디렉토리 경로 찾기
    # 우선순위:
    # 1. 환경 변수 I18N_DIR (수동 설정)
    # 2. DECKY_PLUGIN_DIR/i18n (Decky Plugin 환경)
    # 3. i18n_py.py와 같은 디렉토리 (기본)
    
    i18n_dir = None
    
    # 1. 환경 변수 I18N_DIR 확인
    if os.environ.get('I18N_DIR'):
        i18n_dir = os.environ.get('I18N_DIR')
    
    # 2. Decky Plugin 환경 확인
    elif os.environ.get('DECKY_PLUGIN_DIR'):
        plugin_dir = os.environ.get('DECKY_PLUGIN_DIR')
        i18n_dir = os.path.join(plugin_dir, 'i18n')
    
    # 3. i18n_py.py와 같은 디렉토리 (기본)
    else:
        current_file = os.path.abspath(__file__)
        i18n_dir = os.path.dirname(current_file)
    
    if not i18n_dir or not os.path.exists(i18n_dir):
        # 번역 파일을 찾을 수 없음 - 빈 딕셔너리 반환
        return translations
    
    try:
        for filename in os.listdir(i18n_dir):
            if filename.endswith('.json'):
                lang = filename.replace('.json', '')
                try:
                    with open(os.path.join(i18n_dir, filename), 'r', encoding='utf-8') as f:
                        translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {filename}: {e}")
    except Exception as e:
        print(f"Error reading i18n directory {i18n_dir}: {e}")
    
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
        str: Language code (e.g., 'ko', 'en', 'ja')
    
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
        # Decky Plugin 환경에서는 /home/deck을 명시적으로 사용
        steam_config_paths = [
            '/home/deck/.steam/registry.vdf',
            '/home/deck/.local/share/Steam/registry.vdf',
            os.path.expanduser('~/.steam/registry.vdf'),
            os.path.expanduser('~/.local/share/Steam/registry.vdf'),
            os.path.expanduser('~/snap/steam/common/.steam/registry.vdf'),
        ]
        
        for config_path in steam_config_paths:
            if os.path.exists(config_path):
                try:
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
                except PermissionError:
                    # 권한 문제로 읽을 수 없는 경우 계속 진행
                    continue
                except Exception:
                    # 다른 오류 발생 시 계속 진행
                    continue
    except Exception:
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

def get_language_debug_info():
    """
    Get debug information about language detection (useful for Decky Plugin debugging)
    
    Returns:
        dict: Debug information including paths, environment variables, and detection result
    
    Example:
        debug_info = get_language_debug_info()
        print(json.dumps(debug_info, indent=2))
    """
    import re
    
    debug_info = {
        'detected_language': get_current_language(),
        'cached': _cached_lang is not None,
        'current_file': os.path.abspath(__file__),
        'working_directory': os.getcwd(),
        'steam_config_files': {},
        'environment_variables': {},
        'decky_environment': {},
        'translations_loaded': list(TRANSLATIONS.keys()),
        'supported_languages': list(LANGS.keys()),
        'i18n_paths_checked': [],
    }
    
    # Decky Plugin 환경 변수 확인
    decky_vars = [
        'DECKY_PLUGIN_DIR',
        'DECKY_PLUGIN_NAME',
        'DECKY_USER_HOME',
        'DECKY_HOME',
        'DECKY_VERSION',
    ]
    for var in decky_vars:
        value = os.environ.get(var)
        if value:
            debug_info['decky_environment'][var] = value
    
    # Decky Plugin 환경이면 예상 경로 추가
    if os.environ.get('DECKY_PLUGIN_DIR'):
        plugin_dir = os.environ.get('DECKY_PLUGIN_DIR')
        decky_i18n_path = os.path.join(plugin_dir, 'i18n')
        debug_info['decky_environment']['expected_i18n_path'] = decky_i18n_path
        debug_info['decky_environment']['expected_i18n_exists'] = os.path.exists(decky_i18n_path)
    
    # i18n 디렉토리 후보 경로들
    current_file = os.path.abspath(__file__)
    possible_i18n_paths = [
        ('환경 변수 I18N_DIR', os.environ.get('I18N_DIR')),
        ('Decky Plugin (DECKY_PLUGIN_DIR/i18n)', 
         os.path.join(os.environ.get('DECKY_PLUGIN_DIR', ''), 'i18n') if os.environ.get('DECKY_PLUGIN_DIR') else None),
        ('같은 디렉토리 (i18n/)', os.path.dirname(current_file)),
    ]
    
    for desc, path in possible_i18n_paths:
        if not path:
            continue
            
        abs_path = os.path.abspath(path)
        path_info = {
            'description': desc,
            'path': abs_path,
            'exists': os.path.exists(abs_path),
            'is_dir': os.path.isdir(abs_path) if os.path.exists(abs_path) else False,
            'files': []
        }
        
        if path_info['exists'] and path_info['is_dir']:
            try:
                path_info['files'] = [f for f in os.listdir(abs_path) if f.endswith('.json')]
            except Exception as e:
                path_info['error'] = str(e)
        
        debug_info['i18n_paths_checked'].append(path_info)
    
    # Steam 설정 파일 확인
    steam_config_paths = [
        '/home/deck/.steam/registry.vdf',
        '/home/deck/.local/share/Steam/registry.vdf',
        os.path.expanduser('~/.steam/registry.vdf'),
        os.path.expanduser('~/.local/share/Steam/registry.vdf'),
    ]
    
    for path in steam_config_paths:
        exists = os.path.exists(path)
        language_found = None
        
        if exists:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    match = re.search(r'"language"\s+"(\w+)"', content, re.IGNORECASE)
                    if match:
                        language_found = match.group(1)
            except Exception as e:
                language_found = f'ERROR: {str(e)}'
        
        debug_info['steam_config_files'][path] = {
            'exists': exists,
            'language': language_found
        }
    
    # 환경 변수 확인
    env_vars = ['I18N_DIR', 'LANGUAGE', 'LANG', 'LC_ALL', 'STEAM_COMPAT_CLIENT_INSTALL_PATH', 'HOME', 'USER']
    for var in env_vars:
        debug_info['environment_variables'][var] = os.environ.get(var, None)
    
    # 실제 사용된 i18n 디렉토리
    debug_info['i18n_directory_used'] = None
    for path_info in debug_info['i18n_paths_checked']:
        if path_info['exists'] and path_info['is_dir'] and path_info['files']:
            debug_info['i18n_directory_used'] = path_info['path']
            break
    
    return debug_info

def reload_translations():
    """Reload translation files (useful for development)"""
    global TRANSLATIONS
    TRANSLATIONS = load_translations()
