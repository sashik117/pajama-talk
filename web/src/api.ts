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
  current_level: string;
  target_level: string;
  effort_level: string;
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
  status: string;
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
export type GrammarTopicDto = {
  id: string;
  tag: string;
  title: string;
  level: string;
  summary: string;
  micro_lesson: string;
  rules: string[];
  examples: Array<{ wrong: string | null; right: string; note: string }>;
  exercises: Array<{ id: string; type: string; prompt: string; options: string[]; explanation: string }>;
  recommended: boolean;
  reason: string;
};
export type GrammarCheckDto = {
  correct: boolean;
  expected: string;
  feedback: string;
  score_delta: number;
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
export type CallSummaryDto = {
  topic: string;
  new_phrases: string[];
  grammar_feedback: string;
  turns: number;
};
export type LearningPathDto = {
  language_code: string;
  language_name: string;
  level: string;
  assistant_role: string;
  next_room_prompt: string;
  steps: Array<{
    id: string;
    title: string;
    goal: string;
    teacher_note: string;
    micro_task: string;
    examples: Array<{ phrase: string; pronunciation: string; meaning: string }>;
  }>;
};

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

function withQuery(path: string, params: Record<string, string | undefined>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const serialized = query.toString();
  return serialized ? `${path}?${serialized}` : path;
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
  grammarDrops: (token: string, languageCode?: string, targetLanguageCode?: string) =>
    request<GrammarDropDto[]>(withQuery("/grammar/drops", { language_code: languageCode, target_language_code: targetLanguageCode }), { token }),
  grammarTopics: (token: string, languageCode?: string, targetLanguageCode?: string) =>
    request<GrammarTopicDto[]>(withQuery("/grammar/topics", { language_code: languageCode, target_language_code: targetLanguageCode }), { token }),
  checkGrammar: (token: string, topicId: string, exerciseId: string, answer: string, targetLanguageCode?: string) =>
    request<GrammarCheckDto>(withQuery("/grammar/check", { target_language_code: targetLanguageCode }), {
      method: "POST",
      token,
      body: JSON.stringify({ topic_id: topicId, exercise_id: exerciseId, answer })
    }),
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
  speakingRooms: (token: string, languageCode: string, targetLanguageCode?: string) =>
    request<SpeakingRoomDto[]>(withQuery("/speaking/rooms", { language_code: languageCode, target_language_code: targetLanguageCode }), { token }),
  learningPath: (token: string, languageCode: string, targetLanguageCode?: string) =>
    request<LearningPathDto>(withQuery("/learning/path", { language_code: languageCode, target_language_code: targetLanguageCode }), { token }),
  speakingHints: (token: string, roomId: string, lastMessage: string, languageCode: string) =>
    request<SpeakingHintsDto>("/speaking/hints", {
      method: "POST",
      token,
      body: JSON.stringify({ room_id: roomId, last_message: lastMessage, language_code: languageCode })
    })
};
