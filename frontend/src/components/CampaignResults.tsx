import type { CampaignResponse, PlatformCopy } from "../types/campaign";

interface CampaignResultsProps {
  result: CampaignResponse;
  onReset: () => void;
}

export function CopyCard({ platformCopy }: { platformCopy: PlatformCopy }) {
  const handleCopy = async () => {
    await navigator.clipboard.writeText(platformCopy.content);
  };

  return (
    <div className="copy-card">
      <div className="copy-card-header">
        <h3>{platformCopy.platform}</h3>
        <span className="char-count">{platformCopy.character_count} characters</span>
      </div>
      <div className="copy-content">
        <p>{platformCopy.content}</p>
      </div>
      <button className="btn btn-secondary btn-small" onClick={handleCopy}>
        Copy to Clipboard
      </button>
    </div>
  );
}

export default function CampaignResults({ result, onReset }: CampaignResultsProps) {
  return (
    <div className="campaign-results">
      <div className="results-header">
        <h2>Your campaign is ready!</h2>
        <button className="btn btn-secondary" onClick={onReset}>
          Create Another
        </button>
      </div>

      {result.image_url && (
        <div className="image-section">
          <h3>Your Campaign Image</h3>
          <div className="generated-image">
            <img src={result.image_url} alt="Generated campaign image" />
          </div>
          <p className="image-prompt">
            <strong>Image prompt:</strong> {result.revised_image_prompt || result.image_prompt}
          </p>
        </div>
      )}

      <div className="copies-section">
        <h3>Your Social Media Copy</h3>
        <div className="copies-grid">
          {result.copies.map((copy, index) => (
            <CopyCard key={index} platformCopy={copy} />
          ))}
        </div>
      </div>

      {result.message && (
        <p className="result-message">{result.message}</p>
      )}
    </div>
  );
}
