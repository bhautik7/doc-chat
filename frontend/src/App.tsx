import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Documents from "./pages/Documents";
import Chat from "./pages/Chat";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/documents"
            element={<ProtectedRoute><Documents /></ProtectedRoute>}
          />
          <Route
            path="/chat"
            element={<ProtectedRoute><Chat /></ProtectedRoute>}
          />
          <Route path="*" element={<Navigate to="/documents" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}