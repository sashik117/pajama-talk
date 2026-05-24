export type UiLocale =
  | "uk"
  | "en"
  | "pl"
  | "sk"
  | "cs"
  | "fr"
  | "es"
  | "it"
  | "de"
  | "pt"
  | "tr"
  | "ja"
  | "ko"
  | "zh";

export type CopyKey =
  | "tagline"
  | "email"
  | "password"
  | "name"
  | "login"
  | "register"
  | "create"
  | "demo"
  | "aura"
  | "speak"
  | "storage"
  | "vibe"
  | "learningLanguage"
  | "uiLanguage"
  | "nativeLanguage"
  | "contextTitle"
  | "contextPlaceholder"
  | "analyze"
  | "addWords"
  | "newWord"
  | "add"
  | "myWords"
  | "review"
  | "forgot"
  | "remember"
  | "rooms"
  | "hints"
  | "send"
  | "stats"
  | "logOut"
  | "grammar"
  | "due"
  | "learned";

export const uiLocales: Array<{ code: UiLocale; label: string; short: string }> = [
  { code: "uk", label: "Українська", short: "UK" },
  { code: "en", label: "English", short: "EN" },
  { code: "pl", label: "Polski", short: "PL" },
  { code: "sk", label: "Slovenčina", short: "SK" },
  { code: "cs", label: "Čeština", short: "CS" },
  { code: "fr", label: "Français", short: "FR" },
  { code: "es", label: "Español", short: "ES" },
  { code: "it", label: "Italiano", short: "IT" },
  { code: "de", label: "Deutsch", short: "DE" },
  { code: "pt", label: "Português", short: "PT" },
  { code: "tr", label: "Türkçe", short: "TR" },
  { code: "ja", label: "日本語", short: "JA" },
  { code: "ko", label: "한국어", short: "KO" },
  { code: "zh", label: "中文", short: "ZH" }
];

const base: Record<CopyKey, string> = {
  tagline: "Soft language practice, your pace.",
  email: "Email",
  password: "Password",
  name: "Name",
  login: "Log in",
  register: "Create account",
  create: "Create",
  demo: "Continue demo",
  aura: "Aura",
  speak: "Speak",
  storage: "Storage",
  vibe: "Vibe",
  learningLanguage: "Learning language",
  uiLanguage: "Interface language",
  nativeLanguage: "Explanation language",
  contextTitle: "Context Buddy",
  contextPlaceholder: "Paste a line that caught you",
  analyze: "Analyze",
  addWords: "Add words",
  newWord: "New word",
  add: "Add",
  myWords: "My words",
  review: "Review",
  forgot: "Forgot",
  remember: "Remember",
  rooms: "Rooms",
  hints: "Hints",
  send: "Send",
  stats: "Stats",
  logOut: "Log out",
  grammar: "Grammar drop",
  due: "due",
  learned: "learned"
};

