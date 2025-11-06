/* Lightweight client-side i18n for static pages
   - Provides translations for en, hi, te, kn, ta
   - Scans the document for data-i18n attributes and data-i18n-placeholder/value
   - Persists selected language in localStorage under 'lang'
   - Attaches a small language chooser to an element with id 'language-btn' or class 'language-selector'
*/
(function(window){
    const STORAGE_KEY = 'lang';
    const DEFAULT = 'en';

    // Translations are loaded from JSON files under ./assets/locales/
    // This keeps translations maintainable and easier to edit/translate.
    const TRANSLATIONS_CACHE = {};
    // Supported languages - keep this in sync with the locales files
    const SUPPORTED_LANGS = ['en','hi','te','kn','ta'];
    const DEFAULT_INLINE = {
        "tile_recommend": "💡 Crop Recommendation",
        "back_to_home": "← Back to Home",
        "quick_actions": "Quick Actions"
    };

    function fetchTranslation(lang) {
        if (TRANSLATIONS_CACHE[lang]) return Promise.resolve(TRANSLATIONS_CACHE[lang]);

        // Derive a sensible base path for locales by inspecting the currently
        // running script tag that loaded this i18n.js file. This ensures we
        // fetch translations from the same static path (for example /static/assets/locales/...)
        let base = '/assets/locales/';
        try {
            const scripts = document.getElementsByTagName('script');
            for (let i = 0; i < scripts.length; i++) {
                const src = scripts[i].getAttribute('src') || '';
                if (src.indexOf('/assets/js/i18n.js') !== -1 || src.endsWith('assets/js/i18n.js')) {
                    // normalize to folder containing locales
                    base = src.replace(/\/assets\/js\/i18n\.js$/, '/assets/locales/');
                    // if src is absolute (starts with http or /), keep it as-is
                    break;
                }
            }
        } catch (e) {
            // ignore and use default
        }

        const candidates = [
            base + `${lang}.json`,
            // fallback absolute and relative variants
            `/assets/locales/${lang}.json`,
            `assets/locales/${lang}.json`
        ];

        function tryFetchList(list) {
            if (!list.length) return Promise.reject(new Error('no candidates'));
            const url = list.shift();
            return fetch(url, {cache: 'no-store'}).then(r => {
                if (!r.ok) throw new Error('not ok ' + r.status + ' for ' + url);
                return r.json();
            }).then(obj => {
                TRANSLATIONS_CACHE[lang] = obj;
                console.debug('i18n: loaded', url);
                return obj;
            }).catch((err)=> {
                console.warn('i18n: failed to load', err && err.message ? err.message : err);
                return tryFetchList(list);
            });
        }
        return tryFetchList(candidates.slice());
    }

    function getStored() {
        try { return localStorage.getItem(STORAGE_KEY) || DEFAULT; } catch(e){ return DEFAULT; }
    }

    function setStored(lang) {
        try { localStorage.setItem(STORAGE_KEY, lang); } catch(e){}
    }

    function applyMap(map) {
        if (!map) map = DEFAULT_INLINE;
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (map[key]) el.textContent = map[key];
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (map[key]) el.setAttribute('placeholder', map[key]);
        });
        document.querySelectorAll('[data-i18n-value]').forEach(el => {
            const key = el.getAttribute('data-i18n-value');
            if (map[key]) el.value = map[key];
        });
        const btn = document.getElementById('language-btn') || document.querySelector('.language-selector');
        if (btn) {
            const names = { en: 'English', hi: 'हिन्दी', te: 'తెలుగు', kn: 'ಕನ್ನಡ', ta: 'தமிழ்' };
            // Read selected language from storage so applyMap can update the button label
            const cur = (function(){ try { return localStorage.getItem(STORAGE_KEY) || DEFAULT } catch(e){ return DEFAULT } })();
            btn.textContent = `🌐 ${names[cur] || names.en} ▼`;
        }
    }

    function setLanguage(lang) {
        if (!lang) lang = DEFAULT;
        setStored(lang);
        fetchTranslation(lang).then(map => {
            applyMap(map);
            try { window.dispatchEvent(new CustomEvent('i18n:languageChanged', { detail: { lang } })); } catch(e){}
        }).catch(() => {
            // fallback to default inline or english file
            fetchTranslation('en').then(map=>{ applyMap(map); try { window.dispatchEvent(new CustomEvent('i18n:languageChanged', { detail: { lang: 'en' } })); } catch(e){} }).catch(()=>{ applyMap(DEFAULT_INLINE); try { window.dispatchEvent(new CustomEvent('i18n:languageChanged', { detail: { lang: 'en' } })); } catch(e){} });
        });
    }

    function initI18n() {
        const lang = getStored();
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => setLanguage(lang));
        } else {
            setLanguage(lang);
        }
        attachChooser();
    }

    function attachChooser() {
        const btn = document.getElementById('language-btn') || document.querySelector('.language-selector');
        if (!btn) return;
        // avoid duplicating chooser
        if (btn.__i18n_attached) return;
        btn.__i18n_attached = true;

    // Prefer cached translations keys, otherwise fall back to the supported list
    const langs = Object.keys(TRANSLATIONS_CACHE).length ? Object.keys(TRANSLATIONS_CACHE) : SUPPORTED_LANGS;
        const list = document.createElement('div');
        list.style.position = 'absolute';
        list.style.background = '#fff';
        list.style.border = '1px solid #ddd';
        list.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
        list.style.padding = '6px';
        list.style.borderRadius = '6px';
        list.style.zIndex = 2000;
        list.style.display = 'none';

        langs.forEach(l => {
            const item = document.createElement('div');
            item.textContent = l + ' — ' + ( {en:'English',hi:'हिन्दी',te:'తెలుగు',kn:'ಕನ್ನಡ',ta:'தமிழ்'}[l] || l );
            item.style.padding = '6px 10px';
            item.style.cursor = 'pointer';
            item.addEventListener('mouseenter', ()=> item.style.background='#f5f5f5');
            item.addEventListener('mouseleave', ()=> item.style.background='transparent');
            item.addEventListener('click', (e) => {
                setLanguage(l);
                list.style.display = 'none';
            });
            list.appendChild(item);
        });

        document.body.appendChild(list);

        btn.addEventListener('click', (ev) => {
            const rect = btn.getBoundingClientRect();
            list.style.left = rect.left + 'px';
            list.style.top = (rect.bottom + 6) + 'px';
            list.style.display = list.style.display === 'none' ? 'block' : 'none';
        });

        // hide on outside click
        document.addEventListener('click', (e)=>{
            if (!btn.contains(e.target) && !list.contains(e.target)) list.style.display = 'none';
        });
    }

    // expose API
    window.__i18n = { initI18n, setLanguage, getLanguage: getStored };
    // auto-init
    try { initI18n(); } catch(e) { /* fail silently */ }

})(window);
