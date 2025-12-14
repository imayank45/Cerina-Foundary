# 🏥 Cerina Protocol Foundry

**Autonomous Multi-Agent System for CBT Exercise Generation**

A production-ready full-stack application demonstrating advanced AI engineering patterns: multi-agent orchestration, human-in-the-loop workflows, real-time collaboration, and safety-first design.

---

## 🎯 Project Overview

Cerina Protocol Foundry autonomously designs Cognitive Behavioral Therapy (CBT) exercises through a coordinated multi-agent workflow. Given a therapeutic goal, the system drafts, validates, refines, and finalizes clinical-grade protocols—all while maintaining safety guardrails and requiring human approval at critical points.

**Live Demo**: `localhost:3000` (after setup)

---

## ✨ Key Features

### 🤖 Multi-Agent Orchestration
- **5 Specialized Agents**: Supervisor, Drafter, Safety Guardian, Clinical Critic, Synthesizer
- **LangGraph StateGraph**: Deterministic pipeline with conditional routing and autonomous looping
- **Shared Blackboard**: Rich state propagation across agents via `CerinasState`
- **Automatic Self-Correction**: Agents iterate up to 3 times, fixing safety/clinical issues

### 🛡️ Safety-First Architecture
- **Safety Guardian Agent**: Audits every draft for harmful content, self-harm signals, victim-blaming language
- **Critical Safety Halting**: Pauses workflow immediately if critical issues detected
- **Empathy Scoring**: Clinical Critic evaluates warmth, tone, and psychological appropriateness
- **Human Approval Gate**: All protocols require explicit human review before finalization

### 👥 Human-in-the-Loop
- **Approval Modal**: Reviewers can edit drafts before finalization
- **Real-Time Timeline**: Watch agents execute with detailed notes
- **Edit Preservation**: Human modifications are incorporated and persisted
- **Audit Trail**: Complete history of iterations, notes, and decisions

### 🏗️ Production-Ready Stack
- **Backend**: FastAPI + LangGraph + SQLAlchemy + SQLite checkpointing
- **Frontend**: React 18 + TypeScript + Axios
- **Interop**: MCP (Model Context Protocol) server for Claude Desktop integration
- **Persistence**: SQLite for protocols + SqliteSaver for LangGraph checkpoints

---

## 📁 Project Structure

```
cerina_foundry/
├── backend/
│   ├── agents/
│   │   ├── supervisor.py          # Orchestrator, routing decisions
│   │   ├── drafter.py             # Exercise generation
│   │   ├── safety_guardian.py      # Safety auditing
│   │   ├── clinical_critic.py      # Empathy & tone evaluation
│   │   └── synthesizer.py          # Final polishing
│   ├── main.py                    # FastAPI app, endpoints
│   ├── graph.py                   # LangGraph compilation
│   ├── state.py                   # CerinasState definition
│   ├── database.py                # SQLAlchemy ORM, persistence
│   ├── mcp_server.py              # MCP integration
│   └── utils.py                   # Utilities
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProtocolGenerator.tsx    # Main container
│   │   │   ├── InputForm.tsx            # User input
│   │   │   ├── AgentTimeline.tsx        # Agent execution timeline
│   │   │   ├── DraftViewer.tsx          # Draft display
│   │   │   ├── SafetyFlagsPanel.tsx     # Safety review
│   │   │   ├── ClinicalFeedbackPanel.tsx # Empathy scoring
│   │   │   ├── HumanApprovalModal.tsx   # Edit & approve modal
│   │   │   └── FinalProtocolView.tsx    # Final output
│   │   ├── hooks/
│   │   │   └── useProtocolGenerator.ts  # API integration hook
│   │   ├── types/
│   │   │   └── index.ts           # TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── App.css                # Responsive design system
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── ARCHITECTURE.md                # Detailed technical design
├── README.md                       # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Config template
└── setup.sh                       # One-command setup

```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- `ANTHROPIC_API_KEY` from https://console.anthropic.com/

### Quick Setup (One Command)

```bash
chmod +x setup.sh
./setup.sh
```

Or manual setup:

