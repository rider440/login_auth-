import AuthCard from "@/components/AuthCard";
import LoginForm from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <div className="auth-page-container">
      <AuthCard 
        title="Welcome Back" 
        subtitle="Sign in to your account using your phone number"
      >
        <LoginForm />
      </AuthCard>
    </div>
  );
}
