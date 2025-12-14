import React, { useState } from "react";
import "../App.css";

interface HumanApprovalModalProps {
  draft: string;
  onApprove: (edits: string) => void;
  onCancel: () => void;
}

export default function HumanApprovalModal({
  draft,
  onApprove,
  onCancel,
}: HumanApprovalModalProps) {
  const [edits, setEdits] = useState(draft);

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Review & Approve Protocol</h2>
        <textarea
          value={edits}
          onChange={(e) => setEdits(e.target.value)}
          className="modal-textarea"
          placeholder="Make any edits to the draft..."
        />
        <div className="modal-buttons">
          <button onClick={onCancel} className="btn btn-secondary">
            Cancel
          </button>
          <button onClick={() => onApprove(edits)} className="btn btn-success">
            Approve & Finalize
          </button>
        </div>
      </div>
    </div>
  );
}
