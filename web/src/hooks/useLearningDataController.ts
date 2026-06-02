import { useEffect, useReducer } from "react";
import {
  api,
  type ContextAnalyzeDto,
  type GrammarCheckDto,
  type UserDto,
  type WordDto
} from "../api";
import { languageName, uiLocales, type UiLocale } from "../i18n";
import { createInitialLearningDataState, learningDataReducer } from "../state/learningDataState";

type LearningDataControllerOptions = {
  clearContext: () => void;
  clearHints: () => void;
  resetChat: () => void;
  setUiLocale: (locale: UiLocale) => void;
};

const demoEmail = "dreamer@pajamatalk.dev";
const demoPassword = "pajama-dev-secret";

function uiLocaleFromCode(code: string): UiLocale {
  return uiLocales.some((locale) => locale.code === code) ? (code as UiLocale) : "en";
}

export function useLearningDataController({
  clearContext,
  clearHints,
  resetChat,
  setUiLocale
}: LearningDataControllerOptions) {
  const [state, dispatch] = useReducer(
    learningDataReducer,
    undefined,
    () => createInitialLearningDataState(localStorage.getItem("pajama-token") || "")
  );
  const explanationCode = state.user?.native_language_code ?? "uk";
  const targetLanguage = languageName(explanationCode);

  useEffect(() => {
    api.health().catch(() => dispatch({ type: "setError", error: "FastAPI offline. Запусти backend на :8000." }));
    if (state.token) {
      void openSession(state.token);
    }
  }, []);

  async function loadData(nextToken = state.token, languageCode = state.learningCode, targetCode = explanationCode) {
    if (!nextToken) return;
    const [stats, words, dueWords, rooms, grammarDrops, grammarTopics, learningPath] = await Promise.all([
      api.stats(nextToken),
      api.words(nextToken, languageCode),
      api.dueWords(nextToken, languageCode),
      api.speakingRooms(nextToken, languageCode, targetCode),
      api.grammarDrops(nextToken, languageCode, targetCode),
      api.grammarTopics(nextToken, languageCode, targetCode),
      api.learningPath(nextToken, languageCode, targetCode)
    ]);
    dispatch({
      type: "setData",
      data: { stats, words, dueWords, rooms, grammarDrops, grammarTopics, learningPath }
    });
  }

  async function openSession(nextToken: string) {
    dispatch({ type: "setBusy", busy: true });
    dispatch({ type: "setError", error: "" });
    try {
      const profile = await api.me(nextToken);
      localStorage.setItem("pajama-token", nextToken);
      dispatch({ type: "hydrateSession", token: nextToken, user: profile });
      setUiLocale(uiLocaleFromCode(profile.native_language_code));
      await loadData(nextToken, profile.active_language_code, profile.native_language_code);
    } catch (err) {
      localStorage.removeItem("pajama-token");
      dispatch({ type: "clearSession" });
      dispatch({ type: "setError", error: err instanceof Error ? err.message : "Session failed." });
    } finally {
      dispatch({ type: "setBusy", busy: false });
    }
  }

  async function login(email: string, password: string, displayName?: string) {
    dispatch({ type: "setBusy", busy: true });
    dispatch({ type: "setError", error: "" });
    try {
      const session = displayName ? await api.register(email, password, displayName) : await api.login(email, password);
      await openSession(session.access_token);
    } catch (err) {
      dispatch({ type: "setError", error: err instanceof Error ? err.message : "Auth failed." });
    } finally {
      dispatch({ type: "setBusy", busy: false });
    }
  }

  async function demo() {
    dispatch({ type: "setBusy", busy: true });
    dispatch({ type: "setError", error: "" });
    try {
      let session;
      try {
        session = await api.register(demoEmail, demoPassword, "Dreamer");
      } catch {
        session = await api.login(demoEmail, demoPassword);
      }
      await openSession(session.access_token);
    } catch (err) {
      dispatch({ type: "setError", error: err instanceof Error ? err.message : "Demo login failed." });
    } finally {
      dispatch({ type: "setBusy", busy: false });
    }
  }

  async function updateLearning(code: string) {
    if (!state.token) return;
    dispatch({ type: "setLearningCode", code });
    resetChat();
    clearContext();
    const profile = await api.updateProfile(state.token, { active_language_code: code });
    dispatch({ type: "setUser", user: profile });
    await loadData(state.token, code);
  }

  async function updateNative(code: string) {
    if (!state.token) return;
    clearHints();
    clearContext();
    setUiLocale(uiLocaleFromCode(code));
    const profile = await api.updateProfile(state.token, { native_language_code: code });
    dispatch({ type: "setUser", user: profile });
    setUiLocale(uiLocaleFromCode(profile.native_language_code));
    await loadData(state.token, state.learningCode, profile.native_language_code);
  }

  async function updateVibe(vibe: string) {
    if (!state.token) return;
    const minutes = vibe === "Hardcore" ? 30 : vibe === "Normal" ? 15 : 5;
    const profile = await api.updateProfile(state.token, { learning_vibe: vibe, daily_vibe_minutes: minutes });
    dispatch({ type: "setUser", user: profile });
    dispatch({ type: "setStats", stats: await api.stats(state.token) });
  }

  async function updateTone(tone: string) {
    if (!state.token) return;
    dispatch({ type: "setUser", user: await api.updateProfile(state.token, { ai_tone: tone }) });
  }

  async function updateProfileSettings(payload: Partial<Record<string, string | number>>) {
    if (!state.token) return;
    const profile = await api.updateProfile(state.token, payload);
    dispatch({ type: "setUser", user: profile });
    dispatch({ type: "setLearningCode", code: profile.active_language_code });
    await loadData(state.token, profile.active_language_code, profile.native_language_code);
  }

  async function addWord(term: string, source = ""): Promise<WordDto | undefined> {
    if (!state.token || !term.trim()) return undefined;
    dispatch({ type: "setBusy", busy: true });
    try {
      const word = await api.enrichWord(state.token, term.trim(), state.learningCode, targetLanguage, source);
      dispatch({ type: "upsertWord", word });
      dispatch({ type: "setStats", stats: await api.stats(state.token) });
      return word;
    } catch (err) {
      dispatch({ type: "setError", error: err instanceof Error ? err.message : "Could not add word." });
      return undefined;
    } finally {
      dispatch({ type: "setBusy", busy: false });
    }
  }

  async function analyzeContext(text: string): Promise<ContextAnalyzeDto | undefined> {
    if (!state.token || text.trim().length < 3) return undefined;
    dispatch({ type: "setBusy", busy: true });
    dispatch({ type: "setError", error: "" });
    try {
      return await api.analyzeContext(state.token, text, state.learningCode, targetLanguage);
    } catch (err) {
      dispatch({ type: "setError", error: err instanceof Error ? err.message : "Context analysis failed." });
      return undefined;
    } finally {
      dispatch({ type: "setBusy", busy: false });
    }
  }

  async function reviewWord(grade: "remember" | "forgot", wordId?: number) {
    if (!state.token || !wordId) return;
    await api.reviewWord(state.token, wordId, grade);
    await loadData(state.token, state.learningCode);
  }

  async function deleteWord(wordId: number) {
    if (!state.token) return;
    try {
      await api.deleteWord(state.token, wordId);
      dispatch({ type: "removeWord", wordId });
      dispatch({ type: "setStats", stats: await api.stats(state.token) });
    } catch (err) {
      dispatch({ type: "setError", error: err instanceof Error ? err.message : "Could not delete word." });
    }
  }

  async function refreshGrammar() {
    if (!state.token) return;
    const [drops, topics] = await Promise.all([
      api.grammarDrops(state.token, state.learningCode, explanationCode),
      api.grammarTopics(state.token, state.learningCode, explanationCode)
    ]);
    dispatch({ type: "setGrammar", drops, topics });
  }

  async function checkGrammar(topicId: string, exerciseId: string, answer: string): Promise<GrammarCheckDto> {
    if (!state.token) throw new Error("No active session.");
    return api.checkGrammar(state.token, topicId, exerciseId, answer, explanationCode);
  }

  function setError(error: string) {
    dispatch({ type: "setError", error });
  }

  function logout() {
    localStorage.removeItem("pajama-token");
    dispatch({ type: "clearSession" });
    clearContext();
    resetChat();
  }

  return {
    state,
    explanationCode,
    targetLanguage,
    actions: {
      addWord,
      analyzeContext,
      checkGrammar,
      deleteWord,
      demo,
      loadData,
      login,
      logout,
      openSession,
      refreshGrammar,
      reviewWord,
      setError,
      updateLearning,
      updateNative,
      updateProfileSettings,
      updateTone,
      updateVibe
    }
  };
}
