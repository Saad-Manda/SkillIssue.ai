# SkillIssue.ai - AI Interviewer Orchestration

SkillIssue.ai is an advanced AI-powered mock interviewer that conducts realistic, adaptive interview sessions based on a candidate's profile and a specific Job Description (JD). It utilizes a multi-agent orchestration framework to evaluate user performance across a wide range of technical and behavioral parameters.

## Architecture Overview

The system employs a **Dual-State Architecture** to balance performance and persistent storage requirements during complex multi-agent workflows.

- **SystemState (Pydantic)**: A lightweight state used for in-session action tracking. It stores the current user, JD, current turn, current phase, and the interview plan. This state ensures fast graph execution and propagation within the orchestration.
- **SessionState (Redis)**: Manages heavy data such as full chat history and cumulative phase summaries. Redis is used for high-speed asynchronous retrieval of these artifacts at any point in the interview lifecycle.

---

## Multi-Agent Orchestration

SkillIssue.ai is powered by a suite of specialized agents, each with a focused responsibility:

### 1. User Summarizer
- **Input**: User Profile Data
- **Output**: Detailed User Summary
- **Role**: Analyzes the candidate's background to provide a contextual foundation for the interview.

### 2. Planner
- **Input**: User Summary, Job Description
- **Output**: Hierarchical Interview Plan (Phases → Topics)
- **Role**: Generates an exhaustive plan tailored to the JD against the candidate's achievements. Topics are designed to be independent but collectively cover the required expertise.

### 3. Router
- **Input**: Phase Summary, Chat History
- **Role**: Determines the next logical step in the interview based on three cases:
    - **Case 1 (Probing/Dependent)**: If the user's response requires deeper exploration, it triggers a dependent question on the current topic.
    - **Case 2 (Same Topic/Independent)**: If the response is sufficient, it generates a new independent query on the same topic to test another perspective.
    - **Case 3 (Topic Change)**: When the topic's question threshold is met, it signals a transition to the next topic in the plan.

### 4. Question Generator
- **Role**: Dynamically crafts questions based on the Router's decision:
    - **Topic Changed**: Fetches the next topic from the plan using current summaries and user data.
    - **Same Topic Independent**: Uses turn metrics to generate a complementary "trap" or perspective check.
    - **Same Topic Dependent**: Identifies gaps or ambiguities in the previous response for targeted probing.

### 5. Phase Summarizer
- **Role**: Maintains "rolling" summaries for the active phase turn-by-turn. When a phase changes, it preserves the latest summary of the previous phase to maintain a rich context without bloating the prompt.

### 6. Metric Calculator
- **Role**: Scores the candidate's response across several crucial dimensions (see [Metrics](#-metrics-calculated)).

### 7. Report Generator
- **Input**: User Profile, JD, Full Chat History
- **Output**: Markdown "Interview Readiness Report"
- **Role**: Compiles an executive summary, scored performance metrics, key strengths, improvement areas, and a final hiring recommendation.

---

## 📊 Metrics Calculated

Each response is evaluated against the following parameters:

| Metric | Name | Description |
| :--- | :--- | :--- |
| **QAR** | Question Answer Relevance | Semantic relevance of the answer to the specific question asked. |
| **TDS** | Topical Depth Score | Evaluates causal reasoning, examples, and quantified details. |
| **ACS** | Answer Completeness Score | Checks for on-topic consistency and sufficient response length. |
| **SS** | Specificity Score | Measures usage of concrete technologies, tools, and numeric data. |
| **CCS** | Confidence Clarity Score | Rewards direct, action-oriented language; penalizes hedging. |
| **FARQ** | Factual Accuracy & Reasoning | LLM-judged technical correctness and logical soundness. |
| **RFD** | Red Flag Detector | Identifies blame-shifting, contradictions, or question avoidance. |
| **STAR** | STAR Method Tracking | Tracks (Situation, Task, Action, Result) structure both per-turn and cumulatively. |

---

## 📁 File Structure

```text
SkillIssue.ai/
├── src/
│   ├── main.py                 # FastAPI Application entry point
│   ├── gradio.py               # Gradio UI application
│   ├── agents/                 # Agent implementations
│   │   ├── orchestrator.py     # LangGraph workflow logic
│   │   ├── planner/            # Interview planning logic
│   │   ├── question_generator/ # Dynamic question crafting
│   │   ├── metric_calculator/  # Scoring logic
│   │   └── ...
│   ├── controllers/            # API Route handlers
│   ├── models/                 # Pydantic & Redis state models
│   ├── routes/                 # FastAPI router definitions
│   └── schemas/                # Pydantic schemas for data validation
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Redis Server (running on localhost:6379 or configured via environment variables)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/SkillIssue.ai.git
   cd SkillIssue.ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

You can interact with SkillIssue.ai through the Gradio web interface.

#### Start the Gradio UI
For a visual, interactive interview experience:
```bash
python -m src.gradio
```
The UI will be accessible at `http://localhost:7860`.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
