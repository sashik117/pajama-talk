import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Bot,
  BriefcaseBusiness,
  Check,
  ChevronDown,
  Coffee,
  GraduationCap,
  Heart,
  Headphones,
  Home,
  Languages,
  LogOut,
  MapPin,
  MessageCircle,
  Mic,
  MicOff,
  PhoneOff,
  Plane,
  Plus,
  Send,
  ShoppingBag,
  Sparkles,
  Stethoscope,
  Trash2,
  User,
  WandSparkles,
  X
} from "lucide-react";
import {
  CallSummaryDto,
  ContextAnalyzeDto,
  GrammarCheckDto,
  GrammarDropDto,
  GrammarTopicDto,
  LearningPathDto,
  SpeakingHintsDto,
  SpeakingRoomDto,
  StatsDto,
  UserDto,
  WordDto
} from "./api";
import { learningLanguages, nativeLanguages, t, UiLocale, uiLocales } from "./i18n";
import { useLearningDataController } from "./hooks/useLearningDataController";
import { useSpeakingController } from "./hooks/useSpeakingController";
import { useVoiceRecorder } from "./hooks/useVoiceRecorder";
import type { SpeakingTransport, VoiceAudioChunk } from "./realtime/speakingClient";
import { ChatProvider, useChatDispatch, useChatState, type ChatLine, type MoodKey } from "./state/chatState";

type TabKey = "aura" | "speak" | "storage" | "vibe";
type SelectOption = { code: string; label: string; short: string; flag: string };
type SpeakingMode = "text" | "call";
type VoiceSpeed = "slow" | "natural" | "fast";
type SpeakingModeCopy = {
  text: string;
  call: string;
  holdToTalk: string;
  speedSlow: string;
  speedNatural: string;
  speedFast: string;
  hangUp: string;
  callSummary: string;
  moodTitle: string;
  echo: string;
  echoCheck: string;
  echoPlaceholder: string;
  moodTired?: string;
  moodCharged?: string;
  moodHard?: string;
};
type ProfileChoiceCopy = {
  setup: string;
  currentLevel: string;
  targetLevel: string;
  effortLevel: string;
  levels: Record<string, string>;
  targets: Record<string, string>;
  efforts: Record<string, string>;
  vibes: Record<string, string>;
  tones: Record<string, string>;
};

const currentLevelOptions = ["Starter", "A1", "A2", "B1", "B2", "C1"] as const;
const targetLevelOptions = ["A1", "A2", "B1", "B2", "C1", "Fluent"] as const;
const effortOptions = ["Light", "Steady", "Intense"] as const;
const vibeOptions = ["Chill", "Normal", "Hardcore"] as const;
const toneOptions = ["Neutral teacher", "Supportive coach", "Precise examiner"] as const;
const voiceSpeedRate: Record<VoiceSpeed, number> = { slow: 0.82, natural: 1, fast: 1.16 };

const speakingModeCopy: Record<UiLocale, SpeakingModeCopy> = {
  en: {
    text: "Text",
    call: "Call",
    holdToTalk: "Tap the mic to speak. Tap again to stop.",
    speedSlow: "Slow",
    speedNatural: "Natural",
    speedFast: "Fast",
    hangUp: "Hang up",
    callSummary: "Call summary",
    moodTitle: "Mood check",
    echo: "Echo",
    echoCheck: "Check echo",
    echoPlaceholder: "Type what you said",
    moodTired: "soft mode",
    moodCharged: "more energy",
    moodHard: "no pressure"
  },
  uk: {
    text: "Текст",
    call: "Дзвінок",
    holdToTalk: "Натисни мікрофон, щоб говорити. Натисни ще раз, щоб зупинити.",
    speedSlow: "Повільно",
    speedNatural: "Нормально",
    speedFast: "Швидко",
    hangUp: "Завершити",
    callSummary: "Підсумок дзвінка",
    moodTitle: "Настрій перед кімнатою",
    echo: "Ехо",
    echoCheck: "Перевірити ехо",
    echoPlaceholder: "Впиши, що сказала",
    moodTired: "м'яко",
    moodCharged: "енергійно",
    moodHard: "без тиску"
  },
  ru: {
    text: "Текст",
    call: "Звонок",
    holdToTalk: "Нажми микрофон, чтобы говорить. Нажми ещё раз, чтобы остановить.",
    speedSlow: "Медленно",
    speedNatural: "Нормально",
    speedFast: "Быстро",
    hangUp: "Завершить",
    callSummary: "Итог звонка",
    moodTitle: "Настрой перед комнатой",
    echo: "Эхо",
    echoCheck: "Проверить эхо",
    echoPlaceholder: "Впиши, что сказала",
    moodTired: "мягко",
    moodCharged: "энергично",
    moodHard: "без давления"
  },
  pl: {
    text: "Tekst",
    call: "Połączenie",
    holdToTalk: "Kliknij mikrofon, aby mówić. Kliknij ponownie, aby zatrzymać.",
    speedSlow: "Wolno",
    speedNatural: "Naturalnie",
    speedFast: "Szybko",
    hangUp: "Zakończ",
    callSummary: "Podsumowanie",
    moodTitle: "Nastrój przed pokojem",
    echo: "Echo",
    echoCheck: "Sprawdź echo",
    echoPlaceholder: "Wpisz, co powiedziałaś"
  },
  sk: {
    text: "Text",
    call: "Hovor",
    holdToTalk: "Ťukni na mikrofón a hovor. Ťukni znova pre stop.",
    speedSlow: "Pomaly",
    speedNatural: "Prirodzene",
    speedFast: "Rýchlo",
    hangUp: "Ukončiť",
    callSummary: "Zhrnutie hovoru",
    moodTitle: "Nálada pred izbou",
    echo: "Echo",
    echoCheck: "Skontrolovať echo",
    echoPlaceholder: "Napíš, čo si povedala"
  },
  cs: {
    text: "Text",
    call: "Hovor",
    holdToTalk: "Klepni na mikrofon a mluv. Klepni znovu pro stop.",
    speedSlow: "Pomalu",
    speedNatural: "Přirozeně",
    speedFast: "Rychle",
    hangUp: "Ukončit",
    callSummary: "Shrnutí hovoru",
    moodTitle: "Nálada před pokojem",
    echo: "Echo",
    echoCheck: "Zkontrolovat echo",
    echoPlaceholder: "Napiš, co jsi řekla"
  },
  fr: {
    text: "Texte",
    call: "Appel",
    holdToTalk: "Appuie sur le micro pour parler. Appuie encore pour arrêter.",
    speedSlow: "Lent",
    speedNatural: "Naturel",
    speedFast: "Rapide",
    hangUp: "Raccrocher",
    callSummary: "Résumé d'appel",
    moodTitle: "Humeur avant la room",
    echo: "Écho",
    echoCheck: "Vérifier l'écho",
    echoPlaceholder: "Écris ce que tu as dit"
  },
  es: {
    text: "Texto",
    call: "Llamada",
    holdToTalk: "Toca el micro para hablar. Toca otra vez para parar.",
    speedSlow: "Lento",
    speedNatural: "Natural",
    speedFast: "Rápido",
    hangUp: "Colgar",
    callSummary: "Resumen",
    moodTitle: "Ánimo antes de entrar",
    echo: "Eco",
    echoCheck: "Revisar eco",
    echoPlaceholder: "Escribe lo que dijiste"
  },
  it: {
    text: "Testo",
    call: "Chiamata",
    holdToTalk: "Tocca il microfono per parlare. Tocca ancora per fermarti.",
    speedSlow: "Lento",
    speedNatural: "Naturale",
    speedFast: "Veloce",
    hangUp: "Chiudi",
    callSummary: "Riepilogo",
    moodTitle: "Umore prima della stanza",
    echo: "Eco",
    echoCheck: "Controlla eco",
    echoPlaceholder: "Scrivi cosa hai detto"
  },
  de: {
    text: "Text",
    call: "Anruf",
    holdToTalk: "Tippe aufs Mikro zum Sprechen. Tippe erneut zum Stoppen.",
    speedSlow: "Langsam",
    speedNatural: "Natürlich",
    speedFast: "Schnell",
    hangUp: "Auflegen",
    callSummary: "Anrufübersicht",
    moodTitle: "Stimmung vor dem Raum",
    echo: "Echo",
    echoCheck: "Echo prüfen",
    echoPlaceholder: "Schreib, was du gesagt hast"
  },
  pt: {
    text: "Texto",
    call: "Chamada",
    holdToTalk: "Toca no microfone para falar. Toca outra vez para parar.",
    speedSlow: "Lento",
    speedNatural: "Natural",
    speedFast: "Rápido",
    hangUp: "Desligar",
    callSummary: "Resumo",
    moodTitle: "Humor antes da sala",
    echo: "Eco",
    echoCheck: "Verificar eco",
    echoPlaceholder: "Escreve o que disseste"
  },
  tr: {
    text: "Metin",
    call: "Arama",
    holdToTalk: "Konuşmak için mikrofona dokun. Durdurmak için tekrar dokun.",
    speedSlow: "Yavaş",
    speedNatural: "Doğal",
    speedFast: "Hızlı",
    hangUp: "Bitir",
    callSummary: "Arama özeti",
    moodTitle: "Odaya girmeden ruh hali",
    echo: "Eko",
    echoCheck: "Ekoyu kontrol et",
    echoPlaceholder: "Söylediğini yaz"
  },
  ja: {
    text: "テキスト",
    call: "通話",
    holdToTalk: "マイクをタップして話す。もう一度タップで停止。",
    speedSlow: "ゆっくり",
    speedNatural: "自然",
    speedFast: "速い",
    hangUp: "終了",
    callSummary: "通話まとめ",
    moodTitle: "入室前の気分",
    echo: "エコー",
    echoCheck: "エコー確認",
    echoPlaceholder: "言った内容を書く"
  },
  ko: {
    text: "텍스트",
    call: "통화",
    holdToTalk: "마이크를 눌러 말하고, 다시 눌러 멈춰요.",
    speedSlow: "천천히",
    speedNatural: "자연스럽게",
    speedFast: "빠르게",
    hangUp: "종료",
    callSummary: "통화 요약",
    moodTitle: "방에 들어가기 전 기분",
    echo: "에코",
    echoCheck: "에코 확인",
    echoPlaceholder: "말한 내용을 적어줘"
  },
  zh: {
    text: "文字",
    call: "通话",
    holdToTalk: "点按麦克风开始说话，再点一次停止。",
    speedSlow: "慢速",
    speedNatural: "自然",
    speedFast: "快速",
    hangUp: "挂断",
    callSummary: "通话总结",
    moodTitle: "进入房间前的心情",
    echo: "回声",
    echoCheck: "检查回声",
    echoPlaceholder: "写下你说的话"
  }
};

