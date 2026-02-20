import { useState, useEffect } from "react";
import type { ApiKeys, FreeTierStatus } from "../types/auth";
import { getFreeTierStatus } from "../services/api";

interface ApiKeyModalProps {
  onSave: (keys: ApiKeys) => void;
  onTryFree: () => void;
  initialKeys?: ApiKeys | null;
}

function validateAnthropicKey(key: string): boolean {
  return /^sk-ant-[a-zA-Z0-9-_]{20,}$/.test(key);
}

function validateOpenAIKey(key: string): boolean {
  return /^sk-[a-zA-Z0-9-_]{20,}$/.test(key);
}

export default function ApiKeyModal({ onSave, onTryFree, initialKeys }: ApiKeyModalProps) {
  const [anthropicKey, setAnthropicKey] = useState(initialKeys?.anthropicKey || "");
  const [openaiKey, setOpenaiKey] = useState(initialKeys?.openaiKey || "");
  const [showKeys, setShowKeys] = useState(false);
  const [errors, setErrors] = useState<{ anthropic?: string; openai?: string }>({});
  const [freeTierStatus, setFreeTierStatus] = useState<FreeTierStatus | null>(null);
  const [freeTierLoading, setFreeTierLoading] = useState(true);

  useEffect(() => {
    getFreeTierStatus()
      .then(setFreeTierStatus)
      .catch(() => setFreeTierStatus(null))
      .finally(() => setFreeTierLoading(false));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: { anthropic?: string; openai?: string } = {};

    if (!validateAnthropicKey(anthropicKey)) {
      newErrors.anthropic = "Invalid format. Key should start with 'sk-ant-'";
    }

    if (!validateOpenAIKey(openaiKey)) {
      newErrors.openai = "Invalid format. Key should start with 'sk-'";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    onSave({ anthropicKey, openaiKey });
  };

  const isValid = anthropicKey.length > 0 && openaiKey.length > 0;
  const hasFreeGenerations = freeTierStatus !== null && freeTierStatus.remaining > 0;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Get Started</h2>

        {!freeTierLoading && hasFreeGenerations && (
          <div className="free-tier-section">
            <div className="free-tier-badge">
              {freeTierStatus!.remaining} of {freeTierStatus!.limit} free generations remaining today
            </div>
            <p className="free-tier-description">
              Try the app instantly — no API keys needed. Generate full campaigns
              with copy and images, completely free.
            </p>
            <button
              type="button"
              className="btn btn-primary btn-free-tier"
              onClick={onTryFree}
            >
              Try Free
            </button>
            <div className="modal-divider">
              <span>or use your own keys</span>
            </div>
          </div>
        )}

        {!freeTierLoading && !hasFreeGenerations && freeTierStatus !== null && (
          <div className="free-tier-exhausted">
            <p>
              You've used all {freeTierStatus.limit} free generations for today.
              Enter your own API keys to continue, or try again tomorrow.
            </p>
          </div>
        )}

        <p className="modal-description">
          Enter your own API keys for unlimited generations.
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
                onChange={(e) => {
                  setAnthropicKey(e.target.value);
                  setErrors((prev) => ({ ...prev, anthropic: undefined }));
                }}
                placeholder="sk-ant-..."
                required
              />
            </div>
            {errors.anthropic && (
              <span className="input-error">{errors.anthropic}</span>
            )}
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
                onChange={(e) => {
                  setOpenaiKey(e.target.value);
                  setErrors((prev) => ({ ...prev, openai: undefined }));
                }}
                placeholder="sk-..."
                required
              />
            </div>
            {errors.openai && (
              <span className="input-error">{errors.openai}</span>
            )}
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
