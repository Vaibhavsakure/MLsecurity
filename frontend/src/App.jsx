import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./components/AuthContext";
import { useAuth } from "./components/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import ErrorBoundary from "./components/ErrorBoundary";
import LoginPage from "./components/LoginPage";
import SignupPage from "./components/SignupPage";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import UrlScanner from "./components/UrlScanner";
import PlatformCard from "./components/PlatformCard";
import AnalysisForm from "./components/AnalysisForm";
import ResultDisplay from "./components/ResultDisplay";
import HistoryPage from "./components/HistoryPage";
import DashboardPage from "./components/DashboardPage";
import BatchAnalysis from "./components/BatchAnalysis";
import ComparisonMode from "./components/ComparisonMode";
import ApiKeysPage from "./components/ApiKeysPage";
import Chatbot from "./components/Chatbot";
import Footer from "./components/Footer";
import { PLATFORMS } from "./platforms";
import { predictPlatform, setTokenProvider } from "./api";
import { saveAnalysis } from "./firebase";

function Home() {
  const { user } = useAuth();
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [ensembleMode, setEnsembleMode] = useState(false);

  const handleSelectPlatform = (platform) => {
    setSelectedPlatform(platform);
    setResult(null);
    setError(null);
  };

  const handleBack = () => {
    setSelectedPlatform(null);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await predictPlatform(selectedPlatform, data, { ensemble: ensembleMode });
      setResult(res);
      if (user) {
        saveAnalysis(user.uid, res).catch((err) =>
          console.error("Failed to save analysis:", err)
        );
      }
    } catch (err) {
      setError(err.message || "Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  // Handle URL scanner result (direct prediction)
  const handleUrlScanResult = (res) => {
    setResult(res);
    setSelectedPlatform(res.platform);
    if (user) {
      saveAnalysis(user.uid, res).catch((err) =>
        console.error("Failed to save analysis:", err)
      );
    }
  };

  // Handle URL scanner platform detection (needs manual input)
  const handlePlatformDetected = (platform) => {
    setSelectedPlatform(platform);
    setResult(null);
    setError(null);
  };

  const config = selectedPlatform ? PLATFORMS[selectedPlatform] : null;

  return (
    <>
      {!selectedPlatform ? (
        <>
          <Hero />
          <UrlScanner
            onResult={handleUrlScanResult}
            onPlatformDetected={handlePlatformDetected}
          />
          <div className="platforms-grid">
            {Object.entries(PLATFORMS).map(([key, cfg]) => (
              <PlatformCard
                key={key}
                platform={key}
                config={cfg}
                onClick={handleSelectPlatform}
              />
            ))}
          </div>
        </>
      ) : (
        <div
          className="analysis-page"
          style={{ "--platform-color": config.color }}
        >
          <button className="back-button" onClick={handleBack}>
            ← Back to Platforms
          </button>

          <div className="analysis-header">
            <div className="platform-dot" />
            <h2>{config.name} Analysis</h2>
            {config.synthetic && (
              <span className="synthetic-badge-inline">⚗️ Synthetic Model</span>
            )}
          </div>

          {config.dataWarning && (
            <div className="synthetic-warning-banner">
              ⚗️ {config.dataWarning}
            </div>
          )}

          {/* Ensemble Mode Toggle */}
          <div className="ensemble-toggle">
            <button
              className={`ensemble-switch ${ensembleMode ? "active" : ""}`}
              onClick={() => setEnsembleMode(!ensembleMode)}
            />
            <label onClick={() => setEnsembleMode(!ensembleMode)}>
              🧠 Ensemble Mode {ensembleMode ? "(3 Models)" : "(XGBoost Only)"}
            </label>
          </div>

          {error && <div className="error-message">⚠️ {error}</div>}

          {!result ? (
            <AnalysisForm
              config={config}
              platform={selectedPlatform}
              onSubmit={handleSubmit}
              loading={loading}
            />
          ) : (
            <ResultDisplay result={result} onReset={() => setResult(null)} />
          )}
        </div>
      )}
    </>
  );
}

function ProtectedLayout({ children }) {
  return (
    <>
      <Navbar />
      {children}
      <Chatbot />
      <Footer />
    </>
  );
}

/**
 * TokenInjector — wires the Firebase token provider into the API layer.
 * Must be inside AuthProvider so it has access to getIdToken.
 */
function TokenInjector({ children }) {
  const { getIdToken } = useAuth();

  useEffect(() => {
    setTokenProvider(getIdToken);
  }, [getIdToken]);

  return children;
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <TokenInjector>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <ProtectedLayout><Home /></ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <ProtectedLayout><HistoryPage /></ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <ProtectedLayout><DashboardPage /></ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/batch"
              element={
                <ProtectedRoute>
                  <ProtectedLayout><BatchAnalysis /></ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/compare"
              element={
                <ProtectedRoute>
                  <ProtectedLayout><ComparisonMode /></ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/api-keys"
              element={
                <ProtectedRoute>
                  <ProtectedLayout><ApiKeysPage /></ProtectedLayout>
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </TokenInjector>
      </AuthProvider>
    </ErrorBoundary>
  );
}
