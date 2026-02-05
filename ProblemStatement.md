### Project Title: AI-Driven Contextual Mock Interviewer & Analyzer

---

### 1. Context & Background

Traditional mock interviews are often either static (standard lists of questions), expensive (hiring human coaches), or lack specific context (generic AI chatbots). Candidates struggle to assess their readiness for specific roles because existing tools cannot dynamically synthesize their personal history (Resume) with the specific demands of a target role (Job Description) to provide objective, actionable feedback.

---

### 2. Phase I: The Core MVP (Context-Aware Logic Engine)

**Problem Definition:**
The primary challenge is to create an intelligent conversational agent capable of conducting a specialized technical and behavioral interview based on specific, unstructured input data.

* **Input Ingestion:** The system must accept and parse three distinct data sources:
1. **Candidate Profile:** The user's Resume/CV (PDF/Docx).
2. **Target Profile:** The Job Description (JD).
3. **Domain Parameters:** Specific industry knowledge or difficulty settings (e.g., "Senior Python Developer" vs. "Junior Data Analyst").


* **Contextualization:** The system currently lacks the ability to generate questions that bridge the gap between the Resume and the JD. The problem is to generate unique questions that probe *claimed* skills in the context of *required* duties, rather than generic questions.
* **Dynamic Evaluation:** The system must evaluate answers not just for factual correctness, but for relevance to the specific question asked. It needs to track the "flow" of the interview, digging deeper if an answer is vague.
* **Analytical Output:** The user needs a post-interview report that identifies:
* Technical gaps (Knowledge missed).
* Relevance gaps (Did the candidate answer the specific question asked?).
* Resume discrepancies (claimed vs. demonstrated knowledge).



---

### 3. Phase II: The Voice Interface (Mandatory Extension)

**Problem Definition:**
Text-based interviews fail to simulate the pressure and mechanics of a real-world verbal interview. To mirror reality, the system must transition from a "Chatbot" to a "Spoken Agent."

* **Verbal fluency:** The system needs to assess the candidate's ability to articulate complex thoughts verbally, which involves different cognitive processes than typing.
* **Latency & Flow:** The interaction requires a conversational cadence. The problem is to minimize the "dead air" between the candidate finishing a sentence and the interviewer responding, maintaining the illusion of a live conversation.
* **Interruptibility:** In a real interview, people interrupt or pause. The system must handle audio input streams that may contain filler words ("um," "uh"), pauses, or corrections, distinguishing between the end of a thought and a momentary pause.

---

### 4. Phase III: The Integrity & Proctoring Layer (Security Extension)

**Problem Definition:**
Remote interviews (and mock assessments intended to simulate them) suffer from a lack of environmental control. To validate the authenticity of the mock interview performance, the system requires a monitoring layer.

* **Visual Monitoring:** The system needs to detect the presence of the candidate within a specific frame. It must identify anomalies such as the candidate leaving the seat or looking away excessively (suggesting reading off-screen notes).
* **Environment Integrity:** The problem involves detecting unauthorized external aid. This includes identifying multiple voices in the audio stream (coaching) or detecting secondary screens/devices in the visual field.
* **Digital Integrity:** The system must ensure the browser environment is the focus. It needs to detect if the user is switching tabs to search for answers or using copy-paste functions during the session.

---

### 5. Phase IV: The Behavioral Analyst (Affective Computing Extension)

**Problem Definition:**
Human interviewers judge "soft skills" and "confidence" based on non-verbal cues. A purely text/audio transcript misses a significant portion of communication data.

* **Micro-Expression Analysis:** The system needs to capture and interpret facial cues such as confusion, stress, or confidence during specific questions.
* **Audio Sentiment:** The problem is to analyze the *delivery* of the answer, not just the content. This includes detecting monotony, nervousness (trembling voice), or aggression in tone.
* **Engagement Metrics:** The system must correlate physical behavior with answer quality—e.g., "Does the candidate lose eye contact when asked about their weakness?"

---

### 6. Suggested Future Extensions (Scope Expansion)

These are additional problem areas that could be addressed after Phase IV:

* **Collaborative Whiteboarding:** Defining the problem of assessing System Design skills where candidates must draw diagrams or architecture while speaking.
* **Live Coding Sandbox:** The need for a secure, executable environment where the AI can "watch" code being written character-by-character to judge coding style, not just output.
* **Bias Calibration:** The problem of ensuring the AI interviewer does not develop biases based on accent, dialect, or visual demographics.
