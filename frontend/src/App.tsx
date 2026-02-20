import { useState, useEffect } from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import CampaignForm from "./components/CampaignForm";
import CampaignResults from "./components/CampaignResults";
import ApiKeyModal from "./components/ApiKeyModal";
import SampleOutputs from "./components/SampleOutputs";
import type { CampaignBrief, CampaignResponse } from "./types/campaign";
import type { ApiKeys, AuthMode } from "./types/auth";
import { hasValidKeys, saveKeys, loadKeys } from "./types/auth";
import {
  generateFullCampaign,
  generateCopyOnly,
  generateFreeCampaign,
  parseApiError,
} from "./services/api";
import "./App.css";

function App() {
  const [result, setResult] = useState<CampaignResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<ApiKeys | null>(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode | null>(null);
  const location = useLocation();

  useEffect(() => {
    const stored = loadKeys();
    if (hasValidKeys(stored)) {
      setApiKeys(stored);
      setAuthMode("byok");
    } else {
      setShowKeyModal(true);
    }
  }, []);

  const handleSaveKeys = (keys: ApiKeys) => {
    saveKeys(keys);
    setApiKeys(keys);
    setAuthMode("byok");
    setShowKeyModal(false);
  };

  const handleTryFree = () => {
    setAuthMode("free");
    setShowKeyModal(false);
  };

  const handleChangeKeys = () => {
    setShowKeyModal(true);
  };

  const handleSubmit = async (brief: CampaignBrief, generateImage: boolean) => {
    if (authMode === "free") {
      setIsLoading(true);
      setError(null);

      try {
        const response = await generateFreeCampaign(brief);
        setResult(response);
      } catch (err: unknown) {
        const message = parseApiError(err);
        setError(message);
        // If free tier exhausted, show the key modal
        if (message.includes("free generations")) {
          setShowKeyModal(true);
          setAuthMode(null);
        }
      } finally {
        setIsLoading(false);
      }
      return;
    }

    if (!apiKeys) {
      setShowKeyModal(true);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = generateImage
        ? await generateFullCampaign(brief, apiKeys)
        : await generateCopyOnly(brief, apiKeys);
      setResult(response);
    } catch (err: unknown) {
      const message = parseApiError(err);
      setError(message);
      // If it's an auth error, reopen the key modal
      if (message.includes("API key is invalid") || message.includes("revoked")) {
        setShowKeyModal(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  const isHome = location.pathname === "/";

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Social Market</h1>
        <p>Create engaging social media content for your UK business in seconds</p>
        <nav className="header-nav">
          <Link to="/" className={`nav-link ${isHome ? "active" : ""}`}>
            Generate
          </Link>
          <Link
            to="/samples"
            className={`nav-link ${location.pathname === "/samples" ? "active" : ""}`}
          >
            Sample Outputs
          </Link>
          {authMode === "free" && (
            <button className="btn-link" onClick={handleChangeKeys}>
              Use Your Own Keys
            </button>
          )}
          {authMode === "byok" && apiKeys && (
            <button className="btn-link" onClick={handleChangeKeys}>
              Change API Keys
            </button>
          )}
        </nav>
        {authMode === "free" && (
          <div className="free-tier-banner">
            Free tier active — using shared API keys
          </div>
        )}
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}

        <Routes>
          <Route
            path="/"
            element={
              <>
                {showKeyModal && (
                  <ApiKeyModal
                    onSave={handleSaveKeys}
                    onTryFree={handleTryFree}
                    initialKeys={apiKeys}
                  />
                )}

                {!showKeyModal && (
                  <>
                    {result ? (
                      <CampaignResults result={result} onReset={handleReset} />
                    ) : (
                      <CampaignForm onSubmit={handleSubmit} isLoading={isLoading} />
                    )}
                  </>
                )}
              </>
            }
          />
          <Route path="/samples" element={<SampleOutputs />} />
        </Routes>
      </main>

      <footer className="app-footer">
        <p>Made for UK small businesses</p>
      </footer>
    </div>
  );
}

export default App;
