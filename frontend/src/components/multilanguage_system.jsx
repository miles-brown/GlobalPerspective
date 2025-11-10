import React, { useState, useEffect, createContext, useContext } from 'react';
import { Globe, ChevronDown, Check, Translate, Volume2, VolumeX } from 'lucide-react';

// Language Context
const LanguageContext = createContext();

// Language data
const languages = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸',
    rtl: false,
    translations: {
      // Navigation
      home: 'Home',
      worldAffairs: 'World Affairs',
      business: 'Business',
      technology: 'Technology',
      culture: 'Culture',
      politics: 'Politics',
      search: 'Search',
      login: 'Login',
      register: 'Register',
      
      // Content
      readMore: 'Read More',
      readingTime: 'min read',
      publishedOn: 'Published on',
      author: 'Author',
      category: 'Category',
      tags: 'Tags',
      comments: 'Comments',
      share: 'Share',
      
      // Search
      searchPlaceholder: 'Search articles, topics, authors...',
      searchResults: 'Search Results',
      noResults: 'No results found',
      filters: 'Filters',
      sortBy: 'Sort by',
      
      // Comments
      writeComment: 'Write a comment...',
      postComment: 'Post Comment',
      reply: 'Reply',
      like: 'Like',
      report: 'Report',
      
      // Common
      loading: 'Loading...',
      save: 'Save',
      cancel: 'Cancel',
      edit: 'Edit',
      delete: 'Delete',
      confirm: 'Confirm',
      
      // Footer
      aboutUs: 'About Us',
      contactUs: 'Contact Us',
      privacyPolicy: 'Privacy Policy',
      termsOfService: 'Terms of Service',
      
      // Accessibility
      listenToArticle: 'Listen to this article',
      stopListening: 'Stop listening',
      increaseTextSize: 'Increase text size',
      decreaseTextSize: 'Decrease text size',
      highContrast: 'High contrast mode'
    }
  },
  
  es: {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    flag: '🇪🇸',
    rtl: false,
    translations: {
      home: 'Inicio',
      worldAffairs: 'Asuntos Mundiales',
      business: 'Negocios',
      technology: 'Tecnología',
      culture: 'Cultura',
      politics: 'Política',
      search: 'Buscar',
      login: 'Iniciar Sesión',
      register: 'Registrarse',
      
      readMore: 'Leer Más',
      readingTime: 'min de lectura',
      publishedOn: 'Publicado el',
      author: 'Autor',
      category: 'Categoría',
      tags: 'Etiquetas',
      comments: 'Comentarios',
      share: 'Compartir',
      
      searchPlaceholder: 'Buscar artículos, temas, autores...',
      searchResults: 'Resultados de Búsqueda',
      noResults: 'No se encontraron resultados',
      filters: 'Filtros',
      sortBy: 'Ordenar por',
      
      writeComment: 'Escribe un comentario...',
      postComment: 'Publicar Comentario',
      reply: 'Responder',
      like: 'Me gusta',
      report: 'Reportar',
      
      loading: 'Cargando...',
      save: 'Guardar',
      cancel: 'Cancelar',
      edit: 'Editar',
      delete: 'Eliminar',
      confirm: 'Confirmar',
      
      aboutUs: 'Acerca de Nosotros',
      contactUs: 'Contáctanos',
      privacyPolicy: 'Política de Privacidad',
      termsOfService: 'Términos de Servicio',
      
      listenToArticle: 'Escuchar este artículo',
      stopListening: 'Dejar de escuchar',
      increaseTextSize: 'Aumentar tamaño del texto',
      decreaseTextSize: 'Disminuir tamaño del texto',
      highContrast: 'Modo de alto contraste'
    }
  },
  
  fr: {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    flag: '🇫🇷',
    rtl: false,
    translations: {
      home: 'Accueil',
      worldAffairs: 'Affaires Mondiales',
      business: 'Affaires',
      technology: 'Technologie',
      culture: 'Culture',
      politics: 'Politique',
      search: 'Rechercher',
      login: 'Se Connecter',
      register: 'S\'inscrire',
      
      readMore: 'Lire Plus',
      readingTime: 'min de lecture',
      publishedOn: 'Publié le',
      author: 'Auteur',
      category: 'Catégorie',
      tags: 'Étiquettes',
      comments: 'Commentaires',
      share: 'Partager',
      
      searchPlaceholder: 'Rechercher des articles, sujets, auteurs...',
      searchResults: 'Résultats de Recherche',
      noResults: 'Aucun résultat trouvé',
      filters: 'Filtres',
      sortBy: 'Trier par',
      
      writeComment: 'Écrire un commentaire...',
      postComment: 'Publier le Commentaire',
      reply: 'Répondre',
      like: 'J\'aime',
      report: 'Signaler',
      
      loading: 'Chargement...',
      save: 'Sauvegarder',
      cancel: 'Annuler',
      edit: 'Modifier',
      delete: 'Supprimer',
      confirm: 'Confirmer',
      
      aboutUs: 'À Propos',
      contactUs: 'Nous Contacter',
      privacyPolicy: 'Politique de Confidentialité',
      termsOfService: 'Conditions d\'Utilisation',
      
      listenToArticle: 'Écouter cet article',
      stopListening: 'Arrêter l\'écoute',
      increaseTextSize: 'Augmenter la taille du texte',
      decreaseTextSize: 'Diminuer la taille du texte',
      highContrast: 'Mode contraste élevé'
    }
  },
  
  de: {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    flag: '🇩🇪',
    rtl: false,
    translations: {
      home: 'Startseite',
      worldAffairs: 'Weltangelegenheiten',
      business: 'Wirtschaft',
      technology: 'Technologie',
      culture: 'Kultur',
      politics: 'Politik',
      search: 'Suchen',
      login: 'Anmelden',
      register: 'Registrieren',
      
      readMore: 'Mehr Lesen',
      readingTime: 'Min. Lesezeit',
      publishedOn: 'Veröffentlicht am',
      author: 'Autor',
      category: 'Kategorie',
      tags: 'Schlagwörter',
      comments: 'Kommentare',
      share: 'Teilen',
      
      searchPlaceholder: 'Artikel, Themen, Autoren suchen...',
      searchResults: 'Suchergebnisse',
      noResults: 'Keine Ergebnisse gefunden',
      filters: 'Filter',
      sortBy: 'Sortieren nach',
      
      writeComment: 'Kommentar schreiben...',
      postComment: 'Kommentar Veröffentlichen',
      reply: 'Antworten',
      like: 'Gefällt mir',
      report: 'Melden',
      
      loading: 'Laden...',
      save: 'Speichern',
      cancel: 'Abbrechen',
      edit: 'Bearbeiten',
      delete: 'Löschen',
      confirm: 'Bestätigen',
      
      aboutUs: 'Über Uns',
      contactUs: 'Kontakt',
      privacyPolicy: 'Datenschutzrichtlinie',
      termsOfService: 'Nutzungsbedingungen',
      
      listenToArticle: 'Artikel anhören',
      stopListening: 'Anhören stoppen',
      increaseTextSize: 'Textgröße erhöhen',
      decreaseTextSize: 'Textgröße verringern',
      highContrast: 'Hoher Kontrast Modus'
    }
  },
  
  zh: {
    code: 'zh',
    name: 'Chinese',
    nativeName: '中文',
    flag: '🇨🇳',
    rtl: false,
    translations: {
      home: '首页',
      worldAffairs: '国际事务',
      business: '商业',
      technology: '科技',
      culture: '文化',
      politics: '政治',
      search: '搜索',
      login: '登录',
      register: '注册',
      
      readMore: '阅读更多',
      readingTime: '分钟阅读',
      publishedOn: '发布于',
      author: '作者',
      category: '分类',
      tags: '标签',
      comments: '评论',
      share: '分享',
      
      searchPlaceholder: '搜索文章、主题、作者...',
      searchResults: '搜索结果',
      noResults: '未找到结果',
      filters: '筛选',
      sortBy: '排序',
      
      writeComment: '写评论...',
      postComment: '发表评论',
      reply: '回复',
      like: '点赞',
      report: '举报',
      
      loading: '加载中...',
      save: '保存',
      cancel: '取消',
      edit: '编辑',
      delete: '删除',
      confirm: '确认',
      
      aboutUs: '关于我们',
      contactUs: '联系我们',
      privacyPolicy: '隐私政策',
      termsOfService: '服务条款',
      
      listenToArticle: '收听此文章',
      stopListening: '停止收听',
      increaseTextSize: '增大字体',
      decreaseTextSize: '减小字体',
      highContrast: '高对比度模式'
    }
  },
  
  ar: {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    flag: '🇸🇦',
    rtl: true,
    translations: {
      home: 'الرئيسية',
      worldAffairs: 'الشؤون العالمية',
      business: 'الأعمال',
      technology: 'التكنولوجيا',
      culture: 'الثقافة',
      politics: 'السياسة',
      search: 'بحث',
      login: 'تسجيل الدخول',
      register: 'التسجيل',
      
      readMore: 'اقرأ المزيد',
      readingTime: 'دقيقة قراءة',
      publishedOn: 'نُشر في',
      author: 'الكاتب',
      category: 'الفئة',
      tags: 'العلامات',
      comments: 'التعليقات',
      share: 'مشاركة',
      
      searchPlaceholder: 'البحث في المقالات والمواضيع والكتاب...',
      searchResults: 'نتائج البحث',
      noResults: 'لم يتم العثور على نتائج',
      filters: 'المرشحات',
      sortBy: 'ترتيب حسب',
      
      writeComment: 'اكتب تعليقاً...',
      postComment: 'نشر التعليق',
      reply: 'رد',
      like: 'إعجاب',
      report: 'إبلاغ',
      
      loading: 'جاري التحميل...',
      save: 'حفظ',
      cancel: 'إلغاء',
      edit: 'تحرير',
      delete: 'حذف',
      confirm: 'تأكيد',
      
      aboutUs: 'من نحن',
      contactUs: 'اتصل بنا',
      privacyPolicy: 'سياسة الخصوصية',
      termsOfService: 'شروط الخدمة',
      
      listenToArticle: 'استمع لهذا المقال',
      stopListening: 'إيقاف الاستماع',
      increaseTextSize: 'زيادة حجم النص',
      decreaseTextSize: 'تقليل حجم النص',
      highContrast: 'وضع التباين العالي'
    }
  }
};