const grammarTopics = [
  {
    id: "past-perfect",
    title: "Past Simple vs Present Perfect",
    rule: "Past Simple = є точний завершений час. Present Perfect = результат важливий зараз.",
    examples: ["I saw it yesterday.", "I have already seen it.", "She called me last night."]
  },
  {
    id: "articles",
    title: "A / An / The",
    rule: "A або an для нового предмета, the для конкретного або вже відомого.",
    examples: ["I saw a dog.", "The dog was tiny.", "She needs an umbrella."]
  },
  {
    id: "prepositions",
    title: "In / On / At",
    rule: "In для простору або місяців, on для днів і поверхонь, at для точок і точного часу.",
    examples: ["in March", "on Monday", "at 8 PM"]
  },
  {
    id: "conditionals",
    title: "If-sentences",
    rule: "If + Present Simple, will + verb для реальної майбутньої ситуації.",
    examples: ["If I have time, I will call.", "If it rains, we will stay in."]
  }
];

const contextExamplesByLanguage: Record<string, string[]> = {
  en: ["no worries, I got you", "it hits different", "I'm down for it"],
  uk: ["Привіт, я Саша.", "Я хочу каву, будь ласка.", "Можеш мені допомогти?"],
  ru: ["Привет, я Саша.", "Я хочу кофе, пожалуйста.", "Можешь мне помочь?"],
  sk: ["Ahoj, som Sasha.", "Prosím si kávu.", "Môžete mi pomôcť?"],
  pl: ["Cześć, jestem Sasha.", "Poproszę kawę.", "Możesz mi pomóc?"],
  cs: ["Ahoj, jsem Sasha.", "Prosím kávu.", "Můžete mi pomoct?"],
  fr: ["Salut, je suis Sasha.", "Je voudrais un café.", "Vous pouvez m'aider ?"],
  es: ["Hola, soy Sasha.", "Quiero un café, por favor.", "¿Puedes ayudarme?"],
  it: ["Ciao, sono Sasha.", "Vorrei un caffè.", "Puoi aiutarmi?"],
  de: ["Hallo, ich bin Sasha.", "Ich hätte gern einen Kaffee.", "Kannst du mir helfen?"],
  pt: ["Olá, eu sou Sasha.", "Queria um café, por favor.", "Pode me ajudar?"],
  ko: ["안녕하세요, 저는 Sasha예요.", "커피 주세요.", "도와줄 수 있어요?"],
  ja: ["こんにちは、Sashaです。", "コーヒーをください。", "手伝ってくれますか？"],
  zh: ["你好，我是Sasha。", "请给我一杯咖啡。", "你可以帮我吗？"],
  tr: ["Merhaba, ben Sasha.", "Bir kahve istiyorum, lütfen.", "Bana yardım eder misin?"]
};

type GrammarMicrocopy = {
  intro: string;
  loading: string;
  answerPlaceholder: string;
  check: string;
  next: string;
  correct: string;
  almost: string;
};

const grammarMicrocopy: Record<UiLocale, GrammarMicrocopy> = {
  uk: {
    intro: "Міні-урок, приклади і перевірка відповіді. Без полотна правил.",
    loading: "Граматика завантажується. Зачекай кілька секунд.",
    answerPlaceholder: "Впиши правильне речення",
    check: "Перевірити",
    next: "Далі",
    correct: "Так, воно.",
    almost: "Ще трошки."
  },
  ru: {
    intro: "Мини-урок, примеры и проверка ответа. Без полотна правил.",
    loading: "Грамматика загружается. Подожди пару секунд.",
    answerPlaceholder: "Впиши правильное предложение",
    check: "Проверить",
    next: "Дальше",
    correct: "Да, оно.",
    almost: "Еще чуть-чуть."
  },
  en: {
    intro: "Mini lesson, examples, and answer check. No wall of rules.",
    loading: "Grammar is loading. Give it a few seconds.",
    answerPlaceholder: "Type the correct sentence",
    check: "Check",
    next: "Next",
    correct: "Yes, that's it.",
    almost: "Almost there."
  },
  pl: {
    intro: "Mini-lekcja, przykłady i sprawdzenie odpowiedzi. Bez ściany zasad.",
    loading: "Gramatyka się ładuje. Daj jej kilka sekund.",
    answerPlaceholder: "Wpisz poprawne zdanie",
    check: "Sprawdź",
    next: "Dalej",
    correct: "Tak, to jest to.",
    almost: "Jeszcze trochę."
  },
  sk: {
    intro: "Mini lekcia, príklady a kontrola odpovede. Bez steny pravidiel.",
    loading: "Gramatika sa načítava. Daj jej pár sekúnd.",
    answerPlaceholder: "Napíš správnu vetu",
    check: "Skontrolovať",
    next: "Ďalej",
    correct: "Áno, presne.",
    almost: "Už skoro."
  },
  cs: {
    intro: "Mini lekce, příklady a kontrola odpovědi. Bez stěny pravidel.",
    loading: "Gramatika se načítá. Dej jí pár sekund.",
    answerPlaceholder: "Napiš správnou větu",
    check: "Zkontrolovat",
    next: "Dál",
    correct: "Ano, přesně.",
    almost: "Ještě kousek."
  },
  fr: {
    intro: "Mini-leçon, exemples et vérification. Pas de mur de règles.",
    loading: "La grammaire charge. Patiente quelques secondes.",
    answerPlaceholder: "Écris la phrase correcte",
    check: "Vérifier",
    next: "Suivant",
    correct: "Oui, c'est ça.",
    almost: "Presque."
  },
  es: {
    intro: "Mini lección, ejemplos y revisión. Nada de muro de reglas.",
    loading: "La gramática se está cargando. Dale unos segundos.",
    answerPlaceholder: "Escribe la frase correcta",
    check: "Comprobar",
    next: "Siguiente",
    correct: "Sí, eso es.",
    almost: "Casi."
  },
  it: {
    intro: "Mini-lezione, esempi e controllo risposta. Niente muro di regole.",
    loading: "La grammatica sta caricando. Attendi qualche secondo.",
    answerPlaceholder: "Scrivi la frase corretta",
    check: "Controlla",
    next: "Avanti",
    correct: "Sì, esatto.",
    almost: "Ci sei quasi."
  },
  de: {
    intro: "Mini-Lektion, Beispiele und Antwortcheck. Keine Regelwand.",
    loading: "Grammatik lädt. Gib ihr ein paar Sekunden.",
    answerPlaceholder: "Schreibe den richtigen Satz",
    check: "Prüfen",
    next: "Weiter",
    correct: "Ja, genau.",
    almost: "Fast."
  },
  pt: {
    intro: "Mini-lição, exemplos e verificação. Sem parede de regras.",
    loading: "A gramática está a carregar. Dá-lhe alguns segundos.",
    answerPlaceholder: "Escreve a frase correta",
    check: "Verificar",
    next: "Seguinte",
    correct: "Sim, é isso.",
    almost: "Quase."
  },
  tr: {
    intro: "Mini ders, örnekler ve cevap kontrolü. Kural duvarı yok.",
    loading: "Gramer yükleniyor. Birkaç saniye ver.",
    answerPlaceholder: "Doğru cümleyi yaz",
    check: "Kontrol et",
    next: "Sonraki",
    correct: "Evet, bu.",
    almost: "Neredeyse."
  },
  ja: {
    intro: "ミニレッスン、例、答えチェック。長いルール説明なし。",
    loading: "文法を読み込み中です。少し待ってください。",
    answerPlaceholder: "正しい文を入力",
    check: "確認",
    next: "次へ",
    correct: "はい、それです。",
    almost: "あと少し。"
  },
  ko: {
    intro: "미니 레슨, 예문, 답 확인. 긴 규칙 설명은 없어요.",
    loading: "문법을 불러오는 중이에요. 잠깐만 기다려 주세요.",
    answerPlaceholder: "올바른 문장을 입력하세요",
    check: "확인",
    next: "다음",
    correct: "맞아요.",
    almost: "거의 됐어요."
  },
  zh: {
    intro: "迷你课程、例句和答案检查。不堆规则。",
    loading: "语法正在加载。请稍等几秒。",
    answerPlaceholder: "输入正确句子",
    check: "检查",
    next: "下一题",
    correct: "对，就是这样。",
    almost: "快对了。"
  }
};

const enProfileCopy: ProfileChoiceCopy = {
  setup: "Learning profile",
  currentLevel: "Current level",
  targetLevel: "Goal level",
  effortLevel: "Effort",
  levels: { Starter: "Starter", A1: "A1", A2: "A2", B1: "B1", B2: "B2", C1: "C1" },
  targets: { A1: "A1", A2: "A2", B1: "B1", B2: "B2", C1: "C1", Fluent: "Fluent" },
  efforts: { Light: "Light", Steady: "Steady", Intense: "Intense" },
  vibes: { Chill: "Chill", Normal: "Normal", Hardcore: "Hardcore" },
  tones: { "Neutral teacher": "Neutral teacher", "Supportive coach": "Supportive coach", "Precise examiner": "Precise examiner" },
};

