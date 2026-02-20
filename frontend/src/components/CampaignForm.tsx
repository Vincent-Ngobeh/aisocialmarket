import { useState } from "react";
import type { CampaignBrief } from "../types/campaign";
import {
  AVAILABLE_PLATFORMS,
  TONE_OPTIONS,
  UK_SEASONAL_HOOKS,
} from "../types/campaign";

interface CampaignFormProps {
  onSubmit: (brief: CampaignBrief, generateImage: boolean) => void;
  isLoading: boolean;
}

const initialFormState: CampaignBrief = {
  business_name: "",
  business_type: "",
  target_audience: "",
  campaign_goal: "",
  key_messages: "",
  tone: "friendly and professional",
  platforms: ["Instagram", "Facebook"],
  include_hashtags: true,
  include_emoji: true,
  seasonal_hook: null,
};

export default function CampaignForm({ onSubmit, isLoading }: CampaignFormProps) {
  const [formData, setFormData] = useState<CampaignBrief>(initialFormState);
  const [step, setStep] = useState(1);
  const [generateImage, setGenerateImage] = useState(false);
  const totalSteps = 3;

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handlePlatformToggle = (platform: string) => {
    setFormData((prev) => {
      const platforms = prev.platforms.includes(platform)
        ? prev.platforms.filter((p) => p !== platform)
        : [...prev.platforms, platform];
      return { ...prev, platforms };
    });
  };

  const handleSeasonalChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFormData((prev) => ({
      ...prev,
      seasonal_hook: value === "" ? null : value,
    }));
  };

  const handleNext = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handleBack = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (step === totalSteps && canProceed()) {
      onSubmit(formData, generateImage);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.business_name && formData.business_type && formData.target_audience;
      case 2:
        return formData.campaign_goal && formData.key_messages;
      case 3:
        return formData.platforms.length > 0;
      default:
        return false;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="campaign-form">
      <div className="step-indicator">
        {Array.from({ length: totalSteps }, (_, i) => (
          <div
            key={i}
            className={`step-dot ${i + 1 <= step ? "active" : ""}`}
            onClick={() => i + 1 < step && setStep(i + 1)}
          />
        ))}
      </div>

      {step === 1 && (
        <div className="form-step">
          <h2>Tell us about your business</h2>

          <div className="form-group">
            <label htmlFor="business_name">Business Name</label>
            <input
              type="text"
              id="business_name"
              name="business_name"
              value={formData.business_name}
              onChange={handleInputChange}
              placeholder="e.g. The Corner Bakery"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="business_type">What type of business is it?</label>
            <input
              type="text"
              id="business_type"
              name="business_type"
              value={formData.business_type}
              onChange={handleInputChange}
              placeholder="e.g. Independent bakery and cafe"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="target_audience">Who are your customers?</label>
            <textarea
              id="target_audience"
              name="target_audience"
              value={formData.target_audience}
              onChange={handleInputChange}
              placeholder="e.g. Local families and office workers in Manchester"
              rows={3}
              required
            />
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="form-step">
          <h2>What would you like to promote?</h2>

          <div className="form-group">
            <label htmlFor="campaign_goal">Campaign Goal</label>
            <textarea
              id="campaign_goal"
              name="campaign_goal"
              value={formData.campaign_goal}
              onChange={handleInputChange}
              placeholder="e.g. Promote our new afternoon tea menu for spring"
              rows={3}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="key_messages">Key Messages</label>
            <textarea
              id="key_messages"
              name="key_messages"
              value={formData.key_messages}
              onChange={handleInputChange}
              placeholder="e.g. Locally sourced ingredients, traditional recipes, book online for 10% off"
              rows={4}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="seasonal_hook">Seasonal Hook (Optional)</label>
            <select
              id="seasonal_hook"
              name="seasonal_hook"
              value={formData.seasonal_hook || ""}
              onChange={handleSeasonalChange}
            >
              <option value="">None</option>
              {UK_SEASONAL_HOOKS.map((hook) => (
                <option key={hook} value={hook}>
                  {hook}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="form-step">
          <h2>Customise your content</h2>

          <div className="form-group">
            <label htmlFor="tone">Tone of Voice</label>
            <select
              id="tone"
              name="tone"
              value={formData.tone}
              onChange={handleInputChange}
            >
              {TONE_OPTIONS.map((tone) => (
                <option key={tone} value={tone}>
                  {tone.charAt(0).toUpperCase() + tone.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label id="platforms-label">Which platforms do you need?</label>
            <div className="platform-grid" role="group" aria-labelledby="platforms-label">
              {AVAILABLE_PLATFORMS.map((platform) => (
                <button
                  key={platform}
                  type="button"
                  className={`platform-btn ${
                    formData.platforms.includes(platform) ? "selected" : ""
                  }`}
                  onClick={() => handlePlatformToggle(platform)}
                >
                  {platform}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group checkbox-group">
            <label htmlFor="include_hashtags">
              <input
                type="checkbox"
                id="include_hashtags"
                name="include_hashtags"
                checked={formData.include_hashtags}
                onChange={handleInputChange}
              />
              Include hashtags
            </label>

            <label htmlFor="include_emoji">
              <input
                type="checkbox"
                id="include_emoji"
                name="include_emoji"
                checked={formData.include_emoji}
                onChange={handleInputChange}
              />
              Include emojis
            </label>
          </div>

          <div className="form-group checkbox-group">
            <label htmlFor="generate_image">
              <input
                type="checkbox"
                id="generate_image"
                checked={generateImage}
                onChange={(e) => setGenerateImage(e.target.checked)}
              />
              Generate promotional image (takes longer)
            </label>
          </div>
        </div>
      )}

      <div className="form-actions">
        {step > 1 && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleBack}
            disabled={isLoading}
          >
            Back
          </button>
        )}

        {step < totalSteps ? (
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleNext}
            disabled={!canProceed()}
          >
            Continue
          </button>
        ) : (
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !canProceed()}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner"></span>
                Generating...
              </>
            ) : (
              "Generate Campaign"
            )}
          </button>
        )}
      </div>
    </form>
  );
}
