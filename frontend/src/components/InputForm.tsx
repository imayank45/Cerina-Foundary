import React, { useState } from "react";
import "../App.css";

interface InputFormProps {
  onGenerate: (intent: string, query: string) => void;
}

export default function InputForm({ onGenerate }: InputFormProps) {
  const [intent, setIntent] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (intent.trim()) {
      onGenerate(intent, intent);
      setIntent("");
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit} className="input-form">
        <h2>Generate CBT Exercise Protocol</h2>
        
        <div className="form-group">
          <label htmlFor="intent">Therapeutic Goal:</label>
          <textarea
            id="intent"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="e.g., 'Create an exposure hierarchy for agoraphobia' or 'Develop a sleep hygiene protocol'"
            rows={4}
            className="form-input"
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={!intent.trim()}>
          Generate Protocol
        </button>

        <div className="examples">
          <h3>Examples:</h3>
          <ul>
            <li>Exposure hierarchy for social anxiety</li>
            <li>Sleep hygiene protocol for insomnia</li>
            <li>Thought record template for depression</li>
            <li>Behavioral activation exercise for low mood</li>
          </ul>
        </div>
      </form>
    </div>
  );
}
