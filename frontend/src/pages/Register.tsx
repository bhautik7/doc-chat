import AuthForm from "../components/AuthForm";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();

  return (
    <AuthForm
      title="Create a Doc Chat Account"
      submitLabel="Register"
      pendingLabel="Creating account..."
      errorFallback="Registration failed"
      footerText="Already have an account?"
      footerLinkTo="/login"
      footerLinkLabel="Log in"
      onSubmit={register}
    />
  );
}
