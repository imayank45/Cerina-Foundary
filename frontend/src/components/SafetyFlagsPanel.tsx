import React from "react";
import { SafetyFlag } from "../types";
import "../App.css";

interface SafetyFlagsPanelProps {
  flags: SafetyFlag[];
  score: number;
}

export default function SafetyFlagsPanel({
  flags,
  score,
}: SafetyFlagsPanelProps) {
  const severityColor = (sev: string): string => {
    if (sev === "critical") return "critical";
    if (sev === "moderate") return "moderate";
    return "low";
  };

  return (
    <div className="safety-panel">
      <div className="panel-header">
        <h3>Safety Review</h3>
        <span className={`score score-${Math.round(score / 25)}`}>
          {Math.round(score)}/100
        </span>
      </div>
      <div className="flags-list">
        {flags.length === 0 ? (
          <p className="success">✓ No safety issues detected</p>
        ) : (
          flags.map((flag, idx) => (
            <div key={idx} className={`flag flag-${severityColor(flag.severity)}`}>
              <div className="flag-title">{flag.issue}</div>
              <div className="flag-suggestion">→ {flag.suggestion}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