const profileCopy: Record<UiLocale, ProfileChoiceCopy> = {
  en: enProfileCopy,
  uk: {
    setup: "Профіль навчання",
    currentLevel: "Поточний рівень",
    targetLevel: "Цільовий рівень",
    effortLevel: "Зусилля",
    levels: { Starter: "З нуля", A1: "A1", A2: "A2", B1: "B1", B2: "B2", C1: "C1" },
    targets: { A1: "A1 база", A2: "A2 впевнено", B1: "B1 розмовний", B2: "B2 сильний", C1: "C1 вільний", Fluent: "Вільно" },
    efforts: { Light: "Легко", Steady: "Стабільно", Intense: "Інтенсивно" },
    vibes: { Chill: "Спокійно", Normal: "Нормально", Hardcore: "Потужно" },
    tones: { "Neutral teacher": "Нейтральний вчитель", "Supportive coach": "Підтримуючий коуч", "Precise examiner": "Точний екзаменатор" },
  },
  ru: {
    setup: "Профиль обучения",
    currentLevel: "Текущий уровень",
    targetLevel: "Целевой уровень",
    effortLevel: "Усилия",
    levels: { Starter: "С нуля", A1: "A1", A2: "A2", B1: "B1", B2: "B2", C1: "C1" },
    targets: { A1: "A1 база", A2: "A2 уверенно", B1: "B1 разговорный", B2: "B2 сильный", C1: "C1 свободный", Fluent: "Свободно" },
    efforts: { Light: "Легко", Steady: "Стабильно", Intense: "Интенсивно" },
    vibes: { Chill: "Спокойно", Normal: "Нормально", Hardcore: "Мощно" },
    tones: { "Neutral teacher": "Нейтральный учитель", "Supportive coach": "Поддерживающий коуч", "Precise examiner": "Точный экзаменатор" },
  },
  pl: { ...enProfileCopy, setup: "Profil nauki", currentLevel: "Obecny poziom", targetLevel: "Cel", effortLevel: "Wysiłek", efforts: { Light: "Lekko", Steady: "Regularnie", Intense: "Intensywnie" }, vibes: { Chill: "Spokojnie", Normal: "Normalnie", Hardcore: "Mocno" }, tones: { "Neutral teacher": "Neutralny nauczyciel", "Supportive coach": "Wspierający coach", "Precise examiner": "Precyzyjny egzaminator" } },
  sk: { ...enProfileCopy, setup: "Profil učenia", currentLevel: "Aktuálna úroveň", targetLevel: "Cieľ", effortLevel: "Úsilie", efforts: { Light: "Ľahko", Steady: "Pravidelne", Intense: "Intenzívne" }, vibes: { Chill: "Pokojne", Normal: "Normálne", Hardcore: "Naplno" }, tones: { "Neutral teacher": "Neutrálny učiteľ", "Supportive coach": "Podporný kouč", "Precise examiner": "Presný skúšajúci" } },
  cs: { ...enProfileCopy, setup: "Profil učení", currentLevel: "Aktuální úroveň", targetLevel: "Cíl", effortLevel: "Úsilí", efforts: { Light: "Lehce", Steady: "Pravidelně", Intense: "Intenzivně" }, vibes: { Chill: "V klidu", Normal: "Normálně", Hardcore: "Naplno" }, tones: { "Neutral teacher": "Neutrální učitel", "Supportive coach": "Podporující kouč", "Precise examiner": "Přesný zkoušející" } },
  fr: { ...enProfileCopy, setup: "Profil d'apprentissage", currentLevel: "Niveau actuel", targetLevel: "Objectif", effortLevel: "Effort", efforts: { Light: "Léger", Steady: "Régulier", Intense: "Intense" }, vibes: { Chill: "Calme", Normal: "Normal", Hardcore: "Intensif" }, tones: { "Neutral teacher": "Prof neutre", "Supportive coach": "Coach encourageant", "Precise examiner": "Examinateur précis" } },
  es: { ...enProfileCopy, setup: "Perfil de aprendizaje", currentLevel: "Nivel actual", targetLevel: "Meta", effortLevel: "Esfuerzo", efforts: { Light: "Ligero", Steady: "Constante", Intense: "Intenso" }, vibes: { Chill: "Tranquilo", Normal: "Normal", Hardcore: "Intenso" }, tones: { "Neutral teacher": "Profesor neutral", "Supportive coach": "Coach de apoyo", "Precise examiner": "Examinador preciso" } },
  it: { ...enProfileCopy, setup: "Profilo di studio", currentLevel: "Livello attuale", targetLevel: "Obiettivo", effortLevel: "Impegno", efforts: { Light: "Leggero", Steady: "Costante", Intense: "Intenso" }, vibes: { Chill: "Calmo", Normal: "Normale", Hardcore: "Intenso" }, tones: { "Neutral teacher": "Insegnante neutro", "Supportive coach": "Coach di supporto", "Precise examiner": "Esaminatore preciso" } },
  de: { ...enProfileCopy, setup: "Lernprofil", currentLevel: "Aktuelles Niveau", targetLevel: "Ziel", effortLevel: "Einsatz", efforts: { Light: "Leicht", Steady: "Regelmäßig", Intense: "Intensiv" }, vibes: { Chill: "Ruhig", Normal: "Normal", Hardcore: "Intensiv" }, tones: { "Neutral teacher": "Neutraler Lehrer", "Supportive coach": "Unterstützender Coach", "Precise examiner": "Präziser Prüfer" } },
  pt: { ...enProfileCopy, setup: "Perfil de estudo", currentLevel: "Nível atual", targetLevel: "Meta", effortLevel: "Esforço", efforts: { Light: "Leve", Steady: "Constante", Intense: "Intenso" }, vibes: { Chill: "Calmo", Normal: "Normal", Hardcore: "Intenso" }, tones: { "Neutral teacher": "Professor neutro", "Supportive coach": "Coach de apoio", "Precise examiner": "Examinador preciso" } },
  tr: { ...enProfileCopy, setup: "Öğrenme profili", currentLevel: "Mevcut seviye", targetLevel: "Hedef", effortLevel: "Çaba", efforts: { Light: "Hafif", Steady: "Düzenli", Intense: "Yoğun" }, vibes: { Chill: "Sakin", Normal: "Normal", Hardcore: "Yoğun" }, tones: { "Neutral teacher": "Nötr öğretmen", "Supportive coach": "Destekleyici koç", "Precise examiner": "Net sınavcı" } },
  ja: { ...enProfileCopy, setup: "学習プロフィール", currentLevel: "現在のレベル", targetLevel: "目標レベル", effortLevel: "努力量", efforts: { Light: "軽め", Steady: "安定", Intense: "集中" }, vibes: { Chill: "ゆるく", Normal: "普通", Hardcore: "集中" }, tones: { "Neutral teacher": "中立の先生", "Supportive coach": "応援コーチ", "Precise examiner": "正確な試験官" } },
  ko: { ...enProfileCopy, setup: "학습 프로필", currentLevel: "현재 레벨", targetLevel: "목표 레벨", effortLevel: "노력량", efforts: { Light: "가볍게", Steady: "꾸준히", Intense: "집중" }, vibes: { Chill: "편하게", Normal: "보통", Hardcore: "집중" }, tones: { "Neutral teacher": "중립 선생님", "Supportive coach": "응원 코치", "Precise examiner": "정확한 시험관" } },
  zh: { ...enProfileCopy, setup: "学习档案", currentLevel: "当前水平", targetLevel: "目标水平", effortLevel: "投入程度", efforts: { Light: "轻松", Steady: "稳定", Intense: "高强度" }, vibes: { Chill: "轻松", Normal: "正常", Hardcore: "高强度" }, tones: { "Neutral teacher": "中立老师", "Supportive coach": "支持型教练", "Precise examiner": "精准考官" } },
};

const storageFlowCopy: Record<UiLocale, { translation: string; examples: string; empty: string }> = {
  en: { translation: "translation", examples: "examples", empty: "Add a word above. PajamaTalk will show translation, examples, and SRS." },
  uk: { translation: "переклад", examples: "приклади", empty: "Додай слово вище. PajamaTalk покаже переклад, приклади й повторення." },
  ru: { translation: "перевод", examples: "примеры", empty: "Добавь слово выше. PajamaTalk покажет перевод, примеры и повторение." },
  pl: { translation: "tłumaczenie", examples: "przykłady", empty: "Dodaj słowo wyżej. PajamaTalk pokaże tłumaczenie, przykłady i SRS." },
  sk: { translation: "preklad", examples: "príklady", empty: "Pridaj slovo vyššie. PajamaTalk ukáže preklad, príklady a SRS." },
  cs: { translation: "překlad", examples: "příklady", empty: "Přidej slovo nahoře. PajamaTalk ukáže překlad, příklady a SRS." },
  fr: { translation: "traduction", examples: "exemples", empty: "Ajoute un mot plus haut. PajamaTalk montrera traduction, exemples et SRS." },
  es: { translation: "traducción", examples: "ejemplos", empty: "Añade una palabra arriba. PajamaTalk mostrará traducción, ejemplos y SRS." },
  it: { translation: "traduzione", examples: "esempi", empty: "Aggiungi una parola sopra. PajamaTalk mostrerà traduzione, esempi e SRS." },
  de: { translation: "Übersetzung", examples: "Beispiele", empty: "Füge oben ein Wort hinzu. PajamaTalk zeigt Übersetzung, Beispiele und SRS." },
  pt: { translation: "tradução", examples: "exemplos", empty: "Adiciona uma palavra acima. PajamaTalk mostra tradução, exemplos e SRS." },
  tr: { translation: "çeviri", examples: "örnekler", empty: "Yukarıya bir kelime ekle. PajamaTalk çeviri, örnekler ve SRS gösterir." },
  ja: { translation: "翻訳", examples: "例文", empty: "上に単語を追加すると、翻訳・例文・SRS が表示されます。" },
  ko: { translation: "번역", examples: "예문", empty: "위에 단어를 추가하면 번역, 예문, SRS가 표시됩니다." },
  zh: { translation: "翻译", examples: "例句", empty: "在上方添加单词后，PajamaTalk 会显示翻译、例句和 SRS。" },
};

function readDailyDone(key: string): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(key) ?? "{}") as Record<string, boolean>;
  } catch {
    return {};
  }
}

export function App() {
  return (
    <ChatProvider>
      <PajamaTalkApp />
    </ChatProvider>
  );
}

