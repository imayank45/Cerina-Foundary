import React, { useState } from "react";
import { useProtocolGenerator } from "../hooks/useProtocolGenerator";
import InputForm from "./InputForm";
import AgentTimeline from "./AgentTimeline";
import DraftViewer from "./DraftViewer";
import SafetyFlagsPanel from "./SafetyFlagsPanel";
import ClinicalFeedbackPanel from "./ClinicalFeedbackPanel";
import HumanApprovalModal from "./HumanApprovalModal";
import "../App.css";
import ReactMarkdown from "react-markdown";

export default function ProtocolGenerator() {
  const { state, loading, error, generate, approve } = useProtocolGenerator();
  const [showApprovalModal, setShowApprovalModal] = useState(false);

  const handleGenerateClick = (intent: string, query: string) => {
    generate(intent, query);
  };

  const handleApprove = (edits: string) => {
    if (state) {
      approve(state.thread_id, edits);
      setShowApprovalModal(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🏥 Cerina Protocol Foundry</h1>
        <p>Autonomous Multi-Agent CBT Exercise Generation</p>
      </header>

      <main className="app-main">
        {!state && <InputForm onGenerate={handleGenerateClick} />}

        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Agents are collaborating...</p>
            <p className="sub-text">Drafting → Safety Review → Clinical Review</p>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        {state && (
          <div className="protocol-view">
            <div className="view-left">
              <AgentTimeline notes={state.agent_notes} />
            </div>

            <div className="view-right">
              <DraftViewer draft={state.current_draft} />
              <SafetyFlagsPanel flags={state.safety_flags} score={state.safety_score} />
              <ClinicalFeedbackPanel
                feedback={state.clinical_feedback}
                empathyScore={state.empathy_score}
              />
            </div>
          </div>
        )}

        {state && state.status === "halted" && (
          <div className="action-bar">
            <button
              onClick={() => setShowApprovalModal(true)}
              className="btn btn-primary btn-large"
            >
              Review & Approve Protocol
            </button>
          </div>
        )}

        {showApprovalModal && state && (
          <HumanApprovalModal
            draft={state.current_draft}
            onApprove={handleApprove}
            onCancel={() => setShowApprovalModal(false)}
          />
        )}

        {state?.status === "finalized" && (
          <div className="final-view">
            <h2>✨ Final Protocol (Ready for Client)</h2>
            <div className="final-content">
              <ReactMarkdown>{state.current_draft}</ReactMarkdown>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
