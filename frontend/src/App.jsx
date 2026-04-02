import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./components/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./components/LoginPage";
import SignupPage from "./components/SignupPage";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import PlatformCard from "./components/PlatformCard";
import AnalysisForm from "./components/AnalysisForm";
import ResultDisplay from "./components/ResultDisplay";
import Footer from "./components/Footer";
import { PLATFORMS } from "./platforms";
import { predictPlatform } from "./api";

function Dashboard() {
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      const res = await predictPlatform(selectedPlatform, data);
      setResult(res);
    } catch (err) {
      setError(err.message || "Failed to connect to the server. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const config = selectedPlatform ? PLATFORMS[selectedPlatform] : null;

  return (
    <>
      {!selectedPlatform ? (
        <>
          <Hero />
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
          </div>

          {error && <div className="error-message">⚠️ {error}</div>}

          {!result ? (
            <AnalysisForm
              config={config}
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

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Navbar />
              <Dashboard />
              <Footer />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
