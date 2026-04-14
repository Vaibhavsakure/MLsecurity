import { useAuth } from "./AuthContext";
import { logout } from "../firebase";
import { Link, useNavigate, useLocation } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const initial = user?.displayName?.[0] || user?.email?.[0] || "U";
  const displayName = user?.displayName || user?.email?.split("@")[0] || "User";

  const navLinks = [
    { to: "/", label: "Analyze" },
    { to: "/batch", label: "Batch" },
    { to: "/compare", label: "Compare" },
    { to: "/dashboard", label: "Dashboard" },
    { to: "/history", label: "History" },
    { to: "/api-keys", label: "API" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-logo">
          <div className="logo-icon">S</div>
          <span className="logo-text">SocialGuard AI</span>
        </Link>

        {user && (
          <>
            <div className="navbar-links">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`navbar-link ${location.pathname === link.to ? "active" : ""}`}
                >
                  {link.label}
                </Link>
              ))}
            </div>

            <div className="navbar-user">
              <ThemeToggle />
              <div className="user-avatar">{initial.toUpperCase()}</div>
              <span className="user-name">{displayName}</span>
              <button className="logout-btn" onClick={handleLogout} title="Sign out">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
              </button>
            </div>
          </>
        )}
      </div>
    </nav>
  );
}
