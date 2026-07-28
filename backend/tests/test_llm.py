from unittest.mock import MagicMock, patch

from app.rag.llm import SYSTEM_PROMPT, generate_answer


def make_completion(content: str):
    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content=content))]
    return completion


@patch("app.rag.llm.client")
def test_generate_answer_returns_model_content(mock_client):
    mock_client.chat.completions.create.return_value = make_completion("Refunds take 30 days.")

    answer = generate_answer("Refund policy?", ["Refunds are issued within 30 days."])

    assert answer == "Refunds take 30 days."


@patch("app.rag.llm.client")
def test_generate_answer_sends_system_prompt_and_context(mock_client):
    mock_client.chat.completions.create.return_value = make_completion("answer")

    generate_answer("Refund policy?", ["chunk one", "chunk two"])

    kwargs = mock_client.chat.completions.create.call_args.kwargs
    system_message, user_message = kwargs["messages"]
    assert system_message == {"role": "system", "content": SYSTEM_PROMPT}
    assert "chunk one\n\n---\n\nchunk two" in user_message["content"]
    assert "Refund policy?" in user_message["content"]
    assert kwargs["temperature"] == 0.2


@patch("app.rag.llm.client")
def test_generate_answer_handles_empty_context(mock_client):
    mock_client.chat.completions.create.return_value = make_completion("No context provided.")

    assert generate_answer("Anything?", []) == "No context provided."
