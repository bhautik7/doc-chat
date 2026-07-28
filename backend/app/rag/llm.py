import logging

from openai import OpenAI, OpenAIError

from app.utils.config import settings
from app.utils.exceptions import LLMError

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based only on the provided document excerpts.

Rules:
- Only use information from the provided context to answer.
- If the context does not contain enough information to answer, say so clearly — do not guess or use outside knowledge.
- Keep answers concise and directly relevant to the question.
- If you reference a specific fact, it should be traceable to the provided context.
"""

def generate_answer(question: str, context_chunks: list[str]) -> str:
    context_text = "\n\n---\n\n".join(context_chunks)

    user_prompt = f"""Context from documents:
{context_text}

Question: {question}

Answer the question using only the context above."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
    except OpenAIError as exc:
        logger.exception("Answer generation failed")
        raise LLMError("Could not generate an answer right now") from exc

    content = response.choices[0].message.content if response.choices else None
    if not content:
        logger.error("Answer generation returned an empty response")
        raise LLMError("The model returned an empty answer")
    return content