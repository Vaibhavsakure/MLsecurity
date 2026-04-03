import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginWithEmail, signInWithGoogle, signInWithGithub, resetPassword } from "../firebase";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleEmail = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await loginWithEmail(email, password);
      navigate("/");
    } catch (err) {
      setError(friendlyError(err.code));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogle = async () => {
    setError(null);
    setSuccess(null);
    try {
      await signInWithGoogle();
      navigate("/");
    } catch (err) {
      if (err.code !== "auth/popup-closed-by-user") {
        setError(friendlyError(err.code));
      }
    }
  };

  const handleGithub = async () => {
    setError(null);
    setSuccess(null);
    try {
      await signInWithGithub();
      navigate("/");
    } catch (err) {
      if (err.code !== "auth/popup-closed-by-user") {
        setError(friendlyError(err.code));
      }
    }
  };

  const handleForgotPassword = async () => {
    setError(null);
    setSuccess(null);
    if (!email) {
      setError("Enter your email address first, then click Forgot Password.");
      return;
    }
    try {
      await resetPassword(email);
      setSuccess("Password reset email sent! Check your inbox.");
    } catch (err) {
      setError(friendlyError(err.code));
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card glass-card">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <div className="logo-icon">S</div>
            <span className="logo-text">SocialGuard AI</span>
          </div>
          <h2>Welcome back</h2>
          <p className="auth-subtitle">Sign in to continue analyzing accounts</p>
        </div>

        {error && <div className="auth-error">⚠️ {error}</div>}
        {success && <div className="auth-success">✅ {success}</div>}

        {/* Social Sign-In */}
        <div className="social-buttons">
          <button className="google-btn" onClick={handleGoogle} type="button">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>
          
          <button className="github-btn" onClick={handleGithub} type="button">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
            </svg>
            Continue with GitHub
          </button>
        </div>

        {/* Divider */}
        <div className="auth-divider">
          <span>or sign in with email</span>
        </div>

        {/* Email/Password Form */}
        <form className="auth-form" onSubmit={handleEmail}>
          <div className="auth-field">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="auth-field">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          <button
            type="button"
            className="forgot-password-link"
            onClick={handleForgotPassword}
          >
            Forgot password?
          </button>
          <button type="submit" className="auth-submit-btn" disabled={loading}>
            {loading && <span className="spinner" />}
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        {/* Footer */}
        <p className="auth-footer-text">
          Don't have an account?{" "}
          <Link to="/signup" className="auth-link">Create one</Link>
        </p>
      </div>
    </div>
  );
}

function friendlyError(code) {
  switch (code) {
    case "auth/invalid-email": return "Invalid email address.";
    case "auth/user-disabled": return "This account has been disabled.";
    case "auth/user-not-found": return "No account found with this email.";
    case "auth/wrong-password": return "Incorrect password.";
    case "auth/invalid-credential": return "Invalid email or password.";
    case "auth/too-many-requests": return "Too many attempts. Try again later.";
    case "auth/account-exists-with-different-credential":
      return "An account already exists with the same email using a different sign-in method.";
    case "auth/popup-blocked": return "Pop-up blocked by browser. Please allow pop-ups.";
    default: return "Something went wrong. Please try again.";
  }
}
