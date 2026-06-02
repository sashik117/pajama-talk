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
