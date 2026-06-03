import { describe, expect, it } from "vitest";
import type { LearningDataPayload } from "./learningDataState";
import { createInitialLearningDataState, learningDataReducer } from "./learningDataState";

const user = {
  id: 1,
  email: "dreamer@pajamatalk.dev",
  display_name: "Dreamer",
  learning_vibe: "Chill",
  active_language_code: "pl",
  native_language_code: "uk",
  daily_vibe_minutes: 5,
  ai_tone: "Neutral teacher",
  current_level: "A1",
  target_level: "B1",
  effort_level: "Steady"
};

const stats = {
  active_language_code: "pl",
  total_words: 2,
  language_words: 2,
  learned_words: 1,
  due_reviews: 1,
  daily_vibe_minutes: 5,
  learning_vibe: "Chill",
  ai_tone: "Neutral teacher"
};

const word = {
  id: 7,
  language_code: "pl",
  term: "kawa",
  translation: "кава",
  transcription: "ka-va",
  meme: "coffee mood",
  example_one: "Poproszę kawę.",
  example_two: "Ta kawa jest dobra.",
  source_context: "test",
  status: "learning",
  color_level: 1,
  due_at: null
};

const payload: LearningDataPayload = {
  stats,
  words: [word],
  dueWords: [word],
  rooms: [
    {
      id: "coffee-alex",
      title: "Lo-fi Coffee",
      character: "Alex",
      vibe: "soft",
      prompt: "Order coffee.",
      accent_color: "#F3B6A8"
    }
  ],
  grammarDrops: [{ id: "drop", title: "Past Simple", nudge: "nudge", tiny_explanation: "tiny", quests: ["quest"] }],
  grammarTopics: [
    {
      id: "articles",
      tag: "articles",
      title: "Articles",
      level: "A1",
      summary: "summary",
      micro_lesson: "lesson",
      rules: ["rule"],
      examples: [{ wrong: null, right: "a coffee", note: "note" }],
      exercises: [{ id: "ex", type: "choice", prompt: "prompt", options: ["a"], explanation: "why" }],
      recommended: true,
      reason: "reason"
    }
  ],
  learningPath: {
    language_code: "pl",
    language_name: "Polish",
    level: "A1",
    assistant_role: "teacher",
    next_room_prompt: "coffee",
    profile_summary: "A1 plan",
    coach_tip: "repeat first",
    review_prompt: "review words",
    speaking_drill: "say coffee",
    objectives: ["ask for coffee"],
    daily_plan: [],
    steps: [
      {
        id: "pl-hello",
        title: "Hello",
        goal: "greet",
        teacher_note: "note",
        micro_task: "repeat",
        examples: [],
        vocabulary: [{ term: "Cześć", pronunciation: "cheshch", meaning: "greeting" }]
      }
    ]
  }
};

describe("learningDataReducer", () => {
  it("hydrates the active session and learning code", () => {
    const state = learningDataReducer(createInitialLearningDataState(), {
      type: "hydrateSession",
      token: "token-1",
      user
    });

    expect(state.token).toBe("token-1");
    expect(state.user?.email).toBe(user.email);
    expect(state.learningCode).toBe("pl");
  });

  it("stores the loaded learning data as one consistent snapshot", () => {
    const state = learningDataReducer(createInitialLearningDataState("token-1"), {
      type: "setData",
      data: payload
    });

    expect(state.stats?.language_words).toBe(2);
    expect(state.words).toHaveLength(1);
    expect(state.dueWords[0].term).toBe("kawa");
    expect(state.rooms[0].id).toBe("coffee-alex");
    expect(state.learningPath?.language_name).toBe("Polish");
  });

  it("upserts and removes words without duplicating due cards", () => {
    const base = learningDataReducer(createInitialLearningDataState("token-1"), { type: "setData", data: payload });
    const updatedWord = { ...word, translation: "coffee", color_level: 2 };
    const upserted = learningDataReducer(base, { type: "upsertWord", word: updatedWord });

    expect(upserted.words).toHaveLength(1);
    expect(upserted.words[0].translation).toBe("coffee");
    expect(upserted.dueWords).toHaveLength(1);

    const removed = learningDataReducer(upserted, { type: "removeWord", wordId: word.id });
    expect(removed.words).toHaveLength(0);
    expect(removed.dueWords).toHaveLength(0);
  });

  it("clears session data on logout", () => {
    const loaded = learningDataReducer(createInitialLearningDataState("token-1"), { type: "setData", data: payload });
    const cleared = learningDataReducer(loaded, { type: "clearSession" });

    expect(cleared.token).toBe("");
    expect(cleared.user).toBeNull();
    expect(cleared.words).toHaveLength(0);
    expect(cleared.learningCode).toBe("en");
  });
});
