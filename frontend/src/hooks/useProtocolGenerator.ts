// import { useState } from "react";
// import axios from "axios";
// import { ProtocolState, ProtocolResponse, ApprovalResponse } from "../types";

// const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

// export function useProtocolGenerator() {
//   const [state, setState] = useState<ProtocolState | null>(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");

//   const generate = async (userIntent: string, originalQuery: string) => {
//     setLoading(true);
//     setError("");
//     try {
//       const response = await axios.post(`${API_BASE}/generate`, {
//         user_intent: userIntent,
//         original_query: originalQuery,
//       });
      
//       const data = response.data as ProtocolResponse;
//       setState({
//         thread_id: data.thread_id,
//         status: data.status,
//         current_draft: data.current_draft,
//         safety_flags: data.safety_flags,
//         clinical_feedback: data.clinical_feedback,
//         empathy_score: data.empathy_score,
//         safety_score: data.safety_score,
//         agent_notes: data.agent_notes,
//         iteration_count: data.iteration_count,
//       });
//     } catch (err: any) {
//       const errorMsg = err.response?.data?.detail || "Generation failed";
//       setError(errorMsg);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const approve = async (threadId: string, edits: string = "") => {
//     setLoading(true);
//     try {
//       const response = await axios.post(`${API_BASE}/approve`, {
//         thread_id: threadId,
//         human_approval: true,
//         human_edits: edits,
//       });

//       const data = response.data as ApprovalResponse;
//       setState((prev) => 
//         prev ? {
//           ...prev,
//           status: data.status,
//           current_draft: data.final_protocol,
//         } : null
//       );
//     } catch (err: any) {
//       const errorMsg = err.response?.data?.detail || "Approval failed";
//       setError(errorMsg);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return { state, loading, error, generate, approve };
// }


import { useState } from "react";
import axios from "axios";
import { ProtocolState, ProtocolResponse, ApprovalResponse } from "../types";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export function useProtocolGenerator() {
  const [state, setState] = useState<ProtocolState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async (userIntent: string, originalQuery: string) => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.post<ProtocolResponse>(`${API_BASE}/generate`, {
        user_intent: userIntent,
        original_query: originalQuery,
      });

      const data = response.data;
      console.log("GENERATE response:", data);

      // Direct 1:1 mapping
      const nextState: ProtocolState = {
        thread_id: data.thread_id,
        status: data.status as ProtocolState["status"],
        current_draft: data.current_draft,
        safety_flags: data.safety_flags,
        clinical_feedback: data.clinical_feedback,
        empathy_score: data.empathy_score,
        safety_score: data.safety_score,
        agent_notes: data.agent_notes,
        iteration_count: data.iteration_count,
      };

      setState(nextState);
    } catch (err: any) {
      console.error("GENERATE error:", err);
      const errorMsg = err.response?.data?.detail || "Generation failed";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const approve = async (threadId: string, edits: string = "") => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.post<ApprovalResponse>(`${API_BASE}/approve`, {
        thread_id: threadId,
        human_approval: true,
        human_edits: edits,
      });

      const data = response.data;
      console.log("APPROVE response:", data);

      setState((prev) =>
        prev
          ? {
              ...prev,
              status: data.status as ProtocolState["status"],
              current_draft: data.final_protocol,
            }
          : null
      );
    } catch (err: any) {
      console.error("APPROVE error:", err);
      const errorMsg = err.response?.data?.detail || "Approval failed";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return { state, loading, error, generate, approve };
}
