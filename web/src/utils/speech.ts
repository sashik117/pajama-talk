export function getSpeechLang(code: string) {
  return (
    {
      en: "en-US",
      uk: "uk-UA",
      ru: "ru-RU",
      pl: "pl-PL",
      sk: "sk-SK",
      cs: "cs-CZ",
      fr: "fr-FR",
      es: "es-ES",
      it: "it-IT",
      de: "de-DE",
      pt: "pt-PT",
      ko: "ko-KR",
      ja: "ja-JP",
      zh: "zh-CN",
      tr: "tr-TR"
    }[code] ?? "en-US"
  );
}

export function speakText(text: string, languageCode: string, rate = 0.92): boolean {
  const cleanText = text.trim();
  if (!cleanText || typeof window === "undefined") return false;

  const synth = window.speechSynthesis;
  const Utterance = globalThis.SpeechSynthesisUtterance;
  if (!synth || !Utterance) return false;

  synth.cancel();
  const utterance = new Utterance(cleanText);
  utterance.lang = getSpeechLang(languageCode);
  utterance.rate = rate;
  synth.speak(utterance);
  return true;
}
