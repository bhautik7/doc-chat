import { useState, useEffect } from "react";
import type { ChangeEvent } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";
import { getErrorMessage } from "../utils/errors";

interface Doc {
  id: number;
  filename: string;
  file_type: string;
  status: string;
  created_at: string;
}

export default function Documents() {
  const [documents, setDocuments] = useState<Doc[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const fetchDocuments = async () => {
    const res = await apiClient.get("/documents/");
    setDocuments(res.data);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await apiClient.post("/documents/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      await fetchDocuments();
    } catch (err) {
      setError(getErrorMessage(err, "Upload failed"));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (id: number) => {
    await apiClient.delete(`/documents/${id}`);
    await fetchDocuments();
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Your Documents</h1>

        <Link to="/chat" className="text-blue-600">
          Go to Chat →
        </Link>
      </div>

      <label className="block mb-6">
        <span className="sr-only">Upload document</span>

        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleUpload}
          disabled={uploading}
          className="block w-full text-sm border rounded-md p-2"
        />
      </label>

      {uploading && (
        <p className="text-sm text-gray-500 mb-4">
          Uploading and processing...
        </p>
      )}

      {error && (
        <p className="text-sm text-red-600 mb-4">
          {error}
        </p>
      )}

      <ul className="space-y-2">
        {documents.map((doc) => (
          <li
            key={doc.id}
            className="flex justify-between items-center p-3 border rounded-md"
          >
            <div>
              <p className="font-medium">{doc.filename}</p>

              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  doc.status === "ready"
                    ? "bg-green-100 text-green-700"
                    : doc.status === "failed"
                    ? "bg-red-100 text-red-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}
              >
                {doc.status}
              </span>
            </div>

            <button
              onClick={() => handleDelete(doc.id)}
              className="text-sm text-red-600"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}