import type {
  GrammarDropDto,
  GrammarTopicDto,
  LearningPathDto,
  SpeakingRoomDto,
  StatsDto,
  UserDto,
  WordDto
} from "../api";

export type LearningDataPayload = {
  stats: StatsDto;
  words: WordDto[];
  dueWords: WordDto[];
  rooms: SpeakingRoomDto[];
  grammarDrops: GrammarDropDto[];
  grammarTopics: GrammarTopicDto[];
  learningPath: LearningPathDto | null;
};

export type LearningDataState = {
  token: string;
  user: UserDto | null;
  stats: StatsDto | null;
  words: WordDto[];
  dueWords: WordDto[];
  rooms: SpeakingRoomDto[];
  grammarDrops: GrammarDropDto[];
  grammarTopics: GrammarTopicDto[];
  learningPath: LearningPathDto | null;
  learningCode: string;
  error: string;
  busy: boolean;
};

type LearningDataAction =
  | { type: "setBusy"; busy: boolean }
  | { type: "setError"; error: string }
  | { type: "hydrateSession"; token: string; user: UserDto }
  | { type: "setUser"; user: UserDto | null }
  | { type: "setLearningCode"; code: string }
  | { type: "setData"; data: LearningDataPayload }
  | { type: "setStats"; stats: StatsDto | null }
  | { type: "setGrammar"; drops: GrammarDropDto[]; topics: GrammarTopicDto[] }
  | { type: "upsertWord"; word: WordDto }
  | { type: "removeWord"; wordId: number }
  | { type: "clearSession" };

export function createInitialLearningDataState(token = ""): LearningDataState {
  return {
    token,
    user: null,
    stats: null,
    words: [],
    dueWords: [],
    rooms: [],
    grammarDrops: [],
    grammarTopics: [],
    learningPath: null,
    learningCode: "en",
    error: "",
    busy: false
  };
}

export function learningDataReducer(state: LearningDataState, action: LearningDataAction): LearningDataState {
  switch (action.type) {
    case "setBusy":
      return { ...state, busy: action.busy };
    case "setError":
      return { ...state, error: action.error };
    case "hydrateSession":
      return {
        ...state,
        token: action.token,
        user: action.user,
        learningCode: action.user.active_language_code
      };
    case "setUser":
      return { ...state, user: action.user };
    case "setLearningCode":
      return { ...state, learningCode: action.code };
    case "setData":
      return {
        ...state,
        stats: action.data.stats,
        words: action.data.words,
        dueWords: action.data.dueWords,
        rooms: action.data.rooms,
        grammarDrops: action.data.grammarDrops,
        grammarTopics: action.data.grammarTopics,
        learningPath: action.data.learningPath
      };
    case "setStats":
      return { ...state, stats: action.stats };
    case "setGrammar":
      return { ...state, grammarDrops: action.drops, grammarTopics: action.topics };
    case "upsertWord":
      return {
        ...state,
        words: [action.word, ...state.words.filter((item) => item.id !== action.word.id)],
        dueWords: [action.word, ...state.dueWords.filter((item) => item.id !== action.word.id)]
      };
    case "removeWord":
      return {
        ...state,
        words: state.words.filter((word) => word.id !== action.wordId),
        dueWords: state.dueWords.filter((word) => word.id !== action.wordId)
      };
    case "clearSession":
      return createInitialLearningDataState();
    default:
      return state;
  }
}