function PajamaTalkApp() {
  const [uiLocale, setUiLocale] = useState<UiLocale>(() => (localStorage.getItem("pajama-ui") as UiLocale) || "uk");
  const copy = (key: Parameters<typeof t>[1]) => t(uiLocale, key);
  const { activeRoom, activeMood, chat, hints } = useChatState();
  const chatDispatch = useChatDispatch();
  const [activeTab, setActiveTab] = useState<TabKey>("aura");
  const [contextText, setContextText] = useState("");
  const [contextResult, setContextResult] = useState<ContextAnalyzeDto | null>(null);
  const [storageMode, setStorageMode] = useState<"words" | "review">("words");
  const { state: learningState, actions: learningActions } = useLearningDataController({
    clearContext: () => setContextResult(null),
    clearHints: () => chatDispatch({ type: "setHints", hints: null }),
    resetChat: () => chatDispatch({ type: "resetSession" }),
    setUiLocale
  });
  const { token, user, stats, words, dueWords, rooms, grammarDrops, grammarTopics, learningPath, learningCode, error, busy } = learningState;
  const { addWord, demo, login, updateLearning, updateNative, updateProfileSettings, updateTone, updateVibe } = learningActions;
  const { isStreaming, loadCallSummary, loadHints, queuedTurnsCount, replayQueuedTurns, sendAudioMessage, sendMessage } = useSpeakingController({
    activeMood,
    activeRoom,
    chat,
    chatDispatch,
    learningCode,
    refreshGrammar: learningActions.refreshGrammar,
    setError: learningActions.setError,
    token
  });

  const selectedLanguage = learningLanguages.find((language) => language.code === learningCode) ?? learningLanguages[0];
  const activeDrop = grammarDrops[0];
  const dueWord = dueWords[0];

  useEffect(() => {
    localStorage.setItem("pajama-ui", uiLocale);
  }, [uiLocale]);

  async function analyzeContext() {
    const result = await learningActions.analyzeContext(contextText);
    if (result) setContextResult(result);
  }

  async function reviewWord(grade: "remember" | "forgot", wordId = dueWord?.id) {
    await learningActions.reviewWord(grade, wordId);
  }

  async function deleteWord(wordId: number) {
    await learningActions.deleteWord(wordId);
  }

  async function checkGrammar(topicId: string, exerciseId: string, answer: string): Promise<GrammarCheckDto> {
    return learningActions.checkGrammar(topicId, exerciseId, answer);
  }

  function logout() {
    learningActions.logout();
  }

  if (!user) {
    return (
      <AuthScreen
        busy={busy}
        error={error}
        locale={uiLocale}
        setLocale={setUiLocale}
        copy={copy}
        onLogin={login}
        onDemo={demo}
      />
    );
  }

  return (
    <div className="app-shell">
      <main className="screen">
        <header className="topbar">
          <div className="topbar-title">
            <h1>{copy(activeTab)}</h1>
            <p>
              PajamaTalk · <LanguageBadge option={selectedLanguage} />
            </p>
          </div>
          <div className="topbar-actions">
            {activeTab === "aura" && (
              <HeaderLanguageChip
                copy={copy}
                learningCode={learningCode}
                nativeCode={user.native_language_code}
                setLearningCode={(code) => void updateLearning(code)}
                setNativeCode={(code) => void updateNative(code)}
              />
            )}
          </div>
        </header>

        {error && <div className="notice">{error}</div>}

        {activeTab === "aura" && (
          <HomeScreen
            copy={copy}
            locale={uiLocale}
            activeDrop={activeDrop}
            grammarTopics={grammarTopics}
            learningPath={learningPath}
            dueWord={dueWord}
            learningCode={learningCode}
            contextText={contextText}
            setContextText={setContextText}
            contextResult={contextResult}
            busy={busy}
            analyzeContext={analyzeContext}
            addWord={addWord}
            checkGrammar={checkGrammar}
            clearContext={() => setContextResult(null)}
            openSpeak={() => setActiveTab("speak")}
            openReview={() => {
              setStorageMode("review");
              setActiveTab("storage");
            }}
          />
        )}

        {activeTab === "speak" && (
          <SpeakingScreen
            copy={copy}
            rooms={rooms}
            activeRoom={activeRoom}
            chat={chat}
            hints={hints}
            learningCode={learningCode}
            setActiveRoom={(room, mood) => {
              chatDispatch({ type: "enterRoom", room, mood, intro: moodIntro(room, mood, uiLocale) });
            }}
            back={() => {
              chatDispatch({ type: "leaveRoom" });
            }}
            loadHints={loadHints}
            queuedTurnsCount={queuedTurnsCount}
            replayQueuedTurns={replayQueuedTurns}
            sendAudioMessage={sendAudioMessage}
            sendMessage={sendMessage}
            isStreaming={isStreaming}
            loadCallSummary={loadCallSummary}
            addWord={addWord}
            labels={speakingModeCopy[uiLocale]}
          />
        )}

        {activeTab === "storage" && (
          <StorageScreen
            copy={copy}
            locale={uiLocale}
            words={words}
            dueWord={dueWord}
            busy={busy}
            sample={selectedLanguage.sample}
            initialMode={storageMode}
            addWord={addWord}
            reviewWord={(grade, word) => void reviewWord(grade, word?.id)}
            deleteWord={(word) => deleteWord(word.id)}
          />
        )}

        {activeTab === "vibe" && (
          <ProfileScreen
            copy={copy}
            locale={uiLocale}
            user={user}
            stats={stats}
            learningCode={learningCode}
            setLearningCode={(code) => void updateLearning(code)}
            setNativeCode={(code) => void updateNative(code)}
            setVibe={(vibe) => void updateVibe(vibe)}
            setTone={(tone) => void updateTone(tone)}
            setProfile={(payload) => void updateProfileSettings(payload)}
            logout={logout}
          />
        )}
      </main>

      <nav className="bottom-nav">
        {[
          ["aura", Home, copy("aura")],
          ["speak", Mic, copy("speak")],
          ["storage", BookOpen, copy("storage")],
          ["vibe", User, copy("vibe")]
        ].map(([key, Icon, label]) => (
          <button
            key={key as string}
            className={activeTab === key ? "active" : ""}
            data-testid={`nav-${key as string}`}
            onClick={() => {
              if (key === "storage") setStorageMode("words");
              setActiveTab(key as TabKey);
            }}
          >
            <Icon size={20} />
            <span>{label as string}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

function AuthScreen({
  busy,
  error,
  locale,
  setLocale,
  copy,
  onLogin,
  onDemo
}: {
  busy: boolean;
  error: string;
  locale: UiLocale;
  setLocale: (locale: UiLocale) => void;
  copy: (key: Parameters<typeof t>[1]) => string;
  onLogin: (email: string, password: string, displayName?: string) => void;
  onDemo: () => void;
}) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  return (
    <main className="auth-screen">
      <section className="auth-panel">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Mic size={26} />
          </div>
          <div>
            <h1>PajamaTalk</h1>
            <p>{copy("tagline")}</p>
          </div>
        </div>

        <DropdownSelect
          title={copy("nativeLanguage")}
          value={locale}
          options={uiLocales}
          onChange={(value) => setLocale(value as UiLocale)}
        />

        <div className="card auth-card">
          <h2>{isRegister ? copy("register") : copy("login")}</h2>
          {isRegister && (
            <input value={name} onChange={(event) => setName(event.target.value)} placeholder={copy("name")} autoComplete="name" />
          )}
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder={copy("email")} autoComplete="email" />
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder={copy("password")}
            type="password"
            autoComplete={isRegister ? "new-password" : "current-password"}
          />
          <button
            className="primary-action"
            disabled={busy || email.length < 5 || password.length < 8}
            onClick={() => onLogin(email, password, isRegister ? name || "Dreamer" : undefined)}
          >
            <Sparkles size={18} />
            {busy ? "..." : isRegister ? copy("create") : copy("login")}
          </button>
          <button className="ghost-action" onClick={() => setIsRegister((value) => !value)}>
            {isRegister ? copy("login") : copy("register")}
          </button>
        </div>

        <button className="demo-action" disabled={busy} onClick={onDemo} data-testid="demo-login">
          <WandSparkles size={18} />
          {copy("demo")}
        </button>
        {error && <div className="notice">{error}</div>}
      </section>
    </main>
  );
}

function HomeScreen({
  copy,
  locale,
  activeDrop,
  grammarTopics,
  learningPath,
  dueWord,
  learningCode,
  contextText,
  setContextText,
  contextResult,
  busy,
  analyzeContext,
  addWord,
  checkGrammar,
  clearContext,
  openSpeak,
  openReview
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  locale: UiLocale;
  activeDrop?: GrammarDropDto;
  grammarTopics: GrammarTopicDto[];
  learningPath: LearningPathDto | null;
  dueWord?: WordDto;
  learningCode: string;
  contextText: string;
  setContextText: (value: string) => void;
  contextResult: ContextAnalyzeDto | null;
  busy: boolean;
  analyzeContext: () => void;
  addWord: (word: string, source?: string) => Promise<WordDto | undefined>;
  checkGrammar: (topicId: string, exerciseId: string, answer: string) => Promise<GrammarCheckDto>;
  clearContext: () => void;
  openSpeak: () => void;
  openReview: () => void;
}) {
  const contextExamples = contextExamplesByLanguage[learningCode] ?? contextExamplesByLanguage.en;
  const [contextSavedNote, setContextSavedNote] = useState("");
  const dailyKey = `pajama-daily-${new Date().toISOString().slice(0, 10)}-${learningCode}`;
  const [dailyDone, setDailyDone] = useState<Record<string, boolean>>(() => readDailyDone(dailyKey));

  useEffect(() => {
    setDailyDone(readDailyDone(dailyKey));
  }, [dailyKey]);

  async function saveContextWord(word: string) {
    const created = await addWord(word, contextResult?.summary ?? copy("contextTitle"));
    if (created) {
      setContextSavedNote(`${copy("add")}: ${created.term}`);
      window.setTimeout(() => setContextSavedNote(""), 1800);
    }
  }

  async function saveContextWords(words: string[]) {
    let saved = 0;
    for (const word of words) {
      const created = await addWord(word, contextResult?.summary ?? copy("contextTitle"));
      if (created) saved += 1;
    }
    if (saved) {
      setContextSavedNote(`${copy("addWords")}: ${saved}`);
      window.setTimeout(() => setContextSavedNote(""), 2200);
    }
  }

  function toggleDailyTask(id: string) {
    setDailyDone((current) => {
      const next = { ...current, [id]: !current[id] };
      localStorage.setItem(dailyKey, JSON.stringify(next));
      return next;
    });
  }

  const firstStep = learningPath?.steps[0];
  const firstPhrase = firstStep?.examples[0]?.phrase;
  const dailyTasks = [
    {
      id: "phrase",
      title: firstPhrase ?? copy("speak"),
      body: firstStep?.micro_task ?? copy("dailyFocusSub"),
      actionLabel: copy("speak"),
      action: openSpeak,
    },
    {
      id: "context",
      title: contextExamples[0],
      body: `${copy("contextTitle")} → ${copy("addWords")}`,
      actionLabel: copy("analyze"),
      action: () => setContextText(contextExamples[0]),
    },
    {
      id: "review",
      title: dueWord ? dueWord.term : copy("reviewEmpty"),
      body: dueWord ? dueWord.translation : copy("reviewEmpty"),
      actionLabel: copy("review"),
      action: openReview,
    },
  ];

  return (
    <>
      <section className="home-summary">
        <div className="focus-card card">
          <small>{copy("today")}</small>
          <h2>{copy("dailyFocus")}</h2>
          <p>{copy("dailyFocusSub")}</p>
          <div className="daily-actions">
            <button onClick={openSpeak}>
              <Mic size={16} />
              <span>{learningPath?.steps[0]?.examples[0]?.phrase ?? copy("speak")}</span>
            </button>
            <button onClick={openReview}>
              <BookOpen size={16} />
              <span>{dueWord ? dueWord.term : copy("reviewEmpty")}</span>
            </button>
          </div>
          <div className="action-row">
            <button className="primary-action" onClick={openSpeak}>
              <Mic size={18} />
              {copy("speak")}
            </button>
            <button className="soft-action" onClick={openReview}>
              <BookOpen size={18} />
              {copy("review")}
            </button>
          </div>
        </div>
      </section>

      <section className="card daily-plan-card">
        <div className="section-title">
          <Check size={20} />
          <h2>{copy("today")}</h2>
        </div>
        <div className="daily-task-list">
          {dailyTasks.map((task) => (
            <article key={task.id} className={dailyDone[task.id] ? "daily-task done" : "daily-task"}>
              <button className="task-check" onClick={() => toggleDailyTask(task.id)} aria-label={dailyDone[task.id] ? "Mark not done" : "Mark done"}>
                {dailyDone[task.id] && <Check size={15} />}
              </button>
              <button className="task-main" onClick={task.action}>
                <strong>{task.title}</strong>
                <span>{task.body}</span>
              </button>
              <button className="task-action" onClick={task.action}>
                {task.actionLabel}
              </button>
            </article>
          ))}
        </div>
      </section>

      {learningPath && <LearningPathPanel copy={copy} path={learningPath} openSpeak={openSpeak} addWord={addWord} />}

      <section className="card context-card">
        <div className="section-title">
          <WandSparkles size={20} />
          <h2>{copy("contextTitle")}</h2>
        </div>
        <textarea value={contextText} onChange={(event) => setContextText(event.target.value)} placeholder={copy("contextPlaceholder")} data-testid="context-input" />
        <div className="chip-row">
          {contextExamples.map((example) => (
            <button key={example} className="chip" onClick={() => setContextText(example)}>
              {example}
            </button>
          ))}
        </div>
        <button className="primary-action" disabled={busy || contextText.trim().length < 3} onClick={analyzeContext} data-testid="context-analyze">
          <Sparkles size={18} />
          {copy("analyze")}
        </button>
        {contextResult && (
          <div className="context-result">
            <strong>{contextResult.summary}</strong>
            <p>{contextResult.hidden_meaning}</p>
            <div className="chip-row">
              {contextResult.suggested_words.slice(0, 8).map((word) => (
                <button key={word} className="chip" disabled={busy} onClick={() => void saveContextWord(word)}>
                  <Plus size={14} />
                  {word}
                </button>
              ))}
            </div>
            <div className="action-row">
              <button className="soft-action" disabled={busy} onClick={() => void saveContextWords(contextResult.suggested_words.slice(0, 5))} data-testid="context-add-words">
                {copy("addWords")}
              </button>
              <button className="soft-action pale" onClick={clearContext}>
                <X size={16} />
              </button>
            </div>
            {contextSavedNote && <div className="inline-note">{contextSavedNote}</div>}
          </div>
        )}
      </section>

      <GrammarLab copy={copy} locale={locale} drop={activeDrop} topics={grammarTopics} checkGrammar={checkGrammar} />
    </>
  );
}

function LearningPathPanel({
  copy,
  path,
  openSpeak,
  addWord
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  path: LearningPathDto;
  openSpeak: () => void;
  addWord: (word: string, source?: string) => Promise<WordDto | undefined>;
}) {
  const [activeStep, setActiveStep] = useState(path.steps[0]?.id ?? "");
  const [savedPhrase, setSavedPhrase] = useState("");
  const step = path.steps.find((item) => item.id === activeStep) ?? path.steps[0];

  useEffect(() => {
    setActiveStep(path.steps[0]?.id ?? "");
    setSavedPhrase("");
  }, [path.language_code, path.steps]);

  if (!step) return null;

  async function savePhrase(phrase: string) {
    const created = await addWord(phrase, step.title);
    if (created) {
      setSavedPhrase(`${copy("add")}: ${created.term}`);
      window.setTimeout(() => setSavedPhrase(""), 1800);
    }
  }

  return (
    <section className="card learning-path-card">
      <div className="section-title learning-head">
        <div>
          <small>{path.level}</small>
          <h2>{path.language_name}</h2>
          <p>{path.assistant_role}</p>
        </div>
        <button className="soft-action" onClick={openSpeak}>
          <Mic size={17} />
          {copy("speak")}
        </button>
      </div>
      <div className="path-steps">
        {path.steps.map((item, index) => (
          <button key={item.id} className={item.id === step.id ? "selected" : ""} onClick={() => setActiveStep(item.id)}>
            {index + 1}
          </button>
        ))}
      </div>
      <article className="learning-step">
        <strong>{step.title}</strong>
        <p>{step.goal}</p>
        <p>{step.teacher_note}</p>
        <div className="phrase-stack">
          {step.examples.map((example) => (
            <div key={example.phrase} className="phrase-card">
              <strong>{example.phrase}</strong>
              <span>{example.pronunciation}</span>
              <p>{example.meaning}</p>
              <button className="phrase-add" onClick={() => void savePhrase(example.phrase)}>
                <Plus size={14} />
                {copy("add")}
              </button>
            </div>
          ))}
        </div>
        {savedPhrase && <div className="inline-note">{savedPhrase}</div>}
        <div className="micro-task">
          <Sparkles size={16} />
          <span>{step.micro_task}</span>
        </div>
      </article>
    </section>
  );
}

function SpeakingScreen({
  copy,
  rooms,
  activeRoom,
  chat,
  hints,
  learningCode,
  setActiveRoom,
  back,
  loadHints,
  queuedTurnsCount,
  replayQueuedTurns,
  sendAudioMessage,
  sendMessage,
  isStreaming,
  loadCallSummary,
  addWord,
  labels
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  rooms: SpeakingRoomDto[];
  activeRoom: SpeakingRoomDto | null;
  chat: ChatLine[];
  hints: SpeakingHintsDto | null;
  learningCode: string;
  setActiveRoom: (room: SpeakingRoomDto, mood: MoodKey) => void;
  back: () => void;
  loadHints: () => void;
  queuedTurnsCount: number;
  replayQueuedTurns: () => Promise<void>;
  sendAudioMessage: (chunks: VoiceAudioChunk[], transcriptHint?: string, speechRate?: number) => Promise<boolean>;
  sendMessage: (message: string, speechRate?: number, transport?: SpeakingTransport) => Promise<boolean>;
  isStreaming: boolean;
  loadCallSummary: (roomId: string) => Promise<CallSummaryDto>;
  addWord: (word: string, source?: string) => Promise<WordDto | undefined>;
  labels: SpeakingModeCopy;
}) {
  const [draft, setDraft] = useState("");
  const [callDraft, setCallDraft] = useState("");
  const [pendingRoom, setPendingRoom] = useState<SpeakingRoomDto | null>(null);
  const [transcript, setTranscript] = useState("");
  const [speechError, setSpeechError] = useState("");
  const [mode, setMode] = useState<SpeakingMode>("text");
  const [voiceSpeed, setVoiceSpeed] = useState<VoiceSpeed>("natural");
  const [callSummary, setCallSummary] = useState<CallSummaryDto | null>(null);
  const speechRate = voiceSpeedRate[voiceSpeed];
  const {
    error: recorderError,
    isRecording: isListening,
    isSupported: isVoiceRecorderSupported,
    resetRecorder,
    startRecording,
    status: recorderStatus,
    stopRecording,
    transcript: recordingTranscript
  } = useVoiceRecorder({
    languageCode: learningCode,
    onTranscript: setTranscript
  });
  const isVoiceProcessing = recorderStatus === "processing";
  const roomIcon = useMemo(() => {
    if (!activeRoom) return null;
    if (activeRoom.id.includes("airport")) return <Plane size={28} />;
    if (activeRoom.id.includes("interview")) return <BriefcaseBusiness size={28} />;
    if (activeRoom.id.includes("market")) return <ShoppingBag size={28} />;
    if (activeRoom.id.includes("doctor")) return <Stethoscope size={28} />;
    if (activeRoom.id.includes("date")) return <Heart size={28} />;
    if (activeRoom.id.includes("street")) return <MapPin size={28} />;
    if (activeRoom.id.includes("campus")) return <GraduationCap size={28} />;
    return <Coffee size={28} />;
  }, [activeRoom]);

  useEffect(() => {
    return () => {
      resetRecorder();
    };
  }, []);

  useEffect(() => {
    setMode("text");
    setCallSummary(null);
    setTranscript("");
    setCallDraft("");
    setSpeechError("");
    setPendingRoom(null);
    resetRecorder();
  }, [activeRoom?.id]);

  useEffect(() => {
    if (recorderError) setSpeechError(voiceRecorderErrorCopy(recorderError, copy));
  }, [recorderError]);

  async function startVoice() {
    if (isStreaming || isVoiceProcessing) return;
    if (isListening) {
      await stopVoice();
      return;
    }
    if (!isVoiceRecorderSupported) {
      setSpeechError(copy("speechUnsupported"));
      return;
    }
    setSpeechError("");
    setTranscript("");
    await startRecording();
  }

  async function stopVoice() {
    const recording = await stopRecording();
    if (!recording?.chunks.length) return;
    const voiceText = recording.transcript || transcript || recordingTranscript;
    setTranscript(voiceText);
    await sendAudioMessage(recording.chunks, voiceText, mode === "call" ? speechRate : 1);
  }

  async function finishCall() {
    resetRecorder();
    window.speechSynthesis?.cancel();
    if (!activeRoom) return;
    try {
      setCallSummary(await loadCallSummary(activeRoom.id));
    } catch {
      setCallSummary(buildLocalCallSummary(activeRoom, chat));
    }
    setMode("text");
  }

  function sendDraft() {
    const text = draft.trim();
    if (!text || isStreaming) return;
    setDraft("");
    sendMessage(text);
  }

  function sendCallDraft() {
    const text = callDraft.trim();
    if (!text || isStreaming) return;
    setTranscript(text);
    setCallDraft("");
    sendMessage(text, speechRate, "voice");
  }

  if (!activeRoom) {
    if (pendingRoom) {
      return (
        <section className="card mood-card">
          <button className="ghost-action inline" onClick={() => setPendingRoom(null)}>
            {copy("rooms")}
          </button>
          <div>
            <small>{pendingRoom.character}</small>
            <h2>{labels.moodTitle}</h2>
            <p>{pendingRoom.prompt}</p>
          </div>
          <div className="mood-options">
            {[
              ["tired", "🥱", labels.moodTired ?? "soft mode"],
              ["charged", "⚡", labels.moodCharged ?? "more energy"],
              ["hard", "🫠", labels.moodHard ?? "no pressure"]
            ].map(([mood, emoji, label]) => (
              <button key={mood} onClick={() => setActiveRoom(pendingRoom, mood as MoodKey)} data-testid={`mood-${mood}`}>
                <span>{emoji}</span>
                <strong>{label}</strong>
              </button>
            ))}
          </div>
        </section>
      );
    }

    return (
      <section className="room-grid">
        {rooms.map((room) => (
          <button className="room-card card" key={room.id} onClick={() => setPendingRoom(room)} data-testid={`room-${room.id}`}>
            <span className="room-icon" style={{ background: room.accent_color }}>
              {room.id.includes("airport") ? (
                <Plane />
              ) : room.id.includes("interview") ? (
                <BriefcaseBusiness />
              ) : room.id.includes("market") ? (
                <ShoppingBag />
              ) : room.id.includes("doctor") ? (
                <Stethoscope />
              ) : room.id.includes("date") ? (
                <Heart />
              ) : room.id.includes("street") ? (
                <MapPin />
              ) : room.id.includes("campus") ? (
                <GraduationCap />
              ) : (
                <Coffee />
              )}
            </span>
            <span>
              <strong>{room.title}</strong>
              <small>
                {room.character} · {room.vibe}
              </small>
            </span>
          </button>
        ))}
      </section>
    );
  }

  return (
    <section className="card speaking-card messenger-card">
      <div className="room-head">
        <button className="ghost-action inline" onClick={back}>
          {copy("rooms")}
        </button>
        <span className="room-icon" style={{ background: activeRoom.accent_color }}>
          {roomIcon}
        </span>
        <div>
          <h2>{activeRoom.character}</h2>
          <p>{activeRoom.title}</p>
        </div>
      </div>

      <div className="mode-toggle">
        <button className={mode === "text" ? "active" : ""} onClick={() => setMode("text")} data-testid="speaking-mode-text">
          <MessageCircle size={16} />
          {labels.text}
        </button>
        <button className={mode === "call" ? "active" : ""} onClick={() => setMode("call")} data-testid="speaking-mode-call">
          <Headphones size={16} />
          {labels.call}
        </button>
      </div>

      {mode === "call" ? (
        <div className="call-mode">
          <div className={`call-aura ${isListening ? "listening" : ""}`}>
            <span className="room-icon" style={{ background: activeRoom.accent_color }}>
              {roomIcon}
            </span>
          </div>
          <div className="call-copy">
            <strong>{activeRoom.character}</strong>
            <span>{isStreaming || isVoiceProcessing ? "..." : isListening ? copy("listening") : transcript || recordingTranscript || labels.holdToTalk}</span>
          </div>
          {queuedTurnsCount > 0 && (
            <div className="realtime-queue">
              <span>{queuedTurnsCount} saved turn{queuedTurnsCount > 1 ? "s" : ""}</span>
              <button onClick={() => void replayQueuedTurns()} disabled={isStreaming || isVoiceProcessing}>
                Retry
              </button>
            </div>
          )}
          <div className="speed-row">
            {(["slow", "natural", "fast"] as const).map((speed) => (
              <button key={speed} className={voiceSpeed === speed ? "selected" : ""} onClick={() => setVoiceSpeed(speed)}>
                {speed === "slow" ? labels.speedSlow : speed === "fast" ? labels.speedFast : labels.speedNatural}
              </button>
            ))}
          </div>
          <div className="call-controls">
            <button
              className={`call-mic ${isListening ? "listening" : ""}`}
              onClick={() => void startVoice()}
              disabled={isStreaming || isVoiceProcessing}
              aria-label={copy("tapToSpeak")}
            >
              {isListening ? <MicOff size={30} /> : <Mic size={30} />}
            </button>
            <button className="hangup-action" onClick={() => void finishCall()}>
              <PhoneOff size={17} />
              <span>{labels.hangUp}</span>
            </button>
          </div>
          <div className="call-fallback">
            <input
              value={callDraft}
              onChange={(event) => setCallDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendCallDraft();
              }}
              placeholder={copy("voicePrimary")}
              data-testid="call-fallback-input"
            />
            <button
              className="primary-action icon-only"
              disabled={!callDraft.trim() || isStreaming}
              onClick={sendCallDraft}
              aria-label={copy("send")}
              data-testid="call-fallback-send"
            >
              <Send size={17} />
            </button>
          </div>
          {speechError && <div className="notice">{speechError}</div>}
        </div>
      ) : (
        <>
          {callSummary && (
            <div className="call-summary">
              <small>{labels.callSummary}</small>
              <strong>{callSummary.topic}</strong>
              <p>{callSummary.grammar_feedback}</p>
              <div className="summary-phrases">
                {callSummary.new_phrases.map((phrase) => (
                  <button key={phrase} onClick={() => addWord(phrase, activeRoom.title)}>
                    <Plus size={14} />
                    {phrase}
                  </button>
                ))}
              </div>
            </div>
          )}
          <div className="chat-log">
            {chat.map((line, index) => (
              <div key={`${line.role}-${index}`} className={`bubble ${line.role}`}>
                <span>{line.text || "..."}</span>
              </div>
            ))}
          </div>

          <div className="speaker-tools">
            <button className="soft-action" onClick={loadHints} disabled={isStreaming} data-testid="speaking-hints">
              <WandSparkles size={16} />
              {copy("hints")}
            </button>
            <span>{isVoiceProcessing ? "..." : isListening ? copy("listening") : transcript || recordingTranscript || copy("voicePrimary")}</span>
          </div>

          {queuedTurnsCount > 0 && (
            <div className="realtime-queue">
              <span>{queuedTurnsCount} saved turn{queuedTurnsCount > 1 ? "s" : ""}</span>
              <button onClick={() => void replayQueuedTurns()} disabled={isStreaming || isVoiceProcessing}>
                Retry
              </button>
            </div>
          )}

          {hints && (
            <div className="hint-stack">
              {[
                ["Chill", hints.simple],
                ["Grammar", hints.conversational],
                ["Question", hints.spicy]
              ].map(([label, hint]) => (
                <button key={label} className="hint" onClick={() => setDraft(hint)}>
                  <small>{label}</small>
                  <span>{hint}</span>
                </button>
              ))}
            </div>
          )}
          {speechError && <div className="notice">{speechError}</div>}

          <div className="message-composer">
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") sendDraft();
              }}
              placeholder={`Reply to ${activeRoom.character}`}
              data-testid="speaking-composer"
            />
            <button className={`voice-action ${isListening ? "listening" : ""}`} onClick={() => void startVoice()} disabled={isStreaming || isVoiceProcessing} aria-label={copy("tapToSpeak")}>
              {isListening ? <MicOff size={22} /> : <Mic size={22} />}
            </button>
            <button className="primary-action icon-only" disabled={!draft.trim() || isStreaming} onClick={sendDraft} aria-label={copy("send")} data-testid="speaking-send">
              <Send size={18} />
            </button>
          </div>
        </>
      )}
    </section>
  );
}

function StorageScreen({
  copy,
  locale,
  words,
  dueWord,
  busy,
  sample,
  initialMode,
  addWord,
  reviewWord,
  deleteWord
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  locale: UiLocale;
  words: WordDto[];
  dueWord?: WordDto;
  busy: boolean;
  sample: string;
  initialMode: "words" | "review";
  addWord: (word: string) => Promise<WordDto | undefined>;
  reviewWord: (grade: "remember" | "forgot", word?: WordDto) => void;
  deleteWord: (word: WordDto) => Promise<void>;
}) {
  const [term, setTerm] = useState("");
  const [mode, setMode] = useState<"words" | "review">("words");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "learning" | "learned">("all");
  const [lastAdded, setLastAdded] = useState<WordDto | null>(null);
  const flow = storageFlowCopy[locale] ?? storageFlowCopy.en;
  const filteredWords = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return words.filter((word) => {
      const matchesQuery =
        !needle ||
        word.term.toLowerCase().includes(needle) ||
        word.translation.toLowerCase().includes(needle) ||
        word.source_context.toLowerCase().includes(needle);
      const matchesFilter = filter === "all" || word.status === filter;
      return matchesQuery && matchesFilter;
    });
  }, [filter, query, words]);
  const learningCount = words.filter((word) => word.status === "learning").length;
  const learnedCount = words.filter((word) => word.status === "learned").length;
  const nextDue = dueWord?.due_at ? compactDate(dueWord.due_at) : copy("reviewEmpty");

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  return (
    <>
      <section className="storage-overview">
        <div className="storage-metric card">
          <strong>{words.length}</strong>
          <span>{copy("myWords")}</span>
        </div>
        <div className="storage-metric card">
          <strong>{learningCount}</strong>
          <span>SRS</span>
        </div>
        <div className="storage-metric card">
          <strong>{learnedCount}</strong>
          <span>{copy("learned")}</span>
        </div>
      </section>

      <section className="card new-word-card">
        <div>
          <h2>{copy("newWord")}</h2>
          <p>
            {sample} · {copy("add")} → {flow.translation} → {flow.examples} → SRS
          </p>
        </div>
        <div className="send-row">
          <input value={term} onChange={(event) => setTerm(event.target.value)} placeholder={sample} data-testid="word-input" />
          <button
            className="primary-action"
            disabled={busy || !term.trim()}
            data-testid="word-add"
            onClick={async () => {
              const created = await addWord(term);
              if (created) {
                setLastAdded(created);
                setMode("words");
                setFilter("all");
                setQuery("");
                setTerm("");
              }
            }}
          >
            <Plus size={18} />
            {copy("add")}
          </button>
        </div>
      </section>
      {lastAdded && (
        <section className="card word-result-card" data-testid="word-result">
          <small>{copy("add")} → {copy("myWords")}</small>
          <div>
            <h2>{lastAdded.term}</h2>
            <strong>{lastAdded.translation}</strong>
            <span>{lastAdded.transcription}</span>
          </div>
          <p>{lastAdded.example_one}</p>
          <p>{lastAdded.example_two}</p>
          <button
            className="soft-action pale"
            aria-label="Delete word"
            onClick={async () => {
              await deleteWord(lastAdded);
              setLastAdded(null);
            }}
          >
            <Trash2 size={15} />
          </button>
        </section>
      )}
      <div className="segmented">
        <button className={mode === "words" ? "active" : ""} onClick={() => setMode("words")}>
          {copy("myWords")}
        </button>
        <button className={mode === "review" ? "active" : ""} onClick={() => setMode("review")} data-testid="storage-review-tab">
          {copy("review")}
        </button>
      </div>
      {mode === "review" ? (
        <section className="srs-card card">
          {dueWord ? (
            <>
              <small>{dueWord.transcription}</small>
              <h2>{dueWord.term}</h2>
              <p>{dueWord.meme}</p>
              <p className="muted-line">
                {copy("due")}: {nextDue}
              </p>
              <div className="action-row">
                <button className="soft-action peach" onClick={() => reviewWord("forgot")} data-testid="review-forgot">
                  {copy("forgot")}
                </button>
                <button className="soft-action mint" onClick={() => reviewWord("remember")} data-testid="review-remember">
                  {copy("remember")}
                </button>
              </div>
            </>
          ) : (
            <p>{copy("reviewEmpty")}</p>
          )}
        </section>
      ) : (
        <>
          <section className="dictionary-tools card">
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={`${copy("myWords")} / ${copy("contextTitle")}`} />
            <div className="filter-pills">
              {[
                ["all", copy("myWords")],
                ["learning", "SRS"],
                ["learned", copy("learned")]
              ].map(([key, label]) => (
                <button key={key} className={filter === key ? "selected" : ""} onClick={() => setFilter(key as typeof filter)}>
                  {label}
                </button>
              ))}
            </div>
          </section>
          <section className="word-list">
            {filteredWords.length ? (
              filteredWords.map((word) => (
                <details className="word-card card" key={word.id}>
                  <summary>
                    <span>
                      <strong>{word.term}</strong>
                      <span className="translation-line">{word.translation}</span>
                      <small>{word.transcription}</small>
                    </span>
                    <span className={`status-pill ${word.status}`}>{word.status === "learned" ? copy("learned") : "SRS"}</span>
                  </summary>
                  <div className="word-meta">
                    <span>SRS {word.color_level}/5</span>
                    <span>{word.due_at ? compactDate(word.due_at) : copy("reviewEmpty")}</span>
                  </div>
                  {word.source_context && <p className="source-line">{copy("contextTitle")}: {word.source_context}</p>}
                  <p>{word.meme}</p>
                  <p>{word.example_one}</p>
                  <p>{word.example_two}</p>
                  <div className="action-row word-actions">
                    <button className="soft-action peach" onClick={() => reviewWord("forgot", word)}>
                      {copy("forgot")}
                    </button>
                    <button className="soft-action mint" onClick={() => reviewWord("remember", word)}>
                      {copy("remember")}
                    </button>
                    <button
                      className="soft-action pale icon-only"
                      onClick={async () => {
                        await deleteWord(word);
                        if (lastAdded?.id === word.id) setLastAdded(null);
                      }}
                      aria-label="Delete word"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </details>
              ))
            ) : (
              <section className="card empty-state">
                <strong>{query ? copy("reviewEmpty") : copy("newWord")}</strong>
                <p>
                  {flow.empty}
                </p>
              </section>
            )}
          </section>
        </>
      )}
    </>
  );
}

function compactDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function LanguageBadge({ option }: { option: SelectOption }) {
  return (
    <span className="language-badge">
      <FlagSticker code={option.code} />
      <span>{option.short}</span>
    </span>
  );
}

const flagCountryByLanguage: Record<string, string> = {
  en: "gb",
  uk: "ua",
  ru: "ru",
  pl: "pl",
  sk: "sk",
  cs: "cz",
  fr: "fr",
  es: "es",
  it: "it",
  de: "de",
  pt: "pt",
  tr: "tr",
  ja: "jp",
  ko: "kr",
  zh: "cn",
};

function FlagSticker({ code }: { code: string }) {
  const countryCode = flagCountryByLanguage[code] ?? "gb";
  return (
    <span className="flag-sticker" aria-hidden="true">
      <img src={`/flags/${countryCode}.png`} alt="" loading="lazy" draggable={false} />
    </span>
  );
}

function buildLocalCallSummary(room: SpeakingRoomDto, chat: ChatLine[]): CallSummaryDto {
  const assistantText = chat.filter((line) => line.role === "assistant").map((line) => line.text).join(". ");
  const phrases = assistantText
    .split(/[.!?]/)
    .map((item) => item.trim())
    .filter((item, index, list) => item.length >= 8 && item.length <= 52 && list.indexOf(item) === index)
    .slice(0, 4);
  return {
    topic: `${room.title}: ${chat.filter((line) => line.role === "user").length} voice turns.`,
    new_phrases: phrases.length ? phrases : ["Could I say that another way?", "What would you recommend next?"],
    grammar_feedback: "No repeated grammar pattern yet. Keep answers short, clear, and alive.",
    turns: chat.filter((line) => line.role === "user").length,
  };
}

