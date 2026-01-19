import { useState, useEffect } from "react";
import axios from "axios";
import CampaignForm from "./components/CampaignForm";
import CampaignResults from "./components/CampaignResults";
import ApiKeyModal from "./components/ApiKeyModal";
import type { CampaignBrief, CampaignResponse } from "./types/campaign";
import type { ApiKeys } from "./types/auth";
import { hasValidKeys, saveKeys, loadKeys } from "./types/auth";
import { generateFullCampaign, generateCopyOnly } from "./services/api";
import "./App.css";

function App() {
  const [result, setResult] = useState<CampaignResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<ApiKeys | null>(null);
  const [showKeyModal, setShowKeyModal] = useState(false);

  useEffect(() => {
    const stored = loadKeys();
    if (hasValidKeys(stored)) {
      setApiKeys(stored);
    } else {
      setShowKeyModal(true);
    }
  }, []);

  const handleSaveKeys = (keys: ApiKeys) => {
    saveKeys(keys);
    setApiKeys(keys);
    setShowKeyModal(false);
  };

  const handleChangeKeys = () => {
    setShowKeyModal(true);
  };

  const handleSubmit = async (brief: CampaignBrief, generateImage: boolean) => {
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
      if (axios.isAxiosError(err) && err.response?.status === 401) {
        setError("Invalid API key. Please check your keys and try again.");
        setShowKeyModal(true);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Social Market</h1>
        <p>Create engaging social media content for your UK business in seconds</p>
        {apiKeys && (
          <div className="header-actions">
            <button className="btn-link" onClick={handleChangeKeys}>
              Change API Keys
            </button>
          </div>
        )}
      </header>

      <main className="app-main">
        {showKeyModal && (
          <ApiKeyModal onSave={handleSaveKeys} initialKeys={apiKeys} />
        )}

        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
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
      </main>

      <footer className="app-footer">
        <p>Made for UK small businesses</p>
      </footer>
    </div>
  );
}

export default App;