// Language Provider Component
export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [isListening, setIsListening] = useState(false);

  // Load saved language preference
  useEffect(() => {
    const savedLanguage = localStorage.getItem('preferred-language');
    if (savedLanguage && languages[savedLanguage]) {
      setCurrentLanguage(savedLanguage);
    } else {
      // Detect browser language
      const browserLang = navigator.language.split('-')[0];
      if (languages[browserLang]) {
        setCurrentLanguage(browserLang);
      }
    }
  }, []);

  // Update document direction and language
  useEffect(() => {
    const lang = languages[currentLanguage];
    document.documentElement.lang = lang.code;
    document.documentElement.dir = lang.rtl ? 'rtl' : 'ltr';
    
    // Save preference
    localStorage.setItem('preferred-language', currentLanguage);
  }, [currentLanguage]);

  // Translation function
  const t = (key) => {
    const lang = languages[currentLanguage];
    return lang.translations[key] || key;
  };

  // Text-to-speech function
  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = languages[currentLanguage].code;
      utterance.rate = 0.8;
      utterance.pitch = 1;
      
      utterance.onstart = () => setIsListening(true);
      utterance.onend = () => setIsListening(false);
      utterance.onerror = () => setIsListening(false);
      
      speechSynthesis.speak(utterance);
    }
  };

  // Stop speech
  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsListening(false);
    }
  };

  const value = {
    currentLanguage,
    setCurrentLanguage,
    languages,
    t,
    isRTL: languages[currentLanguage].rtl,
    speakText,
    stopSpeaking,
    isListening
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

// Hook to use language context
export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Language Selector Component
export const LanguageSelector = ({ className = '' }) => {
  const { currentLanguage, setCurrentLanguage, languages, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const currentLang = languages[currentLanguage];

  return (
    <div className={`language-selector relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <Globe className="w-4 h-4" />
        <span className="text-sm">{currentLang.flag}</span>
        <span className="text-sm font-medium hidden sm:inline">{currentLang.nativeName}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-48">
          {Object.values(languages).map((lang) => (
            <button
              key={lang.code}
              onClick={() => {
                setCurrentLanguage(lang.code);
                setIsOpen(false);
              }}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg">{lang.flag}</span>
                <div className="text-left">
                  <div className="font-medium text-gray-900">{lang.nativeName}</div>
                  <div className="text-sm text-gray-500">{lang.name}</div>
                </div>
              </div>
              {currentLanguage === lang.code && (
                <Check className="w-4 h-4 text-blue-600" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// Text-to-Speech Component
export const TextToSpeech = ({ text, className = '' }) => {
  const { speakText, stopSpeaking, isListening, t } = useLanguage();

  return (
    <button
      onClick={() => isListening ? stopSpeaking() : speakText(text)}
      className={`flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors ${className}`}
      title={isListening ? t('stopListening') : t('listenToArticle')}
    >
      {isListening ? (
        <VolumeX className="w-4 h-4 text-red-600" />
      ) : (
        <Volume2 className="w-4 h-4 text-gray-600" />
      )}
      <span className="text-sm hidden sm:inline">
        {isListening ? t('stopListening') : t('listenToArticle')}
      </span>
    </button>
  );
};

// Translated Text Component
export const TranslatedText = ({ textKey, fallback, className = '' }) => {
  const { t } = useLanguage();
  
  return (
    <span className={className}>
      {t(textKey) || fallback || textKey}
    </span>
  );
};

// Auto-translate Component for dynamic content
export const AutoTranslate = ({ text, targetLanguage, className = '' }) => {
  const [translatedText, setTranslatedText] = useState(text);
  const [isTranslating, setIsTranslating] = useState(false);
  const { currentLanguage } = useLanguage();

  const translateText = async () => {
    if (currentLanguage === 'en' || !text) return;

    setIsTranslating(true);
    try {
      // In a real implementation, you would call a translation API
      // For demo purposes, we'll just show the original text
      // Example: Google Translate API, Microsoft Translator, etc.
      
      const response = await fetch('/api/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          from: 'en',
          to: currentLanguage
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTranslatedText(data.translatedText);
      }
    } catch (error) {
      console.error('Translation error:', error);
    } finally {
      setIsTranslating(false);
    }
  };

  useEffect(() => {
    translateText();
  }, [text, currentLanguage]);

  return (
    <span className={className}>
      {isTranslating ? (
        <span className="inline-flex items-center">
          <Translate className="w-4 h-4 mr-1 animate-spin" />
          Translating...
        </span>
      ) : (
        translatedText
      )}
    </span>
  );
};

// RTL-aware layout component
export const RTLContainer = ({ children, className = '' }) => {
  const { isRTL } = useLanguage();
  
  return (
    <div className={`${className} ${isRTL ? 'rtl-layout' : 'ltr-layout'}`}>
      {children}
    </div>
  );
};

export default {
  LanguageProvider,
  LanguageSelector,
  TextToSpeech,
  TranslatedText,
  AutoTranslate,
  RTLContainer,
  useLanguage
};

