import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Bot,
  BriefcaseBusiness,
  Check,
  ChevronDown,
  Coffee,
  GraduationCap,
  Home,
  Languages,
  LogOut,
  Mic,
  MicOff,
  Plane,
  Plus,
  RefreshCw,
  Send,
  Sparkles,
  User,
  WandSparkles,
  X
} from "lucide-react";
import {
  api,
  ContextAnalyzeDto,
  GrammarCheckDto,
  GrammarDropDto,
  GrammarTopicDto,
  SpeakingHintsDto,
  SpeakingRoomDto,
  StatsDto,
  UserDto,
  WordDto
} from "./api";
import { languageName, learningLanguages, nativeLanguages, t, UiLocale, uiLocales } from "./i18n";

type TabKey = "aura" | "speak" | "storage" | "vibe";
type ChatLine = { role: "user" | "assistant"; text: string };
type SelectOption = { code: string; label: string; short: string };

const demoEmail = "dreamer@pajamatalk.dev";
const demoPassword = "pajama-dev-secret";

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

const contextExamples = ["no worries, I got you", "it hits different", "I'm down for it"];

function getSpeechLang(code: string) {
  return (
    {
      en: "en-US",
      pl: "pl-PL",
      sk: "sk-SK",
      cs: "cs-CZ",
      fr: "fr-FR",
      es: "es-ES",
      it: "it-IT",
      ko: "ko-KR",
      ja: "ja-JP",
      zh: "zh-CN",
      tr: "tr-TR"
    }[code] ?? "en-US"
  );
}

