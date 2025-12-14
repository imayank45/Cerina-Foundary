import React from "react";
import "../App.css";
import ReactMarkdown from "react-markdown";

interface ClinicalFeedbackPanelProps {
  feedback: string;
  empathyScore: number;
}

export default function ClinicalFeedbackPanel({
  feedback,
  empathyScore,
}: ClinicalFeedbackPanelProps) {
  return (
    <div className="clinical-panel">
      <div className="panel-header">
        <h3>Clinical Review</h3>
        <span className={`score score-${Math.round(empathyScore / 25)}`}>
          {Math.round(empathyScore)}/100
        </span>
      </div>
      <div className="feedback-content">
        {feedback ? (
          <ReactMarkdown>{feedback}</ReactMarkdown>
        ) : (
          <p className="placeholder">Reviewing...</p>
        )}
      </div>
    </div>
  );
}
