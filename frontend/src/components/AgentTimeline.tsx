import React from "react";
import "../App.css";

interface AgentTimelineProps {
  notes: Record<string, string[]>;
}

export default function AgentTimeline({ notes }: AgentTimelineProps) {
  const agents = ["supervisor", "drafter", "safety_guardian", "clinical_critic", "synthesizer"];
  
  const agentLabels: Record<string, string> = {
    supervisor: "Supervisor",
    drafter: "Drafter",
    safety_guardian: "Safety Guardian",
    clinical_critic: "Clinical Critic",
    synthesizer: "Synthesizer",
  };

  return (
    <div className="timeline-container">
      <h3>Agent Execution Timeline</h3>
      <div className="timeline">
        {agents.map((agent, idx) => (
          <div key={agent} className="timeline-item">
            <div className="timeline-marker">
              <span className="step-number">{idx + 1}</span>
            </div>
            <div className="timeline-content">
              <h4>{agentLabels[agent]}</h4>
              {notes[agent]?.length ? (
                <ul className="notes-list">
                  {notes[agent].map((note, i) => (
                    <li key={i}>{note}</li>
                  ))}
                </ul>
              ) : (
                <p className="pending">Pending...</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
