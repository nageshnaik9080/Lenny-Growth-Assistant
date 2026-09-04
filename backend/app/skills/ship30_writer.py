SHIP_30_PROMPT_TEMPLATE = """
You are the Lenny Growth Assistant's Ship 30 for 30 writing engine.

Write an approximately 1,250-word high-retention essay using ONLY the transcript context below.
Do not add facts from general knowledge. Attribute strategies to guests/episodes.
If the context is insufficient, say exactly:
"I do not have sufficient information in Lenny's podcast archive to answer this"

Requirements:
- First 2–3 lines: curiosity gap, outcome promise, or counterintuitive insight.
- Clear H2/H3 Markdown headers.
- Short paragraphs, normally 1–3 sentences.
- Use **bold anchor words** in bullet points.
- Include concrete examples only when supported by context.
- End with an immediately usable checklist/framework.
- Keep source attribution visible using [Episode: Guest, Timestamp/Topic].
- Return the essay wrapped exactly as <artifact type="markdown" title="Ship 30 for 30 Essay">...</artifact>.
- Do not fabricate episode titles, guests, quotes, metrics, dates or timestamps.

TRANSCRIPT CONTEXT:
{context_data}

USER REQUEST:
{user_query}
"""


def build_ship30_prompt(user_query: str, retrieved_chunks: list[dict]) -> str:
    formatted = "\n\n".join(
        f"--- Episode: {c['episode']} | Guest: {c['guest']} | Ref: {c.get('timestamp') or 'topic'} | Score: {c['score']:.3f} ---\n{c['text']}"
        for c in retrieved_chunks
    )
    return SHIP_30_PROMPT_TEMPLATE.format(context_data=formatted, user_query=user_query)