```bash
# Backend
python -m venv cerina_env
source cerina_env/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..

# Environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### Running

**Terminal 1: Backend**
```bash
source cerina_env/bin/activate
python -m backend.main
# Backend: http://localhost:8000
```

**Terminal 2: Frontend**
```bash
cd frontend && npm start
# Frontend: http://localhost:3000
```

**Terminal 3 (Optional): MCP Server**
```bash
source cerina_env/bin/activate
python -m backend.mcp_server
```

---

## 💡 How It Works

### End-to-End Flow

1. **User Input** → Enter therapeutic goal in React UI
2. **Graph Execution** → LangGraph orchestrates 5 agents in sequence
3. **Autonomous Refinement** → Agents iterate up to 3 times, self-correcting
4. **Safety Halt** → System stops for human review when safe (no critical issues)
5. **Human Approval** → Reviewer edits draft and approves
6. **Synthesis** → Final agent polishes for client delivery
7. **Persistence** → Protocol saved with full audit trail

### Agent Responsibilities

| Agent | Input | Process | Output |
|-------|-------|---------|--------|
| **Supervisor** | Intent + feedback | Parse intent, decide loop/halt, aggregate notes | Routing decision, status |
| **Drafter** | Intent + flags + feedback | Generate evidence-based CBT exercise | `current_draft`, version history |
| **Safety Guardian** | Draft | Audit for harm, self-harm signals, victim-blaming | `safety_flags`, `safety_score` |
| **Clinical Critic** | Draft + intent | Evaluate empathy, warmth, tone, CBT alignment | `empathy_score`, `clinical_feedback` |
| **Synthesizer** | Approved draft + edits | Polish, format, add affirmations | `final_protocol` (client-ready) |

### Key Metrics

- **Safety Score** (0-100): Freedom from harmful content
- **Empathy Score** (0-100): Warmth, supportiveness, non-judgmental tone
- **Iterations**: Number of self-correction cycles (capped at 3)
- **Issues Found**: Count of identified safety/clinical problems

---

## 🔌 API Endpoints

### `POST /generate`
Trigger protocol generation.

**Request:**
```json
{
  "user_intent": "Behavioral activation exercise for low mood",
  "original_query": "..."
}
```

**Response:**
```json
{
  "thread_id": "abc123...",
  "status": "halted",
  "current_draft": "...",
  "safety_flags": [{"line": 0, "severity": "low", "issue": "...", "suggestion": "..."}],
  "clinical_feedback": "...",
  "empathy_score": 82.0,
  "safety_score": 95.0,
  "agent_notes": {"supervisor": ["..."], "drafter": ["..."], ...},
  "iteration_count": 2
}
```

### `POST /approve`
Approve and finalize the protocol.

**Request:**
```json
{
  "thread_id": "abc123...",
  "human_approval": true,
  "human_edits": "Optional edits to draft..."
}
```

**Response:**
```json
{
  "thread_id": "abc123...",
  "status": "finalized",
  "final_protocol": "..."
}
```

### `GET /protocol/{thread_id}`
Retrieve a specific protocol.

### `GET /protocols?limit=10`
List recent protocols.

### `GET /health`
Health check.

---

## 🔗 MCP Integration

Use as a tool in Claude Desktop or compatible MCP clients.

**Config** (`~/.claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "cerina-foundry": {
      "command": "python",
      "args": ["/full/path/to/backend/mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-..."
      }
    }
  }
}
```

**Usage in Claude:**
```
@cerina-foundry
Generate a sleep hygiene protocol for someone with insomnia
```

---

## 🎨 Tech Stack

### Backend
- **FastAPI**: Modern async REST framework
- **LangGraph**: Agent orchestration & conditional routing
- **SQLAlchemy**: ORM for persistence
- **Pydantic**: Data validation
- **Claude 3.5 Sonnet**: LLM backbone for all agents

### Frontend
- **React 18**: Modern UI with hooks
- **TypeScript**: Type-safe state & props
- **Axios**: HTTP client
- **React Markdown**: Draft rendering
- **CSS3**: Responsive design, dark mode support

### Infrastructure
- **SQLite**: Local persistence (easily swappable for PostgreSQL)
- **SqliteSaver**: LangGraph checkpointing for stateful workflows
- **CORS**: Frontend-backend isolation

---

## 📊 Performance & Metrics

- **Generation Time**: ~40-60 seconds (3 Claude API calls per iteration)
- **Database Queries**: <100ms (SQLite)
- **API Response**: <50ms (excluding LLM latency)
- **Token Usage**: ~5,000 tokens per full protocol
- **Concurrent Users**: Single-threaded (easily scalable with async workers)

---

## 🔒 Security & Safety

- ✅ **Input Validation**: Pydantic models enforce types
- ✅ **Safety Guardrails**: Dedicated Safety Guardian agent
- ✅ **Human Approval**: All protocols require explicit review
- ✅ **Audit Trail**: Every iteration logged with timestamps
- ✅ **No Storage APIs**: Avoids browser storage for clinical data
- ✅ **CORS Whitelist**: Only explicit localhost origins

---

## 🧪 Testing & Examples

### Supported CBT Exercise Types
- Exposure hierarchies (anxiety, phobias)
- Sleep hygiene protocols (insomnia)
- Thought records (depression, anxiety)
- Behavioral activation (low mood)
- Problem-solving (stress management)
- Values clarification exercises

### Example Prompts
```
"Create an exposure hierarchy for social anxiety"
"Sleep hygiene protocol for chronic insomnia"
"Thought record template for catastrophizing"
"Behavioral activation plan for depression"
```

---

## 📈 Future Enhancements

- [ ] Multi-language support (Spanish, Mandarin, Hindi)
- [ ] User authentication & protocol libraries
- [ ] Real-time streaming updates (Server-Sent Events)
- [ ] Additional agents (Domain Expert, Patient Advocate)
- [ ] EHR integration hooks
- [ ] Mobile-responsive UI improvements
- [ ] Vector DB for protocol templates
- [ ] Admin dashboard for metrics

---

## 🏆 Why This Project Matters

This project demonstrates mastery of:

1. **Multi-Agent Orchestration**: Complex state management across 5 autonomous agents
2. **Safety-Critical Design**: Guardrails, approval gates, and harm prevention
3. **Human-in-the-Loop AI**: Balancing autonomy with human oversight
4. **Full-Stack Engineering**: Backend (Python/LangGraph), Frontend (React/TS), DevOps
5. **Production Patterns**: Checkpointing, error handling, logging, persistence
6. **UX for AI**: Real-time feedback, transparency, user control
7. **Scalable Architecture**: Stateful workflows, horizontal resilience, clean separation of concerns

---

## 📚 Technical Highlights

### State Management
- **Blackboard Pattern**: All agents read/write to shared `CerinasState`
- **Type Safety**: Pydantic validates state at every transition
- **Immutability**: Each agent outputs a new state instance

### Agent Autonomy
- **Conditional Routing**: Supervisor decides loop vs. halt based on state
- **Self-Correction**: Agents iterate, fixing issues without human intervention
- **Bounded Loops**: Max 3 iterations prevents infinite loops

### Persistence
- **Dual Storage**: SQLite for protocols, SqliteSaver for graph checkpoints
- **Upsert Pattern**: `save_protocol()` handles inserts and updates atomically
- **Thread ID Binding**: All data tied to unique protocol thread ID

---

## 🎓 Learning Outcomes

By studying this codebase, you'll learn:

- How to architect multi-agent systems with LangGraph
- How to implement safety-first AI workflows
- How to build full-stack AI applications (FastAPI + React)
- How to integrate LLMs into production systems
- How to handle stateful, long-running agent workflows
- How to balance autonomous behavior with human control

---

## 📞 Support & Contribution

For issues or questions:

1. Check the `ARCHITECTURE.md` for detailed system design
2. Review agent implementations in `backend/agents/`
3. Inspect state schema in `backend/state.py`
4. Check database logic in `backend/database.py`

---

## 📄 License

This is a portfolio project showcasing AI engineering capabilities.

---

**Built with**: 🐍 Python • ⚡ LangGraph • ⚛️ React • 🤖 Claude AI • 🗄️ SQLite

**Author**: Mayank Kathane  
**Date**: December 2025  
**Status**: Production Ready