function voiceRecorderErrorCopy(error: string, copy: (key: Parameters<typeof t>[1]) => string): string {
  if (error === "media-recorder-unavailable") return copy("speechUnsupported");
  return copy("speechError");
}

function moodIntro(room: SpeakingRoomDto, mood: MoodKey, locale: UiLocale): string {
  const base = {
    uk: {
      tired: `Окей, легкий режим. ${room.character} не буде валити складними питаннями: просто коротка жива розмова.`,
      charged: `Енергія є. ${room.character} дасть трохи швидший темп і більше живих фраз.`,
      hard: `Все складно, тому без тиску. ${room.character} тримає розмову м'якою і простою.`,
      steady: room.prompt,
    },
    ru: {
      tired: `Окей, легкий режим. ${room.character} не будет грузить сложными вопросами: просто короткий живой разговор.`,
      charged: `Энергия есть. ${room.character} даст чуть быстрее темп и больше живых фраз.`,
      hard: `Все сложно, поэтому без давления. ${room.character} держит разговор мягким и простым.`,
      steady: room.prompt,
    },
    en: {
      tired: `Low-energy mode. ${room.character} will keep it short, soft, and easy today.`,
      charged: `Charged mode. ${room.character} will make the pace livelier and a bit more playful.`,
      hard: `No-pressure mode. ${room.character} will keep the conversation simple and kind.`,
      steady: room.prompt,
    },
  };
  return (base[locale as "uk" | "ru" | "en"] ?? base.en)[mood];
}

