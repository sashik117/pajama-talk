import { afterEach, describe, expect, it, vi } from "vitest";
import { getSpeechLang, speakText } from "./speech";

class MockUtterance {
  text: string;
  lang = "";
  rate = 1;

  constructor(text: string) {
    this.text = text;
  }
}

describe("speech utilities", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("maps supported language codes to browser speech locales", () => {
    expect(getSpeechLang("pl")).toBe("pl-PL");
    expect(getSpeechLang("ja")).toBe("ja-JP");
    expect(getSpeechLang("unknown")).toBe("en-US");
  });

  it("speaks text with the selected learning language", () => {
    const speak = vi.fn();
    const cancel = vi.fn();
    vi.stubGlobal("window", {
      speechSynthesis: { cancel, speak },
    });
    vi.stubGlobal("SpeechSynthesisUtterance", MockUtterance);

    const spoken = speakText("hello", "pl", 0.8);

    expect(spoken).toBe(true);
    expect(cancel).toHaveBeenCalledOnce();
    expect(speak).toHaveBeenCalledOnce();
    expect(speak.mock.calls[0][0]).toMatchObject({ text: "hello", lang: "pl-PL", rate: 0.8 });
  });

  it("does nothing when browser speech synthesis is unavailable", () => {
    vi.stubGlobal("window", {});

    expect(speakText("hello", "en")).toBe(false);
  });
});
