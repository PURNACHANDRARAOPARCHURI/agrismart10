/* Lightweight client-side i18n for static pages
   - Provides translations for en, hi, te, kn, ta
   - Scans the document for data-i18n attributes and data-i18n-placeholder/value
   - Persists selected language in localStorage under 'lang'
   - Attaches a small language chooser to an element with id 'language-btn' or class 'language-selector'
*/
(function(window){
    const STORAGE_KEY = 'lang';
    const DEFAULT = 'en';

    const TRANSLATIONS = {
        en: {
            tile_recommend: '💡 Crop Recommendation',
            tile_forecast: '📈 Price Forecast',
            tile_info: '🌾 Crop Info',
            tile_calendar: '📅 Calendar',
            tile_profile: '👤 Profile',
            page_title: '📊 Crop Information',
            select_crop: 'Select a Crop for Price Analysis',
            loading: 'Loading crop information...',
            back_to_home: '← Back to Home',
            quick_actions: 'Quick Actions'
        ,
            feature_info: 'Crop Information',
            feature_info_desc: 'Browse crop-specific details, market prices, and quick tools like recommendations and forecasts.',
            btn_view_info: 'View Crop Info',
            feature_recommend: 'Crop Recommendation',
            feature_recommend_desc: 'Receive intelligent crop recommendations based on your soil type, location, and seasonal conditions.',
            btn_explore_recommend: 'Explore Feature',
            feature_forecast: 'Price Forecast',
            feature_forecast_desc: 'View price predictions, market trends, and get profitability advice for your crops over the next 6 months.',
            btn_explore_forecast: 'Explore Feature'
        ,
            cost_of_cultivation: 'Cost of Cultivation:',
            expected_yield: 'Expected Yield:',
            estimated_profit: 'Estimated Profit:',
            current_market_price: 'Current Market Price:',
            government_msp: 'Government MSP:',
            recommendation_note: 'Note: The recommendation model was trained on N, P, K and pH values. Other fields are optional.'
        },
        hi: {
            tile_recommend: '💡 फसल सिफारिश',
            tile_forecast: '📈 मूल्य पूर्वानुमान',
            tile_info: '🌾 फ़सल जानकारी',
            tile_calendar: '📅 कैलेंडर',
            tile_profile: '👤 प्रोफ़ाइल',
            page_title: '📊 फसल जानकारी',
            select_crop: 'मूल्य विश्लेषण के लिए फसल चुनें',
            loading: 'फसल की जानकारी लोड हो रही है...',
            back_to_home: '← होम पर वापस',
            quick_actions: 'त्वरित क्रियाएँ'
        ,
            feature_info: 'फ़सल जानकारी',
            feature_info_desc: 'फसल-विशिष्ट जानकारी, बाजार मूल्य और त्वरित उपकरण जैसे सिफारिशें और पूर्वानुमान ब्राउज़ करें।',
            btn_view_info: 'फ़सल देखें',
            feature_recommend: 'फसल सिफारिश',
            feature_recommend_desc: 'आपकी मिट्टी, स्थान और मौसमी परिस्थितियों के आधार पर बुद्धिमान फसल सिफारिशें प्राप्त करें।',
            btn_explore_recommend: 'फीचर एक्सप्लोर करें',
            feature_forecast: 'मूल्य पूर्वानुमान',
            feature_forecast_desc: 'मूल्य भविष्यवाणियाँ देखें, बाजार रुझान और अगला 6 महीने के लिए लाभदायक सलाह प्राप्त करें।',
            btn_explore_forecast: 'फीचर एक्सप्लोर करें'
        ,
            cost_of_cultivation: 'खेती लागत:',
            expected_yield: 'अपेक्षित उपज:',
            estimated_profit: 'अनुमानित लाभ:',
            current_market_price: 'वर्तमान बाजार मूल्य:',
            government_msp: 'सरकारी MSP:',
            recommendation_note: 'नोट: सिफारिश मॉडल N, P, K और pH पर प्रशिक्षित है। अन्य फ़ील्ड वैकल्पिक हैं।'
        },
        te: {
            tile_recommend: '💡 పంట సిఫార్సు',
            tile_forecast: '📈 ధర అంచనా',
            tile_info: '🌾 పంట సమాచారం',
            tile_calendar: '📅 క్యాలెండర్',
            tile_profile: '👤 ప్రొఫైల్',
            page_title: '📊 పంట సమాచారం',
            select_crop: 'ధర విశ్లేషణ కోసం పంటను ఎంచుకోండి',
            loading: 'పంట సమాచారం లోడ్ అవుతోంది...',
            back_to_home: '← హోమ్‌కు తిరిగి'
        ,
            feature_info: 'పంట సమాచారం',
            feature_info_desc: 'పంట-సంబంధిత వివరాలు, మార్కెట్ ధరలు మరియు సిఫార్సులు మరియు అంచనాల వంటి సాధనాలు బ్రౌజ్ చేయండి.',
            btn_view_info: 'పంట చూడండి',
            feature_recommend: 'పంట సిఫార్సు',
            feature_recommend_desc: 'మీ మట్టి రకం, స్థానం మరియు కాలపరిమాణ పరిస్థితుల ఆధారంగా తెలివైన పంట సూచనలు పొందండి.',
            btn_explore_recommend: 'ఫీచర్ एक्सplore',
            feature_forecast: 'ధర అంచనా',
            feature_forecast_desc: 'ధర గణనల్ని చూడండి, మార్కెట్ ఒరియెంటేషన్‌లు మరియు తదుపరి 6 నెలల కోసం లాభదాయక సలహా పొందండి.',
            btn_explore_forecast: 'ఫీచర్ అన్వేషించండి'
        ,
            cost_of_cultivation: 'వితరణ వ్యయం:',
            expected_yield: 'అనుమానిత దిగుబడి:',
            estimated_profit: 'అంచనా లాభం:',
            current_market_price: 'ప్రస్తుత మార్కెట్ ధర:',
            government_msp: 'ప్రభుత్వ MSP:',
            recommendation_note: 'గమనిక: సిఫార్సు మోడల్ N, P, K మరియు pH పై ట్రెయిన్ చేయబడింది. ఇతర ఫీల్డ్స్ైవల్డ్.'
        },
        kn: {
            tile_recommend: '💡 ಬೆಳೆ ಶಿಫಾರಸು',
            tile_forecast: '📈 ಬೆಲೆ ಭವಿಷ್ಯವಾಣಿ',
            tile_info: '🌾 ಬೆಳೆ ಮಾಹಿತಿ',
            tile_calendar: '📅 ಕ್ಯಾಲೆಂಡರ್',
            tile_profile: '👤 ಪ್ರೊಫೈಲ್',
            page_title: '📊 ಬೆಳೆ ಮಾಹಿತಿ',
            select_crop: 'ಬೆಲೆ ವಿಶ್ಲೇಷಣೆಗೆ ಬೆಳೆ ಆಯ್ಕೆಮಾಡಿ',
            loading: 'ಬೆಳೆ ಮಾಹಿತಿ ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
            back_to_home: '← ಹೋಮ್‌ಗೆ ಹಿಂದಿರುಗಿ'
        ,
            feature_info: 'ಬೆಳೆ ಮಾಹಿತಿ',
            feature_info_desc: 'ಬೆಳೆ-ಸಂಬಂಧಿತ ವಿವರಗಳು, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಮತ್ತು ಶಿಫಾರಸುಗಳು ಮತ್ತು ಪೂರ್ವಾನುಮಾನಗಳಂತಹ ವೇದಿಕೆಗಳನ್ನು ಬ್ರೌಸ್ ಮಾಡಿ.',
            btn_view_info: 'ಬೆಳೆ ನೋಡಿ',
            feature_recommend: 'ಬೆಳೆ ಶಿಫಾರಸು',
            feature_recommend_desc: 'ನಿಮ್ಮ ಮಣ್ಣಿನ ವಿಧ, ಸ್ಥಳ ಮತ್ತು ಋತುಬಂಧಿತ ಪರಿಸ್ಥಿತೆಗಳ ಆಧಾರದ ಮೇಲೆ ಬುದ್ಧಿವಂತಿಕೆಯ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ.',
            btn_explore_recommend: 'ಫೀಚರ್ ಅನ್ವೇಷಿಸಿ',
            feature_forecast: 'ಬೆಲೆ ಭವಿಷ್ಯವಾಣಿ',
            feature_forecast_desc: 'ಬೆಲೆ ಅಂದಾಜುಗಳನ್ನು ನೋಡಿ, ಮಾರುಕಟ್ಟೆ ಪ್ರವಣತೆ ಮತ್ತು ಮುಂದಿನ 6 ತಿಂಗಳಿಗೂ ಲಾಭದಾಯಕ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಿರಿ.',
            btn_explore_forecast: 'ಫೀಚರ್ ಅನ್ವೇಷಿಸಿ'
        ,
            cost_of_cultivation: 'ಅಗೆಯುವ ವೆಚ್ಚ:',
            expected_yield: 'ಅನಾವಶ್ಯಕ ಫಲ',
            estimated_profit: 'ಅಂದಾಜು ಲಾಭ:',
            current_market_price: 'ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ:',
            government_msp: 'ಸರ್ಕಾರಿ MSP:',
            recommendation_note: 'ಗಮನಿಸಿ: ಶಿಫಾರಸು ಮಾದರಿ N, P, K ಮತ್ತು pH ಮೇಲೆ ತರಬೇತಿ ಪಡೆದಿದೆ. ಇತರೆ ಕ್ಷೇತ್ರಗಳು ಐಚ್ಛಿಕವಾಗಿವೆ.'
        },
        ta: {
            tile_recommend: '💡 பயிர் பரிந்துரை',
            tile_forecast: '📈 விலை கணிப்பு',
            tile_info: '🌾 பயிர் தகவல்',
            tile_calendar: '📅 காலண்டர்',
            tile_profile: '👤 சுயவிவரம்',
            page_title: '📊 பயிர் தகவல்',
            select_crop: 'விலை பகுப்பாய்விற்காக ஒரு பயிரை தேர்வு செய்க',
            loading: 'பயிர் தகவல் ஏற்றப்படுகிறது...',
            back_to_home: '← முகப்பிற்கு திரும்பு'
        ,
            feature_info: 'பயிர் தகவல்',
            feature_info_desc: 'பயிர்-குறித்த விவரங்கள், சந்தை விலைகள் மற்றும் பரிந்துரைகள் மற்றும் கணிப்புகள் போன்ற கருவிகளை உலாவுக.',
            btn_view_info: 'பயிர் பார்க்கவும்',
            feature_recommend: 'பயிர் பரிந்துரை',
            feature_recommend_desc: 'உங்கள் மண் வகை, இடம் மற்றும் பருவத்தைக் கருத்தில் கொண்டு அறிவார்ந்த பரிந்துரைகளைப் பெறுங்கள்.',
            btn_explore_recommend: 'பயன்பாட்டை ஆராய்க',
            feature_forecast: 'விலை கணிப்பு',
            feature_forecast_desc: 'விலை கணிப்புகளைப் பார்க்கவும், சந்தை போக்குகளைப் பார்க்கவும் மற்றும் அடுத்த 6 மாதங்களுக்கு லாபகரமான ஆலோசனையைப் பெறவும்.',
            btn_explore_forecast: 'பயன்பாட்டை ஆராய்க'
        ,
            cost_of_cultivation: 'கاشتுக்கான செலவு:',
            expected_yield: 'எதிர்பார்க்கப்படும் விளைவு:',
            estimated_profit: 'கணிக்கப்பட்ட லாபம்:',
            current_market_price: 'தற்போதைய சந்தை விலை:',
            government_msp: 'அரசு MSP:',
            recommendation_note: 'குறிப்பு: பரிந்துரை மாடல் N, P, K மற்றும் pH இல் பயிற்சி பெற்றது. மற்ற புலங்கள் விருப்பமானவை.'
        }
    };

    function getStored() {
        try { return localStorage.getItem(STORAGE_KEY) || DEFAULT; } catch(e){ return DEFAULT; }
    }

    function setStored(lang) {
        try { localStorage.setItem(STORAGE_KEY, lang); } catch(e){}
    }

    function translateDocument(lang) {
        const map = TRANSLATIONS[lang] || TRANSLATIONS[DEFAULT];
        // data-i18n -> textContent
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (map[key]) el.textContent = map[key];
        });
        // data-i18n-placeholder -> placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (map[key]) el.setAttribute('placeholder', map[key]);
        });
        // data-i18n-value -> value
        document.querySelectorAll('[data-i18n-value]').forEach(el => {
            const key = el.getAttribute('data-i18n-value');
            if (map[key]) el.value = map[key];
        });
        // update language button text
        const btn = document.getElementById('language-btn') || document.querySelector('.language-selector');
        if (btn) {
            const names = { en: 'English', hi: 'हिन्दी', te: 'తెలుగు', kn: 'ಕನ್ನಡ', ta: 'தமிழ்' };
            btn.textContent = `🌐 ${names[lang] || names.en} ▼`;
        }
    }

    function setLanguage(lang) {
        if (!TRANSLATIONS[lang]) lang = DEFAULT;
        setStored(lang);
        translateDocument(lang);
    }

    function initI18n() {
        const lang = getStored();
        // translate on DOMContentLoaded as well
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => translateDocument(lang));
        } else {
            translateDocument(lang);
        }
        attachChooser();
    }

    function attachChooser() {
        const btn = document.getElementById('language-btn') || document.querySelector('.language-selector');
        if (!btn) return;
        // avoid duplicating chooser
        if (btn.__i18n_attached) return;
        btn.__i18n_attached = true;

        const langs = Object.keys(TRANSLATIONS);
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
