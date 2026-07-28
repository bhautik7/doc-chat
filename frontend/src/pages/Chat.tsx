import { useState, useEffect, useRef } from "react";
import type { FormEvent } from "react";
import apiClient from "../api/client";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: string | null;
  created_at: string;
}

function localMessage(role: Message["role"], content: string): Message {
  return {
    id: Date.now(),
    role,
    content,
    sources: null,
    created_at: "",
  };
}

export default function Chat() {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initSession = async () => {
      const res = await apiClient.post("/chat/sessions");
      setSessionId(res.data.id);
    };

    initSession();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();

    if (!input.trim() || !sessionId || loading) {
      return;
    }

    const question = input;

    setInput("");
    setLoading(true);

    setMessages((prev) => [...prev, localMessage("user", question)]);

    try {
      const res = await apiClient.post("/chat/ask", {
        session_id: sessionId,
        question,
      });

      setMessages((prev) => [...prev, res.data]);
    } catch {
      setMessages((prev) => [
        ...prev,
        localMessage("assistant", "Something went wrong. Please try again."),
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto h-screen flex flex-col p-6">
      <h1 className="text-2xl font-semibold mb-4">Doc Chat</h1>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={msg.role === "user" ? "text-right" : "text-left"}
          >
            <div
              className={`inline-block px-4 py-2 rounded-lg max-w-[80%] ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              {msg.content}
            </div>

            {msg.sources && JSON.parse(msg.sources).length > 0 && (
              <div className="text-xs text-gray-500 mt-1">
                Sources: {JSON.parse(msg.sources).length} document excerpt(s)
              </div>
            )}
          </div>
        ))}

        {loading && (
          <p className="text-sm text-gray-400">
            Thinking...
          </p>
        )}

        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-1 px-3 py-2 border rounded-md"
        />

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 rounded-md disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}