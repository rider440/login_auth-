import AuthCard from "@/components/AuthCard";
import RegisterForm from "@/components/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="auth-page-container">
      <AuthCard 
        title="Create Account" 
        subtitle="Join us and experience the premium features"
      >
        <RegisterForm />
      </AuthCard>
    </div>
  );
}
