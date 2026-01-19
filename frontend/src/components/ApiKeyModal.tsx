import { useState } from "react";
import type { ApiKeys } from "../types/auth";

interface ApiKeyModalProps {
  onSave: (keys: ApiKeys) => void;
  initialKeys?: ApiKeys | null;
}

export default function ApiKeyModal({ onSave, initialKeys }: ApiKeyModalProps) {
  const [anthropicKey, setAnthropicKey] = useState(initialKeys?.anthropicKey || "");
  const [openaiKey, setOpenaiKey] = useState(initialKeys?.openaiKey || "");
  const [showKeys, setShowKeys] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (anthropicKey && openaiKey) {
      onSave({ anthropicKey, openaiKey });
    }
  };

  const isValid = anthropicKey.length > 0 && openaiKey.length > 0;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Enter Your API Keys</h2>
        <p className="modal-description">
          This application requires your own API keys to generate content.
          Keys are stored in your browser session and are never saved on our servers.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="anthropic-key">Anthropic API Key</label>
            <div className="input-wrapper">
              <input
                type={showKeys ? "text" : "password"}
                id="anthropic-key"
                value={anthropicKey}
                onChange={(e) => setAnthropicKey(e.target.value)}
                placeholder="sk-ant-..."
                required
              />
            </div>
            <span className="input-hint">
              Get your key from{" "}
              <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer">
                console.anthropic.com
              </a>
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="openai-key">OpenAI API Key</label>
            <div className="input-wrapper">
              <input
                type={showKeys ? "text" : "password"}
                id="openai-key"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-..."
                required
              />
            </div>
            <span className="input-hint">
              Get your key from{" "}
              <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
                platform.openai.com
              </a>
            </span>
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={showKeys}
                onChange={(e) => setShowKeys(e.target.checked)}
              />
              Show API keys
            </label>
          </div>

          <div className="modal-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!isValid}
            >
              Save and Continue
            </button>
          </div>
        </form>

        <div className="modal-footer">
          <p>
            Your keys are used only to make API calls and are stored temporarily in your browser.
            They are cleared when you close this tab.
          </p>
        </div>
      </div>
    </div>
  );
}
