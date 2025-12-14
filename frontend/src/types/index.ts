// export interface SafetyFlag {
//   line: number;
//   severity: "critical" | "moderate" | "low";
//   issue: string;
//   suggestion: string;
// }

// export interface ProtocolState {
//   thread_id: string;
//   status: "drafting" | "safety_review" | "clinical_review" | "halted" | "finalized";
//   current_draft: string;
//   safety_flags: SafetyFlag[];
//   clinical_feedback: string;
//   empathy_score: number;
//   safety_score: number;
//   agent_notes: Record<string, string[]>;
//   iteration_count: number;
// }

// export interface ProtocolResponse {
//   thread_id: string;
//   status: string;
//   current_draft: string;
//   safety_flags: SafetyFlag[];
//   clinical_feedback: string;
//   empathy_score: number;
//   safety_score: number;
//   agent_notes: Record<string, string[]>;
//   iteration_count: number;
// }

// export interface ApprovalResponse {
//   thread_id: string;
//   status: string;
//   final_protocol: string;
// }


export interface SafetyFlag {
  line: number;
  severity: "critical" | "moderate" | "low";
  issue: string;
  suggestion: string;
}

export interface ProtocolState {
  thread_id: string;
  status: "drafting" | "safety_review" | "clinical_review" | "halted" | "finalized";
  current_draft: string;
  safety_flags: SafetyFlag[];
  clinical_feedback: string;
  empathy_score: number;
  safety_score: number;
  agent_notes: Record<string, string[]>;
  iteration_count: number;
}

export interface ProtocolResponse extends ProtocolState {}  // simplify

export interface ApprovalResponse {
  thread_id: string;
  status: string;
  final_protocol: string;
}