export function App() {
  const [uiLocale, setUiLocale] = useState<UiLocale>(() => (localStorage.getItem("pajama-ui") as UiLocale) || "uk");
  const copy = (key: Parameters<typeof t>[1]) => t(uiLocale, key);
  const [token, setToken] = useState(() => localStorage.getItem("pajama-token") || "");
  const [user, setUser] = useState<UserDto | null>(null);
  const [stats, setStats] = useState<StatsDto | null>(null);
  const [words, setWords] = useState<WordDto[]>([]);
  const [dueWords, setDueWords] = useState<WordDto[]>([]);
  const [rooms, setRooms] = useState<SpeakingRoomDto[]>([]);
  const [grammarDrops, setGrammarDrops] = useState<GrammarDropDto[]>([]);
  const [grammarTopics, setGrammarTopics] = useState<GrammarTopicDto[]>([]);
  const [activeTab, setActiveTab] = useState<TabKey>("aura");
  const [learningCode, setLearningCode] = useState("en");
  const [contextText, setContextText] = useState("");
  const [contextResult, setContextResult] = useState<ContextAnalyzeDto | null>(null);
  const [activeRoom, setActiveRoom] = useState<SpeakingRoomDto | null>(null);
  const [chat, setChat] = useState<ChatLine[]>([]);
  const [hints, setHints] = useState<SpeakingHintsDto | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const targetLanguage = languageName(user?.native_language_code ?? "uk");
  const selectedLanguage = learningLanguages.find((language) => language.code === learningCode) ?? learningLanguages[0];
  const activeDrop = grammarDrops[0];
  const dueWord = dueWords[0];

  useEffect(() => {
    localStorage.setItem("pajama-ui", uiLocale);
  }, [uiLocale]);

  useEffect(() => {
    api.health().catch(() => setError("FastAPI offline. Запусти backend на :8000."));
    if (token) {
      void openSession(token);
    }
  }, []);

  async function openSession(nextToken: string) {
    setBusy(true);
    setError("");
    try {
      const profile = await api.me(nextToken);
      setToken(nextToken);
      localStorage.setItem("pajama-token", nextToken);
      setUser(profile);
      setLearningCode(profile.active_language_code);
      await loadData(nextToken, profile.active_language_code);
    } catch (err) {
      localStorage.removeItem("pajama-token");
      setToken("");
      setUser(null);
      setError(err instanceof Error ? err.message : "Session failed.");
    } finally {
      setBusy(false);
    }
  }

  async function loadData(nextToken = token, languageCode = learningCode) {
    if (!nextToken) return;
    const [nextStats, nextWords, nextDue, nextRooms, nextDrops, nextTopics] = await Promise.all([
      api.stats(nextToken),
      api.words(nextToken, languageCode),
      api.dueWords(nextToken, languageCode),
      api.speakingRooms(nextToken, languageCode),
      api.grammarDrops(nextToken),
      api.grammarTopics(nextToken)
    ]);
    setStats(nextStats);
    setWords(nextWords);
    setDueWords(nextDue);
    setRooms(nextRooms);
    setGrammarDrops(nextDrops);
    setGrammarTopics(nextTopics);
  }

  async function login(email: string, password: string, displayName?: string) {
    setBusy(true);
    setError("");
    try {
      const session = displayName ? await api.register(email, password, displayName) : await api.login(email, password);
      await openSession(session.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Auth failed.");
    } finally {
      setBusy(false);
    }
  }

  async function demo() {
    setBusy(true);
    setError("");
    try {
      let session;
      try {
        session = await api.register(demoEmail, demoPassword, "Dreamer");
      } catch {
        session = await api.login(demoEmail, demoPassword);
      }
      await openSession(session.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Demo login failed.");
    } finally {
      setBusy(false);
    }
  }

  async function updateLearning(code: string) {
    if (!token) return;
    setLearningCode(code);
    const profile = await api.updateProfile(token, { active_language_code: code });
    setUser(profile);
    await loadData(token, code);
  }

  async function updateNative(code: string) {
    if (!token) return;
    const profile = await api.updateProfile(token, { native_language_code: code });
    setUser(profile);
  }

  async function updateVibe(vibe: string) {
    if (!token) return;
    const minutes = vibe === "Hardcore" ? 30 : vibe === "Normal" ? 15 : 5;
    const profile = await api.updateProfile(token, { learning_vibe: vibe, daily_vibe_minutes: minutes });
    setUser(profile);
    setStats(await api.stats(token));
  }

  async function updateTone(tone: string) {
    if (!token) return;
    setUser(await api.updateProfile(token, { ai_tone: tone }));
  }

  async function addWord(term: string, source = "") {
    if (!token || !term.trim()) return;
    setBusy(true);
    try {
      const word = await api.enrichWord(token, term.trim(), learningCode, targetLanguage, source);
      setWords((current) => [word, ...current.filter((item) => item.id !== word.id)]);
      setDueWords((current) => [word, ...current.filter((item) => item.id !== word.id)]);
      setStats(await api.stats(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add word.");
    } finally {
      setBusy(false);
    }
  }

  async function analyzeContext() {
    if (!token || contextText.trim().length < 3) return;
    setBusy(true);
    setError("");
    try {
      setContextResult(await api.analyzeContext(token, contextText, learningCode, targetLanguage));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Context analysis failed.");
    } finally {
      setBusy(false);
    }
  }

  async function reviewWord(grade: "remember" | "forgot") {
    if (!token || !dueWord) return;
    await api.reviewWord(token, dueWord.id, grade);
    await loadData(token, learningCode);
  }

  async function loadHints() {
    if (!token || !activeRoom) return;
    const last = [...chat].reverse().find((line: ChatLine) => line.role === "assistant")?.text ?? activeRoom.prompt;
    setHints(await api.speakingHints(token, activeRoom.id, last, learningCode));
  }

  async function sendMessage(message: string) {
    if (!token || !activeRoom || !message.trim()) return;
    const userLine: ChatLine = { role: "user", text: message.trim() };
    setChat((current) => [...current, userLine, { role: "assistant", text: "" }]);
    setHints(null);
    let finalReply = "";
    await new Promise<void>((resolve, reject) => {
      const socket = new WebSocket(
        api.wsUrl(`/speaking/ws?token=${encodeURIComponent(token)}&room_id=${encodeURIComponent(activeRoom.id)}`)
      );
      let reply = "";
      socket.onopen = () => socket.send(message.trim());
      socket.onerror = () => reject(new Error("WebSocket failed."));
      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data) as { type: string; value?: string };
        if (payload.type === "token") {
          reply += payload.value ?? "";
          finalReply = reply.trim();
          setChat((current) => [...current.slice(0, -1), { role: "assistant", text: reply.trimStart() }]);
        }
        if (payload.type === "done") {
          socket.close();
          resolve();
        }
      };
    }).catch((err) => setError(err instanceof Error ? err.message : "Speaking stream failed."));
    if (finalReply && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(new SpeechSynthesisUtterance(finalReply));
    }
    if (token) {
      const [nextDrops, nextTopics] = await Promise.all([api.grammarDrops(token), api.grammarTopics(token)]);
      setGrammarDrops(nextDrops);
      setGrammarTopics(nextTopics);
    }
  }

  async function checkGrammar(topicId: string, exerciseId: string, answer: string): Promise<GrammarCheckDto> {
    if (!token) throw new Error("No active session.");
    return api.checkGrammar(token, topicId, exerciseId, answer);
  }

  function logout() {
    localStorage.removeItem("pajama-token");
    setToken("");
    setUser(null);
    setWords([]);
    setDueWords([]);
    setStats(null);
    setContextResult(null);
    setChat([]);
    setGrammarDrops([]);
    setGrammarTopics([]);
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
              PajamaTalk · {selectedLanguage.label} · {stats?.daily_vibe_minutes ?? 5} min
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
            <button className="icon-button" onClick={() => void loadData()} aria-label="Refresh">
              <RefreshCw size={19} />
            </button>
          </div>
        </header>

        {error && <div className="notice">{error}</div>}

        {activeTab === "aura" && (
          <HomeScreen
            copy={copy}
            activeDrop={activeDrop}
            grammarTopics={grammarTopics}
            contextText={contextText}
            setContextText={setContextText}
            contextResult={contextResult}
            busy={busy}
            analyzeContext={analyzeContext}
            addWord={addWord}
            checkGrammar={checkGrammar}
            clearContext={() => setContextResult(null)}
            openSpeak={() => setActiveTab("speak")}
            openReview={() => setActiveTab("storage")}
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
            setActiveRoom={(room) => {
              setActiveRoom(room);
              setHints(null);
              setChat([{ role: "assistant", text: `Hey, I am ${room.character}. Press mic and answer in ${selectedLanguage.label}.` }]);
            }}
            back={() => {
              setActiveRoom(null);
              setChat([]);
              setHints(null);
            }}
            loadHints={loadHints}
            sendMessage={sendMessage}
          />
        )}

        {activeTab === "storage" && (
          <StorageScreen
            copy={copy}
            words={words}
            dueWord={dueWord}
            busy={busy}
            sample={selectedLanguage.sample}
            addWord={addWord}
            reviewWord={reviewWord}
          />
        )}

        {activeTab === "vibe" && (
          <ProfileScreen
            copy={copy}
            locale={uiLocale}
            setLocale={setUiLocale}
            user={user}
            stats={stats}
            learningCode={learningCode}
            setLearningCode={(code) => void updateLearning(code)}
            setNativeCode={(code) => void updateNative(code)}
            setVibe={(vibe) => void updateVibe(vibe)}
            setTone={(tone) => void updateTone(tone)}
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
          <button key={key as string} className={activeTab === key ? "active" : ""} onClick={() => setActiveTab(key as TabKey)}>
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
          title={copy("uiLanguage")}
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

        <button className="demo-action" disabled={busy} onClick={onDemo}>
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
  activeDrop,
  grammarTopics,
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
  activeDrop?: GrammarDropDto;
  grammarTopics: GrammarTopicDto[];
  contextText: string;
  setContextText: (value: string) => void;
  contextResult: ContextAnalyzeDto | null;
  busy: boolean;
  analyzeContext: () => void;
  addWord: (word: string, source?: string) => void;
  checkGrammar: (topicId: string, exerciseId: string, answer: string) => Promise<GrammarCheckDto>;
  clearContext: () => void;
  openSpeak: () => void;
  openReview: () => void;
}) {
  return (
    <>
      <section className="home-summary">
        <div className="focus-card card">
          <small>{copy("today")}</small>
          <h2>{copy("dailyFocus")}</h2>
          <p>{copy("dailyFocusSub")}</p>
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

      <section className="card context-card">
        <div className="section-title">
          <WandSparkles size={20} />
          <h2>{copy("contextTitle")}</h2>
        </div>
        <textarea value={contextText} onChange={(event) => setContextText(event.target.value)} placeholder={copy("contextPlaceholder")} />
        <div className="chip-row">
          {contextExamples.map((example) => (
            <button key={example} className="chip" onClick={() => setContextText(example)}>
              {example}
            </button>
          ))}
        </div>
        <button className="primary-action" disabled={busy || contextText.trim().length < 3} onClick={analyzeContext}>
          <Sparkles size={18} />
          {copy("analyze")}
        </button>
        {contextResult && (
          <div className="context-result">
            <strong>{contextResult.summary}</strong>
            <p>{contextResult.hidden_meaning}</p>
            <div className="chip-row">
              {contextResult.suggested_words.slice(0, 8).map((word) => (
                <button key={word} className="chip" disabled={busy} onClick={() => addWord(word, contextResult.summary)}>
                  <Plus size={14} />
                  {word}
                </button>
              ))}
            </div>
            <div className="action-row">
              <button className="soft-action" onClick={() => contextResult.suggested_words.slice(0, 5).forEach((word) => addWord(word, contextResult.summary))}>
                {copy("addWords")}
              </button>
              <button className="soft-action pale" onClick={clearContext}>
                <X size={16} />
              </button>
            </div>
          </div>
        )}
      </section>

      <GrammarLab copy={copy} drop={activeDrop} topics={grammarTopics} checkGrammar={checkGrammar} />
    </>
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
  sendMessage
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  rooms: SpeakingRoomDto[];
  activeRoom: SpeakingRoomDto | null;
  chat: ChatLine[];
  hints: SpeakingHintsDto | null;
  learningCode: string;
  setActiveRoom: (room: SpeakingRoomDto) => void;
  back: () => void;
  loadHints: () => void;
  sendMessage: (message: string) => void;
}) {
  const [draft, setDraft] = useState("");
  const [transcript, setTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [speechError, setSpeechError] = useState("");
  const roomIcon = useMemo(() => {
    if (!activeRoom) return null;
    if (activeRoom.id.includes("airport")) return <Plane size={28} />;
    if (activeRoom.id.includes("interview")) return <BriefcaseBusiness size={28} />;
    return <Coffee size={28} />;
  }, [activeRoom]);

  function startVoice() {
    const SpeechCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechCtor) {
      setSpeechError(copy("speechUnsupported"));
      return;
    }
    const recognition = new SpeechCtor();
    recognition.lang = getSpeechLang(learningCode);
    recognition.interimResults = true;
    recognition.continuous = false;
    setSpeechError("");
    setTranscript("");
    setIsListening(true);
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const text = Array.from(event.results)
        .map((result) => result[0]?.transcript ?? "")
        .join(" ")
        .trim();
      setTranscript(text);
    };
    recognition.onerror = () => {
      setSpeechError(copy("speechError"));
      setIsListening(false);
    };
    recognition.onend = () => {
      setIsListening(false);
      setTranscript((current) => {
        if (current.trim()) void sendMessage(current);
        return current;
      });
    };
    recognition.start();
  }

  function sendDraft() {
    const text = draft.trim();
    if (!text) return;
    setDraft("");
    sendMessage(text);
  }

  if (!activeRoom) {
    return (
      <section className="room-grid">
        {rooms.map((room) => (
          <button className="room-card card" key={room.id} onClick={() => setActiveRoom(room)}>
            <span className="room-icon" style={{ background: room.accent_color }}>
              {room.id.includes("airport") ? <Plane /> : room.id.includes("interview") ? <BriefcaseBusiness /> : <Coffee />}
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

      <div className="chat-log">
        {chat.map((line, index) => (
          <div key={`${line.role}-${index}`} className={`bubble ${line.role}`}>
            {line.text || "..."}
          </div>
        ))}
      </div>

      <div className="speaker-tools">
        <button className="soft-action" onClick={loadHints}>
          <WandSparkles size={16} />
          {copy("hints")}
        </button>
        <span>{isListening ? copy("listening") : transcript || copy("voicePrimary")}</span>
      </div>

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
        />
        <button className={`voice-action ${isListening ? "listening" : ""}`} onClick={startVoice} aria-label={copy("tapToSpeak")}>
          {isListening ? <MicOff size={22} /> : <Mic size={22} />}
        </button>
        <button className="primary-action icon-only" disabled={!draft.trim()} onClick={sendDraft} aria-label="Send">
          <Send size={18} />
        </button>
      </div>
    </section>
  );
}

function StorageScreen({
  copy,
  words,
  dueWord,
  busy,
  sample,
  addWord,
  reviewWord
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  words: WordDto[];
  dueWord?: WordDto;
  busy: boolean;
  sample: string;
  addWord: (word: string) => void;
  reviewWord: (grade: "remember" | "forgot") => void;
}) {
  const [term, setTerm] = useState("");
  const [mode, setMode] = useState<"words" | "review">("words");

  return (
    <>
      <section className="card">
        <h2>{copy("newWord")}</h2>
        <div className="send-row">
          <input value={term} onChange={(event) => setTerm(event.target.value)} placeholder={sample} />
          <button
            className="primary-action"
            disabled={busy || !term.trim()}
            onClick={() => {
              addWord(term);
              setTerm("");
            }}
          >
            <Plus size={18} />
            {copy("add")}
          </button>
        </div>
      </section>
      <div className="segmented">
        <button className={mode === "words" ? "active" : ""} onClick={() => setMode("words")}>
          {copy("myWords")}
        </button>
        <button className={mode === "review" ? "active" : ""} onClick={() => setMode("review")}>
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
              <div className="action-row">
                <button className="soft-action peach" onClick={() => reviewWord("forgot")}>
                  {copy("forgot")}
                </button>
                <button className="soft-action mint" onClick={() => reviewWord("remember")}>
                  {copy("remember")}
                </button>
              </div>
            </>
          ) : (
            <p>{copy("reviewEmpty")}</p>
          )}
        </section>
      ) : (
        <section className="word-list">
          {words.map((word) => (
            <details className="word-card card" key={word.id}>
              <summary>
                <span>
                  <strong>{word.term}</strong>
                  <small>
                    {word.translation} / {word.transcription}
                  </small>
                </span>
                <b>{word.color_level}/5</b>
              </summary>
              <p>{word.meme}</p>
              <p>{word.example_one}</p>
              <p>{word.example_two}</p>
            </details>
          ))}
        </section>
      )}
    </>
  );
}

function ProfileScreen({
  copy,
  locale,
  setLocale,
  user,
  stats,
  learningCode,
  setLearningCode,
  setNativeCode,
  setVibe,
  setTone,
  logout
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  locale: UiLocale;
  setLocale: (locale: UiLocale) => void;
  user: UserDto;
  stats: StatsDto | null;
  learningCode: string;
  setLearningCode: (code: string) => void;
  setNativeCode: (code: string) => void;
  setVibe: (vibe: string) => void;
  setTone: (tone: string) => void;
  logout: () => void;
}) {
  const tones = ["soft sitcom bestie", "chill-bro from California", "strict British aristocrat"];
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
        <Stat value={`${user.daily_vibe_minutes}`} label="min/day" />
      </section>
      <DropdownSelect title={copy("uiLanguage")} value={locale} options={uiLocales} onChange={(value) => setLocale(value as UiLocale)} />
      <DropdownSelect title={copy("learningLanguage")} value={learningCode} options={learningLanguages} onChange={setLearningCode} />
      <DropdownSelect title={copy("nativeLanguage")} value={user.native_language_code} options={nativeLanguages} onChange={setNativeCode} />

      <section className="card settings-card">
        <h2>{copy("learningVibe")}</h2>
        <div className="button-grid">
          {["Chill", "Normal", "Hardcore"].map((vibe) => (
            <button key={vibe} className={user.learning_vibe === vibe ? "selected" : ""} onClick={() => setVibe(vibe)}>
              {vibe}
            </button>
          ))}
        </div>
      </section>

      <section className="card settings-card">
        <h2>{copy("aiTone")}</h2>
        <div className="tone-list">
          {tones.map((tone) => (
            <button key={tone} className={user.ai_tone === tone ? "selected" : ""} onClick={() => setTone(tone)}>
              <Bot size={17} />
              {tone}
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
        <strong>{learning.short}</strong>
        <span>→</span>
        <strong>{native.short}</strong>
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
                  {option.short}
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
                  {option.short}
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
  onChange
}: {
  title: string;
  value: string;
  options: readonly SelectOption[];
  onChange: (value: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const selected = options.find((option) => option.code === value) ?? options[0];
  return (
    <section className={`select-card card ${open ? "open" : ""}`}>
      <button className="select-trigger" onClick={() => setOpen((current) => !current)}>
        <span>
          <small>{title}</small>
          <strong>
            {selected.short} · {selected.label}
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
              onClick={() => {
                onChange(option.code);
                setOpen(false);
              }}
            >
              <span>{option.short}</span>
              {option.label}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

function GrammarLab({
  copy,
  drop,
  topics,
  checkGrammar
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
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
        <p>Граматика завантажується. Якщо backend спить, натисни refresh.</p>
      </section>
    );
  }

  return (
    <section className="card grammar-lab">
      <div className="section-title grammar-title">
        <div>
          <h2>{copy("grammar")}</h2>
          <p>Міні-урок, приклади і перевірка відповіді. Без полотна правил.</p>
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
          <button key={item.id} className={item.id === topic.id ? "selected" : ""} onClick={() => selectTopic(item.id)}>
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
            placeholder="Впиши правильне речення"
          />
        )}
        <div className="exercise-actions">
          <button className="primary-action" disabled={checking || !answer.trim()} onClick={submitAnswer}>
            <Check size={17} />
            {checking ? "..." : "Перевірити"}
          </button>
          <button className="soft-action" onClick={nextExercise}>
            Далі
          </button>
        </div>
        {result && (
          <div className="grammar-feedback">
            <strong>{result.correct ? "Так, воно." : "Ще трошки."}</strong>
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

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognition;
    webkitSpeechRecognition?: new () => SpeechRecognition;
  }
}

type SpeechRecognition = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
};

type SpeechRecognitionEvent = {
  results: ArrayLike<ArrayLike<{ transcript: string }>>;
};
