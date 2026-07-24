from openai import OpenAI
from app.utils.config import settings

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

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content