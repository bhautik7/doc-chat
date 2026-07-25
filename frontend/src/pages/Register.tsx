import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(email, password);
      navigate("/documents");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
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
        <h1 className="text-2xl font-semibold mb-6">
          Create a Doc Chat Account
        </h1>

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
          {loading ? "Creating account..." : "Register"}
        </button>

        <p className="mt-4 text-sm text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}