const copies: Partial<Record<UiLocale, Partial<Record<CopyKey, string>>>> = {
  uk: {
    tagline: "М'яка мовна практика у твоєму темпі.",
    email: "Пошта",
    password: "Пароль",
    name: "Ім'я",
    login: "Увійти",
    register: "Створити акаунт",
    create: "Створити",
    demo: "Демо-вхід",
    aura: "Аура",
    speak: "Спікінг",
    storage: "Словник",
    vibe: "Вайб",
    learningLanguage: "Мова навчання",
    uiLanguage: "Мова інтерфейсу",
    nativeLanguage: "Мова пояснень",
    contextTitle: "Context Buddy",
    contextPlaceholder: "Встав текст, який тебе зачепив",
    analyze: "Розібрати",
    addWords: "Додати слова",
    newWord: "Нове слово",
    add: "Додати",
    myWords: "Мої слова",
    review: "Повторення",
    forgot: "Забула",
    remember: "Пам'ятаю",
    rooms: "Кімнати",
    hints: "Підказки",
    send: "Надіслати",
    stats: "Стата",
    logOut: "Вийти",
    grammar: "Граматика",
    due: "до повторення",
    learned: "вивчено"
  },
  pl: {
    tagline: "Miękka praktyka języka w twoim tempie.",
    login: "Zaloguj",
    register: "Utwórz konto",
    demo: "Tryb demo",
    storage: "Słownik",
    vibe: "Klimat",
    learningLanguage: "Język nauki",
    uiLanguage: "Język interfejsu",
    nativeLanguage: "Język wyjaśnień",
    analyze: "Analizuj",
    addWords: "Dodaj słowa",
    review: "Powtórka",
    forgot: "Nie pamiętam",
    remember: "Pamiętam",
    send: "Wyślij",
    logOut: "Wyloguj"
  },
  sk: {
    tagline: "Jemná jazyková prax vlastným tempom.",
    login: "Prihlásiť",
    register: "Vytvoriť účet",
    demo: "Demo vstup",
    storage: "Slovník",
    learningLanguage: "Jazyk učenia",
    uiLanguage: "Jazyk rozhrania",
    nativeLanguage: "Jazyk vysvetlení",
    analyze: "Analyzovať",
    review: "Opakovanie",
    send: "Odoslať"
  },
  cs: {
    tagline: "Jemná jazyková praxe vlastním tempem.",
    login: "Přihlásit",
    register: "Vytvořit účet",
    demo: "Demo vstup",
    storage: "Slovník",
    learningLanguage: "Jazyk učení",
    uiLanguage: "Jazyk rozhraní",
    nativeLanguage: "Jazyk vysvětlení",
    analyze: "Analyzovat",
    review: "Opakování",
    send: "Odeslat"
  },
  fr: {
    tagline: "Une pratique douce, à ton rythme.",
    login: "Connexion",
    register: "Créer un compte",
    demo: "Mode démo",
    storage: "Dico",
    learningLanguage: "Langue apprise",
    uiLanguage: "Langue interface",
    nativeLanguage: "Langue d'explication",
    analyze: "Analyser",
    review: "Révision",
    send: "Envoyer",
    logOut: "Déconnexion"
  },
  es: {
    tagline: "Práctica suave, a tu ritmo.",
    login: "Entrar",
    register: "Crear cuenta",
    demo: "Modo demo",
    storage: "Diccionario",
    learningLanguage: "Idioma de estudio",
    uiLanguage: "Idioma de interfaz",
    nativeLanguage: "Idioma de explicación",
    analyze: "Analizar",
    review: "Repasar",
    send: "Enviar",
    logOut: "Salir"
  },
  it: {
    tagline: "Pratica morbida, al tuo ritmo.",
    login: "Accedi",
    register: "Crea account",
    demo: "Demo",
    storage: "Vocabolario",
    learningLanguage: "Lingua da studiare",
    uiLanguage: "Lingua interfaccia",
    nativeLanguage: "Lingua spiegazioni",
    analyze: "Analizza",
    review: "Ripasso",
    send: "Invia"
  },
  de: {
    tagline: "Sanftes Sprachtraining in deinem Tempo.",
    login: "Einloggen",
    register: "Konto erstellen",
    demo: "Demo starten",
    storage: "Wortschatz",
    learningLanguage: "Lernsprache",
    uiLanguage: "Oberfläche",
    nativeLanguage: "Erklärungssprache",
    analyze: "Analysieren",
    review: "Wiederholen",
    send: "Senden"
  },
  pt: {
    tagline: "Prática leve, no teu ritmo.",
    login: "Entrar",
    register: "Criar conta",
    demo: "Modo demo",
    storage: "Vocabulário",
    learningLanguage: "Idioma de estudo",
    uiLanguage: "Idioma da interface",
    nativeLanguage: "Idioma de explicação",
    analyze: "Analisar",
    review: "Revisão",
    send: "Enviar"
  },
  tr: {
    tagline: "Kendi hızında yumuşak dil pratiği.",
    login: "Giriş",
    register: "Hesap oluştur",
    demo: "Demo",
    storage: "Sözlük",
    learningLanguage: "Öğrenilen dil",
    uiLanguage: "Arayüz dili",
    nativeLanguage: "Açıklama dili",
    analyze: "Analiz et",
    review: "Tekrar",
    send: "Gönder"
  },
  ja: { tagline: "自分のペースでやさしく練習。", login: "ログイン", register: "登録", demo: "デモ", storage: "単語帳", review: "復習", send: "送信" },
  ko: { tagline: "내 속도에 맞춘 부드러운 언어 연습.", login: "로그인", register: "가입", demo: "데모", storage: "단어장", review: "복습", send: "보내기" },
  zh: { tagline: "按你的节奏轻松练习语言。", login: "登录", register: "注册", demo: "演示", storage: "词库", review: "复习", send: "发送" }
};

export function t(locale: UiLocale, key: CopyKey): string {
  return copies[locale]?.[key] ?? base[key];
}

export const learningLanguages = [
  { code: "en", label: "English", short: "EN", sample: "cozy" },
  { code: "sk", label: "Slovak", short: "SK", sample: "ahoj" },
  { code: "pl", label: "Polish", short: "PL", sample: "spoko" },
  { code: "cs", label: "Czech", short: "CS", sample: "pohoda" },
  { code: "fr", label: "French", short: "FR", sample: "coucou" },
  { code: "es", label: "Spanish", short: "ES", sample: "vale" },
  { code: "it", label: "Italian", short: "IT", sample: "allora" },
  { code: "ko", label: "Korean", short: "KO", sample: "안녕" },
  { code: "ja", label: "Japanese", short: "JA", sample: "すごい" },
  { code: "zh", label: "Chinese", short: "ZH", sample: "你好" },
  { code: "tr", label: "Turkish", short: "TR", sample: "merhaba" }
] as const;

export const nativeLanguages = [
  { code: "uk", label: "Ukrainian", short: "UK" },
  { code: "ru", label: "Russian", short: "RU" },
  ...learningLanguages.map((language) => ({
    code: language.code,
    label: language.label,
    short: language.short
  }))
];

export function languageName(code: string): string {
  return nativeLanguages.find((language) => language.code === code)?.label ?? "Ukrainian";
}
