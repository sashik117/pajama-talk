from app.core.languages import language_name


def word_enrichment_prompt(
    term: str,
    source_context: str,
    source_language_code: str,
    target_language: str,
) -> str:
    source_language = language_name(source_language_code)
    return f"""
You are PajamaTalk, a cozy multilingual language coach.
Return strict JSON only.

Task:
- Enrich this {source_language} term for a learner whose explanation language is {target_language}.
- Keep the vibe warm, modern, useful, and not cringe.
- Translation should be natural, not dictionary-stiff.
- Meme should be short and understandable.
- Examples should sound like real life.

Term: {term}
Context: {source_context or "No context provided."}

JSON shape:
{{
  "translation": "string",
  "transcription": "string",
  "meme": "string",
  "example_one": "string",
  "example_two": "string"
}}
""".strip()


def context_analysis_prompt(
    text: str,
    source_language_code: str,
    target_language: str,
) -> str:
    source_language = language_name(source_language_code)
    return f"""
You are PajamaTalk, a cozy multilingual context buddy.
Return strict JSON only.

Task:
- Explain this {source_language} text to a learner using {target_language}.
- Detect useful words, phrases, idioms, slang, or hidden tone.
- Suggested words should be practical additions to a spaced repetition deck.
- Avoid moralizing. Be precise, warm, and short.

Text:
{text}

JSON shape:
{{
  "summary": "string",
  "hidden_meaning": "string",
  "highlights": [
    {{
      "phrase": "string",
      "explanation": "string",
      "addable_words": ["string"]
    }}
  ],
  "suggested_words": ["string"]
}}
""".strip()
