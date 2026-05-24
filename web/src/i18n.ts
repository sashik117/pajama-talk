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
  | "learned"
  | "today"
  | "dailyFocus"
  | "dailyFocusSub"
  | "voicePrimary"
  | "tapToSpeak"
  | "listening"
  | "speechUnsupported"
  | "speechError"
  | "textFallback"
  | "reviewEmpty"
  | "profile"
  | "learningVibe"
  | "aiTone"
  | "adaptiveDrop";

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
  aura: "Home",
  speak: "Speaking",
  storage: "Dictionary",
  vibe: "Profile",
  learningLanguage: "Learning language",
  uiLanguage: "Interface language",
  nativeLanguage: "Explanation language",
  contextTitle: "Context",
  contextPlaceholder: "Paste a phrase, subtitle, post, comment, or song line",
  analyze: "Analyze",
  addWords: "Add words",
  newWord: "New word",
  add: "Add",
  myWords: "Words",
  review: "Review",
  forgot: "Forgot",
  remember: "Remember",
  rooms: "Rooms",
  hints: "Hints",
  send: "Send",
  stats: "Stats",
  logOut: "Log out",
  grammar: "Grammar",
  due: "due",
  learned: "learned",
  today: "Today",
  dailyFocus: "Small useful practice",
  dailyFocusSub: "Speak once, review due words, or parse one real phrase.",
  voicePrimary: "Voice mode. Press the mic and answer out loud.",
  tapToSpeak: "Tap to speak",
  listening: "Listening",
  speechUnsupported: "This browser does not expose speech recognition. Use the text fallback for now.",
  speechError: "Could not hear that. Try again.",
  textFallback: "Text fallback",
  reviewEmpty: "Nothing due right now.",
  profile: "Profile",
  learningVibe: "Learning vibe",
  aiTone: "AI tone",
  adaptiveDrop: "Adaptive drop"
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
    aura: "Головна",
    speak: "Спікінг",
    storage: "Словник",
    vibe: "Профіль",
    learningLanguage: "Мова навчання",
    uiLanguage: "Мова інтерфейсу",
    nativeLanguage: "Мова пояснень",
    contextTitle: "Контекст",
    contextPlaceholder: "Встав фразу, субтитр, пост, комент або рядок з пісні",
    analyze: "Розібрати",
    addWords: "Додати слова",
    newWord: "Нове слово",
    add: "Додати",
    myWords: "Слова",
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
    learned: "вивчено",
    today: "Сьогодні",
    dailyFocus: "Маленька корисна практика",
    dailyFocusSub: "Скажи одну фразу голосом, повтори слова або розбери реальний текст.",
    voicePrimary: "Голосовий режим. Натисни мікрофон і відповідай вголос.",
    tapToSpeak: "Натисни і говори",
    listening: "Слухаю",
    speechUnsupported: "Браузер не дав розпізнавання голосу. Поки є текстовий fallback.",
    speechError: "Не почула фразу. Спробуй ще раз.",
    textFallback: "Текстовий fallback",
    reviewEmpty: "Зараз нічого повторювати.",
    profile: "Профіль",
    learningVibe: "Вайб навчання",
    aiTone: "Тон ШІ",
    adaptiveDrop: "Адаптивна підказка"
  },
  pl: {
    tagline: "Miękka praktyka języka w twoim tempie.",
    aura: "Start",
    speak: "Mówienie",
    storage: "Słownik",
    vibe: "Profil",
    learningLanguage: "Język nauki",
    uiLanguage: "Język interfejsu",
    nativeLanguage: "Język wyjaśnień",
    analyze: "Analizuj",
    review: "Powtórka",
    tapToSpeak: "Naciśnij i mów"
  },
  sk: { aura: "Domov", speak: "Hovorenie", storage: "Slovník", vibe: "Profil", tapToSpeak: "Stlač a hovor" },
  cs: { aura: "Domů", speak: "Mluvení", storage: "Slovník", vibe: "Profil", tapToSpeak: "Stiskni a mluv" },
  fr: { aura: "Accueil", speak: "Oral", storage: "Dico", vibe: "Profil", tapToSpeak: "Appuie et parle" },
  es: { aura: "Inicio", speak: "Hablar", storage: "Diccionario", vibe: "Perfil", tapToSpeak: "Pulsa y habla" },
  it: { aura: "Home", speak: "Parlato", storage: "Vocabolario", vibe: "Profilo", tapToSpeak: "Premi e parla" },
  de: { aura: "Start", speak: "Sprechen", storage: "Wortschatz", vibe: "Profil", tapToSpeak: "Tippen und sprechen" },
  pt: { aura: "Início", speak: "Fala", storage: "Vocabulário", vibe: "Perfil", tapToSpeak: "Toca e fala" },
  tr: { aura: "Ana sayfa", speak: "Konuşma", storage: "Sözlük", vibe: "Profil", tapToSpeak: "Dokun ve konuş" },
  ja: { aura: "ホーム", speak: "スピーキング", storage: "単語帳", vibe: "プロフィール", tapToSpeak: "押して話す" },
  ko: { aura: "홈", speak: "말하기", storage: "단어장", vibe: "프로필", tapToSpeak: "눌러서 말하기" },
  zh: { aura: "主页", speak: "口语", storage: "词库", vibe: "资料", tapToSpeak: "点击说话" }
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
