import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getErrorMessage } from "../utils/errors";

interface AuthFormProps {
  title: string;
  submitLabel: string;
  pendingLabel: string;
  errorFallback: string;
  footerText: string;
  footerLinkTo: string;
  footerLinkLabel: string;
  onSubmit: (email: string, password: string) => Promise<void>;
}

export default function AuthForm({
  title,
  submitLabel,
  pendingLabel,
  errorFallback,
  footerText,
  footerLinkTo,
  footerLinkLabel,
  onSubmit,
}: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await onSubmit(email, password);
      navigate("/documents");
    } catch (err) {
      setError(getErrorMessage(err, errorFallback));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-lg shadow-md w-96"
      >
        <h1 className="text-2xl font-semibold mb-6">{title}</h1>

        {error && (
          <div className="mb-4 text-sm text-red-600">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full mb-3 px-3 py-2 border rounded-md"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-4 px-3 py-2 border rounded-md"
          required
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-md disabled:opacity-50"
        >
          {loading ? pendingLabel : submitLabel}
        </button>

        <p className="mt-4 text-sm text-center">
          {footerText}{" "}
          <Link to={footerLinkTo} className="text-blue-600">
            {footerLinkLabel}
          </Link>
        </p>
      </form>
    </div>
  );
}