function ProfileScreen({
  copy,
  locale,
  user,
  stats,
  learningCode,
  setLearningCode,
  setNativeCode,
  setVibe,
  setTone,
  setProfile,
  logout
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  locale: UiLocale;
  user: UserDto;
  stats: StatsDto | null;
  learningCode: string;
  setLearningCode: (code: string) => void;
  setNativeCode: (code: string) => void;
  setVibe: (vibe: string) => void;
  setTone: (tone: string) => void;
  setProfile: (payload: Partial<Record<string, string | number>>) => void;
  logout: () => void;
}) {
  const labels = profileCopy[locale] ?? enProfileCopy;
  return (
    <>
      <section className="profile-hero card">
        <div>
          <small>{copy("profile")}</small>
          <h2>{user.display_name}</h2>
          <p>{user.email}</p>
        </div>
        <div className="profile-score">
          <strong>{stats?.language_words ?? 0}</strong>
          <span>{copy("myWords")}</span>
        </div>
      </section>
      <section className="stats-grid">
        <Stat value={`${stats?.due_reviews ?? 0}`} label={copy("due")} />
        <Stat value={`${stats?.learned_words ?? 0}`} label={copy("learned")} />
        <Stat value={`${stats?.language_words ?? 0}`} label={copy("myWords")} />
      </section>
      <section className="profile-controls">
        <DropdownSelect title={copy("learningLanguage")} value={learningCode} options={learningLanguages} onChange={setLearningCode} testId="profile-learning-language" />
        <DropdownSelect title={copy("nativeLanguage")} value={user.native_language_code} options={nativeLanguages} onChange={setNativeCode} testId="profile-native-language" />
      </section>

      <section className="card settings-card">
        <h2>{labels.setup}</h2>
        <div className="preference-grid">
          <ChoiceGroup title={labels.currentLevel} value={user.current_level} options={currentLevelOptions} labels={labels.levels} onSelect={(value) => setProfile({ current_level: value })} testId="profile-current-level" />
          <ChoiceGroup title={labels.targetLevel} value={user.target_level} options={targetLevelOptions} labels={labels.targets} onSelect={(value) => setProfile({ target_level: value })} testId="profile-target-level" />
          <ChoiceGroup title={labels.effortLevel} value={user.effort_level} options={effortOptions} labels={labels.efforts} onSelect={(value) => setProfile({ effort_level: value })} testId="profile-effort" />
        </div>
      </section>

      <section className="card settings-card">
        <h2>{copy("learningVibe")}</h2>
        <div className="button-grid">
          {vibeOptions.map((vibe) => (
            <button key={vibe} className={user.learning_vibe === vibe ? "selected" : ""} onClick={() => setVibe(vibe)}>
              {labels.vibes[vibe]}
            </button>
          ))}
        </div>
      </section>

      <section className="card settings-card">
        <h2>{copy("aiTone")}</h2>
        <div className="tone-list">
          {toneOptions.map((tone) => (
            <button key={tone} className={user.ai_tone === tone ? "selected" : ""} onClick={() => setTone(tone)}>
              <Bot size={17} />
              {labels.tones[tone]}
            </button>
          ))}
        </div>
      </section>

      <button className="soft-action peach full-width" onClick={logout}>
        <LogOut size={16} />
        {copy("logOut")}
      </button>
    </>
  );
}

