import React from "react";
import ReactMarkdown from "react-markdown";
import "../App.css";

interface DraftViewerProps {
  draft: string;
}

export default function DraftViewer({ draft }: DraftViewerProps) {
  return (
    <div className="draft-container">
      <h3>Current Draft</h3>
      <div className="draft-content">
        {draft ? (
          <ReactMarkdown>{draft}</ReactMarkdown>
        ) : (
          <p className="placeholder">Generating...</p>
        )}
      </div>
    </div>
  );
}
