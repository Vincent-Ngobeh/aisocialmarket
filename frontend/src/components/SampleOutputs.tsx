import { Link } from "react-router-dom";
import { sampleCampaigns } from "../data/sampleCampaigns";
import { CopyCard } from "./CampaignResults";

export default function SampleOutputs() {
  return (
    <div className="sample-outputs">
      <div className="sample-outputs-header">
        <h2>Sample Campaign Outputs</h2>
        <p>
          See the quality of AI-generated campaigns before you try it yourself.
          These are real examples produced by our tool for UK businesses.
        </p>
        <Link to="/" className="btn btn-primary">
          Try It Yourself
        </Link>
      </div>

      <div className="sample-campaigns-list">
        {sampleCampaigns.map((campaign, index) => (
          <div key={index} className="sample-campaign-card">
            <div className="sample-campaign-header">
              <h3>{campaign.business_name}</h3>
            </div>

            <div className="copies-section">
              <h4>Generated Social Media Copy</h4>
              <div className="copies-grid">
                {campaign.copies.map((copy, copyIndex) => (
                  <CopyCard key={copyIndex} platformCopy={copy} />
                ))}
              </div>
            </div>

            {campaign.image_prompt && (
              <div className="sample-image-prompt">
                <h4>Generated Image Prompt</h4>
                <p className="image-prompt">
                  {campaign.image_prompt}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="sample-outputs-footer">
        <p>Ready to create your own campaign?</p>
        <Link to="/" className="btn btn-primary">
          Get Started
        </Link>
      </div>
    </div>
  );
}
