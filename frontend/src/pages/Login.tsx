import AuthForm from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();

  return (
    <AuthForm
      title="Log in to Doc Chat"
      submitLabel="Log in"
      pendingLabel="Logging in..."
      errorFallback="Login failed"
      footerText="No account?"
      footerLinkTo="/register"
      footerLinkLabel="Register"
      onSubmit={login}
    />
  );
}