function HeaderLanguageChip({
  copy,
  learningCode,
  nativeCode,
  setLearningCode,
  setNativeCode
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  learningCode: string;
  nativeCode: string;
  setLearningCode: (code: string) => void;
  setNativeCode: (code: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const learning = learningLanguages.find((language) => language.code === learningCode) ?? learningLanguages[0];
  const native = nativeLanguages.find((language) => language.code === nativeCode) ?? nativeLanguages[0];

  return (
    <div className={`header-language ${open ? "open" : ""}`}>
      <button className="language-pill" onClick={() => setOpen((current) => !current)} aria-label="Change languages">
        <Languages size={16} />
        <span className="language-pair">
          <span className="language-pair-top">
            <strong><LanguageBadge option={learning} /></strong>
            <span>→</span>
            <strong><LanguageBadge option={native} /></strong>
          </span>
        </span>
        <ChevronDown size={15} />
      </button>
      {open && (
        <div className="header-language-menu">
          <section>
            <small>{copy("learningLanguage")}</small>
            <div className="mini-options">
              {learningLanguages.map((option) => (
                <button
                  key={option.code}
                  className={option.code === learningCode ? "selected" : ""}
                  onClick={() => {
                    setLearningCode(option.code);
                    setOpen(false);
                  }}
                >
                  <LanguageBadge option={option} />
                </button>
              ))}
            </div>
          </section>
          <section>
            <small>{copy("nativeLanguage")}</small>
            <div className="mini-options">
              {nativeLanguages.map((option) => (
                <button
                  key={option.code}
                  className={option.code === nativeCode ? "selected" : ""}
                  onClick={() => {
                    setNativeCode(option.code);
                    setOpen(false);
                  }}
                >
                  <LanguageBadge option={option} />
                </button>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function DropdownSelect({
  title,
  value,
  options,
  onChange,
  testId
}: {
  title: string;
  value: string;
  options: readonly SelectOption[];
  onChange: (value: string) => void;
  testId?: string;
}) {
  const [open, setOpen] = useState(false);
  const selected = options.find((option) => option.code === value) ?? options[0];
  return (
    <section className={`select-card card ${open ? "open" : ""}`} data-testid={testId}>
      <button className="select-trigger" onClick={() => setOpen((current) => !current)} data-testid={testId ? `${testId}-trigger` : undefined}>
        <span>
          <small>{title}</small>
          <strong>
            <LanguageBadge option={selected} />
          </strong>
        </span>
        <ChevronDown size={18} />
      </button>
      {open && (
        <div className="select-menu">
          {options.map((option) => (
            <button
              key={option.code}
              className={option.code === value ? "selected" : ""}
              data-testid={testId ? `${testId}-option-${option.code}` : undefined}
              onClick={() => {
                onChange(option.code);
                setOpen(false);
              }}
            >
              <LanguageBadge option={option} />
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

function ChoiceGroup({
  title,
  value,
  options,
  labels,
  onSelect,
  testId
}: {
  title: string;
  value: string;
  options: readonly string[];
  labels: Record<string, string>;
  onSelect: (value: string) => void;
  testId?: string;
}) {
  return (
    <div className="choice-group" data-testid={testId}>
      <small>{title}</small>
      <div className="choice-pills">
        {options.map((option) => (
          <button key={option} className={value === option ? "selected" : ""} onClick={() => onSelect(option)} data-testid={testId ? `${testId}-${option}` : undefined}>
            {labels[option] ?? option}
          </button>
        ))}
      </div>
    </div>
  );
}

function GrammarLab({
  copy,
  locale,
  drop,
  topics,
  checkGrammar
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  locale: UiLocale;
  drop?: GrammarDropDto;
  topics: GrammarTopicDto[];
  checkGrammar: (topicId: string, exerciseId: string, answer: string) => Promise<GrammarCheckDto>;
}) {
  const [activeTopicId, setActiveTopicId] = useState("");
  const [exerciseIndex, setExerciseIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<GrammarCheckDto | null>(null);
  const [score, setScore] = useState(0);
  const [checking, setChecking] = useState(false);
  const topic = topics.find((item) => item.id === activeTopicId) ?? topics[0];
  const exercise = topic?.exercises[exerciseIndex] ?? topic?.exercises[0];
  const micro = grammarMicrocopy[locale] ?? grammarMicrocopy.en;
  const adaptive = drop ?? {
    title: "Past Simple",
    nudge: "Past Simple is tapping the window for 30 seconds.",
    tiny_explanation: "Finished time, finished action.",
    quests: ["I watched it yesterday", "She called me last night"]
  };

  useEffect(() => {
    if (!activeTopicId && topics[0]) setActiveTopicId(topics[0].id);
  }, [activeTopicId, topics]);

  function selectTopic(nextTopicId: string) {
    setActiveTopicId(nextTopicId);
    setExerciseIndex(0);
    setAnswer("");
    setResult(null);
  }

  async function submitAnswer() {
    if (!topic || !exercise || !answer.trim()) return;
    setChecking(true);
    try {
      const nextResult = await checkGrammar(topic.id, exercise.id, answer);
      setResult(nextResult);
      setScore((current) => current + nextResult.score_delta);
    } finally {
      setChecking(false);
    }
  }

  function nextExercise() {
    if (!topic) return;
    setExerciseIndex((current) => (current + 1) % topic.exercises.length);
    setAnswer("");
    setResult(null);
  }

  if (!topic || !exercise) {
    return (
      <section className="card grammar-lab">
        <div className="section-title">
          <GraduationCap size={20} />
          <h2>{copy("grammar")}</h2>
        </div>
        <p>{micro.loading}</p>
      </section>
    );
  }

  return (
    <section className="card grammar-lab">
      <div className="section-title grammar-title">
        <div>
          <h2>{copy("grammar")}</h2>
          <p>{micro.intro}</p>
        </div>
        <span className="grammar-score">{score} xp</span>
      </div>

      <article className="adaptive-drop">
        <small>{copy("adaptiveDrop")}</small>
        <strong>{adaptive.title}</strong>
        <p>{topic.recommended ? topic.reason : adaptive.nudge}</p>
      </article>

      <div className="topic-tabs">
        {topics.map((item) => (
          <button key={item.id} className={item.id === topic.id ? "selected" : ""} onClick={() => selectTopic(item.id)} data-testid={`grammar-topic-${item.id}`}>
            {item.recommended && <Sparkles size={14} />}
            {item.title}
          </button>
        ))}
      </div>

      <article className="grammar-topic lesson-card">
        <div className="lesson-head">
          <span>{topic.level}</span>
          <strong>{topic.title}</strong>
        </div>
        <p>{topic.summary}</p>
        <p>{topic.micro_lesson}</p>
        <div className="rule-list">
          {topic.rules.map((rule) => (
            <span key={rule}>{rule}</span>
          ))}
        </div>
      </article>

      <div className="example-grid">
        {topic.examples.map((example) => (
          <article key={`${example.right}-${example.wrong ?? "ok"}`} className="mini-example">
            {example.wrong && <del>{example.wrong}</del>}
            <strong>{example.right}</strong>
            <p>{example.note}</p>
          </article>
        ))}
      </div>

      <article className={`exercise-card ${result ? (result.correct ? "correct" : "wrong") : ""}`}>
        <div className="lesson-head">
          <span>
            {exerciseIndex + 1}/{topic.exercises.length}
          </span>
          <strong>{exercise.prompt}</strong>
        </div>
        {exercise.options.length > 0 ? (
          <div className="option-grid">
            {exercise.options.map((option) => (
              <button
                key={option}
                className={answer === option ? "selected" : ""}
                data-testid="grammar-option"
                onClick={() => {
                  setAnswer(option);
                  setResult(null);
                }}
              >
                {option}
              </button>
            ))}
          </div>
        ) : (
          <input
            value={answer}
            onChange={(event) => {
              setAnswer(event.target.value);
              setResult(null);
            }}
            placeholder={micro.answerPlaceholder}
          />
        )}
        <div className="exercise-actions">
          <button className="primary-action" disabled={checking || !answer.trim()} onClick={submitAnswer} data-testid="grammar-check">
            <Check size={17} />
            {checking ? "..." : micro.check}
          </button>
          <button className="soft-action" onClick={nextExercise} data-testid="grammar-next">
            {micro.next}
          </button>
        </div>
        {result && (
          <div className="grammar-feedback" data-testid="grammar-feedback">
            <strong>{result.correct ? micro.correct : micro.almost}</strong>
            <p>{result.feedback}</p>
          </div>
        )}
      </article>
    </section>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="card stat-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
