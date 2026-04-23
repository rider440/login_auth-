import Link from "next/link";

export default function Home() {
  return (
    <div className="glass-card text-center">
      <h1>Welcome</h1>
      <p className="subtitle">Experience modern authentication</p>
      
      <div className="flex flex-col gap-4 mt-4">
        <Link href="/login" className="text-link" style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'block' }}>
          <button>Login with Phone</button>
        </Link>
        
        <Link href="/register" className="text-link" style={{ fontSize: '1.1rem', display: 'block' }}>
          <button style={{ background: 'transparent', border: '2px solid var(--primary)', color: 'var(--primary)', boxShadow: 'none' }}>
            Create an Account
          </button>
        </Link>
      </div>
      
      <div className="auth-footer">
        Powered by Next.js & Vanilla CSS
      </div>
    </div>
  );
}
