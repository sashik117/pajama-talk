import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  BriefcaseBusiness,
  Check,
  Coffee,
  Home,
  Languages,
  LogOut,
  Mic,
  Plane,
  Plus,
  RefreshCw,
  Send,
  Sparkles,
  User,
  WandSparkles,
  X
} from "lucide-react";
import { api, ContextAnalyzeDto, GrammarDropDto, SpeakingHintsDto, SpeakingRoomDto, StatsDto, UserDto, WordDto } from "./api";
import { languageName, learningLanguages, nativeLanguages, t, UiLocale, uiLocales } from "./i18n";

type TabKey = "aura" | "speak" | "storage" | "vibe";
type ChatLine = { role: "user" | "assistant"; text: string };

const demoEmail = "dreamer@pajamatalk.dev";
const demoPassword = "pajama-dev-secret";

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
    api.health().catch(() => setError("FastAPI is offline. Start backend on :8000."));
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
    const [nextStats, nextWords, nextDue, nextRooms, nextDrops] = await Promise.all([
      api.stats(nextToken),
      api.words(nextToken, languageCode),
      api.dueWords(nextToken, languageCode),
      api.speakingRooms(nextToken, languageCode),
      api.grammarDrops(nextToken)
    ]);
    setStats(nextStats);
    setWords(nextWords);
    setDueWords(nextDue);
    setRooms(nextRooms);
    setGrammarDrops(nextDrops);
  }

  async function login(email: string, password: string, displayName?: string) {
    setBusy(true);
    setError("");
    try {
      const session = displayName
        ? await api.register(email, password, displayName)
        : await api.login(email, password);
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
          setChat((current) => [...current.slice(0, -1), { role: "assistant", text: reply.trimStart() }]);
        }
        if (payload.type === "done") {
          socket.close();
          resolve();
        }
      };
    }).catch((err) => setError(err instanceof Error ? err.message : "Speaking stream failed."));
    if (token) setGrammarDrops(await api.grammarDrops(token));
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
          <div>
            <h1>PajamaTalk</h1>
            <p>
              {stats?.daily_vibe_minutes ?? 5} min · {selectedLanguage.label}
            </p>
          </div>
          <button className="icon-button" onClick={() => void loadData()} aria-label="Refresh">
            <RefreshCw size={19} />
          </button>
        </header>

        {error && <div className="notice">{error}</div>}

        {activeTab === "aura" && (
          <AuraScreen
            copy={copy}
            stats={stats}
            activeDrop={activeDrop}
            contextText={contextText}
            setContextText={setContextText}
            contextResult={contextResult}
            busy={busy}
            analyzeContext={analyzeContext}
            addWord={addWord}
            clearContext={() => setContextResult(null)}
            learningCode={learningCode}
            setLearningCode={(code) => void updateLearning(code)}
          />
        )}

        {activeTab === "speak" && (
          <SpeakingScreen
            copy={copy}
            rooms={rooms}
            activeRoom={activeRoom}
            chat={chat}
            hints={hints}
            setActiveRoom={(room) => {
              setActiveRoom(room);
              setHints(null);
              setChat([{ role: "assistant", text: `Hey, I am ${room.character}. Send one line and we will keep it easy.` }]);
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
          <VibeScreen
            copy={copy}
            locale={uiLocale}
            setLocale={setUiLocale}
            user={user}
            stats={stats}
            learningCode={learningCode}
            setLearningCode={(code) => void updateLearning(code)}
            setNativeCode={(code) => void updateNative(code)}
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
          <div className="aura-mini" />
          <div>
            <h1>PajamaTalk</h1>
            <p>{copy("tagline")}</p>
          </div>
        </div>

        <LocalePills value={locale} setValue={setLocale} copy={copy} />

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

function AuraScreen({
  copy,
  stats,
  activeDrop,
  contextText,
  setContextText,
  contextResult,
  busy,
  analyzeContext,
  addWord,
  clearContext,
  learningCode,
  setLearningCode
}: {
  copy: (key: Parameters<typeof t>[1]) => string;
  stats: StatsDto | null;
  activeDrop?: GrammarDropDto;
  contextText: string;
  setContextText: (value: string) => void;
  contextResult: ContextAnalyzeDto | null;
  busy: boolean;
  analyzeContext: () => void;
  addWord: (word: string, source?: string) => void;
  clearContext: () => void;
  learningCode: string;
  setLearningCode: (code: string) => void;
}) {
  return (
    <>
      <LanguagePills title={copy("learningLanguage")} value={learningCode} onChange={setLearningCode} />
      <section className="aura-hero card">
        <div className="aura-orb" />
        <div>
          <h2>Aura of Knowledge</h2>
          <p>
            {stats?.due_reviews ?? 0} {copy("due")} · {stats?.learned_words ?? 0} {copy("learned")}
          </p>
        </div>
      </section>

      <section className="card">
        <div className="section-title">
          <WandSparkles size={20} />
          <h2>{copy("contextTitle")}</h2>
        </div>
        <textarea value={contextText} onChange={(event) => setContextText(event.target.value)} placeholder={copy("contextPlaceholder")} />
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

      <GrammarCard copy={copy} drop={activeDrop} />
    </>
  );
}

function SpeakingScreen({
  copy,
  rooms,
  activeRoom,
  chat,
  hints,
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
  setActiveRoom: (room: SpeakingRoomDto) => void;
  back: () => void;
  loadHints: () => void;
  sendMessage: (message: string) => void;
}) {
  const [draft, setDraft] = useState("");
  const roomIcon = useMemo(() => {
    if (!activeRoom) return null;
    if (activeRoom.id.includes("airport")) return <Plane size={28} />;
    if (activeRoom.id.includes("interview")) return <BriefcaseBusiness size={28} />;
    return <Coffee size={28} />;
  }, [activeRoom]);

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
    <section className="card chat-card">
      <button className="ghost-action inline" onClick={back}>
        {copy("rooms")}
      </button>
      <div className="room-head">
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
      <button className="soft-action" onClick={loadHints}>
        <WandSparkles size={16} />
        {copy("hints")}
      </button>
      {hints && (
        <div className="hint-stack">
          {[hints.simple, hints.conversational, hints.spicy].map((hint) => (
            <button key={hint} className="hint" onClick={() => setDraft(hint)}>
              {hint}
            </button>
          ))}
        </div>
      )}
      <div className="send-row">
        <input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder={`Reply to ${activeRoom.character}`} />
        <button
          className="primary-action icon-only"
          disabled={!draft.trim()}
          onClick={() => {
            const text = draft;
            setDraft("");
            sendMessage(text);
          }}
        >
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
            <p>Review deck is calm.</p>
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

function VibeScreen({
  copy,
  locale,
  setLocale,
  user,
  stats,
  learningCode,
  setLearningCode,
  setNativeCode,
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
  logout: () => void;
}) {
  return (
    <>
      <section className="stats-grid">
        <Stat value={`${stats?.language_words ?? 0}`} label="words" />
        <Stat value={`${stats?.due_reviews ?? 0}`} label={copy("due")} />
        <Stat value={learningCode.toUpperCase()} label="language" />
      </section>
      <LocalePills value={locale} setValue={setLocale} copy={copy} />
      <LanguagePills title={copy("learningLanguage")} value={learningCode} onChange={setLearningCode} />
      <NativePills title={copy("nativeLanguage")} value={user.native_language_code} onChange={setNativeCode} />
      <section className="card profile-card">
        <strong>{user.display_name}</strong>
        <span>{user.email}</span>
        <button className="soft-action peach" onClick={logout}>
          <LogOut size={16} />
          {copy("logOut")}
        </button>
      </section>
    </>
  );
}

function LocalePills({
  value,
  setValue,
  copy
}: {
  value: UiLocale;
  setValue: (locale: UiLocale) => void;
  copy: (key: Parameters<typeof t>[1]) => string;
}) {
  return (
    <section className="card compact">
      <div className="section-title">
        <Languages size={18} />
        <h2>{copy("uiLanguage")}</h2>
      </div>
      <div className="pill-row">
        {uiLocales.map((locale) => (
          <button key={locale.code} className={value === locale.code ? "selected" : ""} onClick={() => setValue(locale.code)}>
            {locale.short}
          </button>
        ))}
      </div>
    </section>
  );
}

function LanguagePills({ title, value, onChange }: { title: string; value: string; onChange: (code: string) => void }) {
  return (
    <section className="card compact">
      <h2>{title}</h2>
      <div className="pill-row">
        {learningLanguages.map((language) => (
          <button key={language.code} className={value === language.code ? "selected" : ""} onClick={() => onChange(language.code)}>
            {language.short}
            <span>{language.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function NativePills({ title, value, onChange }: { title: string; value: string; onChange: (code: string) => void }) {
  return (
    <section className="card compact">
      <h2>{title}</h2>
      <div className="pill-row">
        {nativeLanguages.map((language) => (
          <button key={language.code} className={value === language.code ? "selected" : ""} onClick={() => onChange(language.code)}>
            {language.short}
            <span>{language.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function GrammarCard({ copy, drop }: { copy: (key: Parameters<typeof t>[1]) => string; drop?: GrammarDropDto }) {
  const active = drop ?? {
    title: "Past Simple",
    nudge: "Past Simple is tapping the window for 30 seconds.",
    tiny_explanation: "Finished time, finished action.",
    quests: ["I watched it yesterday", "She called me last night"]
  };
  const [done, setDone] = useState("");
  return (
    <section className="card grammar-card">
      <h2>{copy("grammar")}</h2>
      <strong>{active.title}</strong>
      <p>{active.nudge}</p>
      <p>{active.tiny_explanation}</p>
      <div className="quest-list">
        {active.quests.map((quest) => (
          <button key={quest} className={done === quest ? "done" : ""} onClick={() => setDone(quest)}>
            {done === quest ? <Check size={15} /> : <Sparkles size={15} />}
            {quest}
          </button>
        ))}
      </div>
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
