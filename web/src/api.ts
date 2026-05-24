const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export type TokenResponse = { access_token: string; token_type: string };
export type UserDto = {
  id: number;
  email: string;
  display_name: string;
  learning_vibe: string;
  active_language_code: string;
  native_language_code: string;
  daily_vibe_minutes: number;
  ai_tone: string;
};
export type StatsDto = {
  active_language_code: string;
  total_words: number;
  language_words: number;
  learned_words: number;
  due_reviews: number;
  daily_vibe_minutes: number;
  learning_vibe: string;
  ai_tone: string;
};
export type WordDto = {
  id: number;
  language_code: string;
  term: string;
  translation: string;
  transcription: string;
  meme: string;
  example_one: string;
  example_two: string;
  source_context: string;
  color_level: number;
  due_at: string | null;
};
export type ContextAnalyzeDto = {
  summary: string;
  hidden_meaning: string;
  highlights: Array<{ phrase: string; explanation: string; addable_words: string[] }>;
  suggested_words: string[];
};
export type GrammarDropDto = {
  id: string;
  title: string;
  nudge: string;
  tiny_explanation: string;
  quests: string[];
};
export type SpeakingRoomDto = {
  id: string;
  title: string;
  character: string;
  vibe: string;
  prompt: string;
  accent_color: string;
};
export type SpeakingHintsDto = { simple: string; conversational: string; spicy: string };

type ApiOptions = RequestInit & { token?: string };

async function request<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (options.token) headers.set("Authorization", `Bearer ${options.token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : detail;
    } catch {
      detail = response.statusText;
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  apiUrl: API_URL,
  wsUrl(path: string) {
    const base = API_URL.replace(/^https:/, "wss:").replace(/^http:/, "ws:");
    return `${base}${path}`;
  },
  health: () => request<{ status: string }>("/health"),
  register: (email: string, password: string, displayName: string) =>
    request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name: displayName })
    }),
  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  me: (token: string) => request<UserDto>("/auth/me", { token }),
  updateProfile: (token: string, payload: Partial<Record<string, string | number>>) =>
    request<UserDto>("/auth/me", { method: "PATCH", token, body: JSON.stringify(payload) }),
  stats: (token: string) => request<StatsDto>("/stats/me", { token }),
  grammarDrops: (token: string) => request<GrammarDropDto[]>("/grammar/drops", { token }),
  words: (token: string, languageCode: string) => request<WordDto[]>(`/words?language_code=${languageCode}`, { token }),
  dueWords: (token: string, languageCode: string) =>
    request<WordDto[]>(`/words/review-due?language_code=${languageCode}`, { token }),
  enrichWord: (token: string, term: string, languageCode: string, targetLanguage: string, sourceContext = "") =>
    request<WordDto>("/words/enrich", {
      method: "POST",
      token,
      body: JSON.stringify({
        term,
        language_code: languageCode,
        source_context: sourceContext,
        target_language: targetLanguage
      })
    }),
  reviewWord: (token: string, wordId: number, grade: "remember" | "forgot") =>
    request(`/words/${wordId}/review`, { method: "POST", token, body: JSON.stringify({ grade }) }),
  analyzeContext: (token: string, text: string, languageCode: string, targetLanguage: string) =>
    request<ContextAnalyzeDto>("/context/analyze", {
      method: "POST",
      token,
      body: JSON.stringify({ text, language_code: languageCode, target_language: targetLanguage })
    }),
  speakingRooms: (token: string, languageCode: string) =>
    request<SpeakingRoomDto[]>(`/speaking/rooms?language_code=${languageCode}`, { token }),
  speakingHints: (token: string, roomId: string, lastMessage: string, languageCode: string) =>
    request<SpeakingHintsDto>("/speaking/hints", {
      method: "POST",
      token,
      body: JSON.stringify({ room_id: roomId, last_message: lastMessage, language_code: languageCode })
    })
};
