---
description: Create a Product Requirements Document (PRD) from conversation using rich aesthetics and Mermaid diagrams
argument-hint: [output-filename]
---

# Create PRD: Generate Product Requirements Document

## Overview

Generate a comprehensive Product Requirements Document (PRD) based on the current conversation context and requirements discussed. Use rich aesthetics, clean typography, tables, Github alerts, and Mermaid diagrams to build a premium, highly descriptive PRD.

## Output File

Write the PRD to: `$ARGUMENTS` (default: `PRD.md`)

## PRD Structure

Create a well-structured PRD with the following sections. Adapt depth and detail based on available information:

### 1. Executive Summary
- **concise Overview**: A 2-3 paragraph summary of the product.
- **Value Proposition**: Why does this product exist? Who does it serve?
- **MVP Success Statement**: A single sentence declaring what the Minimum Viable Product must achieve to succeed.

### 2. Product Mission & Principles
- **Mission**: The ultimate north star of this product.
- **Core Principles**: 3-5 guiding engineering or design principles. Let's make these highly opinionated and distinct.

### 3. User Personas & Journey Maps
- **Primary Personas**: Detailed tables for target user personas (Name, Role, Tech comfort, Pain points).
- **Core User Journey Flow (Mermaid)**:
  Use a Mermaid diagram (`flowchart TD` or `sequenceDiagram`) to visualize how users discover, sign up, configure, and use the core capability of the product.
  > [!TIP]
  > Ensure all Mermaid node labels containing special characters are properly quoted to prevent syntax errors.

### 4. MVP Scope Definition
- **In Scope (✅ Checkboxes)**: Mandatory features for the first release.
- **Out of Scope (❌ Checkboxes)**: Deferred features or non-goals.
- Group into clean tables or list blocks (e.g., Core Logic, Database, User Interface, Deployment).

### 5. Functional Specifications & User Stories
- **Primary User Stories**: 5-8 stories formatted as:
  `As a [user]... I want to [action]... So that [benefit]...`
- Provide concrete input/output examples and edge cases for each user story.

### 6. System Architecture & Tech Stack

#### Architecture Block (Mermaid Diagram)
Create a visual system architecture diagram (e.g. Client $\leftrightarrow$ Backend $\leftrightarrow$ Database/External Services) using Mermaid.

#### Tech Stack Table
| Component | Technology | Version | Purpose & Rationale |
|-----------|------------|---------|---------------------|
| Runtime | {Node/Python/etc.} | {version} | {rationale} |
| Framework | {Next.js/FastAPI/etc.} | {version} | {rationale} |
| Database | {PostgreSQL/SQLite/etc.} | {version} | {rationale} |
| Styling | {Vanilla CSS/Tailwind} | {version} | {rationale} |

### 7. Security & Configuration
- **Authentication**: Flow, token types, and session duration.
- **Environment Variables**: Key variables and templates. Include a sample `.env.example` in a code block.
- **Security Boundaries**: What is explicitly protected and what is out of scope.

### 8. API Endpoint Specification (if applicable)
Use clean tables and code blocks to show request and response formats.
- **Endpoints**: `GET /api/v1/health`, `POST /api/v1/tickets`, etc.
- **Request Headers / Query Parameters**
- **JSON Request/Response Payloads**

### 9. Success Criteria & Metrics
- **Functional Verification (✅ Checkboxes)**: Verifiable outcomes.
- **UX & Performance Goals**: Speed, visual appeal, responsiveness targets.

### 10. Phased Implementation Roadmap
Break the development down into 3 or 4 actionable implementation phases:
- **Phase 1: Foundation**: Database models, basic schemas, initial configuration.
- **Phase 2: Core Logic**: Core business logic, unit tests, and API routes.
- **Phase 3: Front-End UI**: Reusable components, state management, layouts.
- **Phase 4: Polish & Integration**: E2E testing, visual styling refinements, final checks.
For each phase, specify:
- Goal
- Deliverables (✅ Checkboxes)
- Verification Command or Action

### 11. Risks & Mitigation Strategies
A table outlining 3-5 major technical or product risks, their severity (High/Medium/Low), and detailed mitigation strategies.

---

## Technical Formatting Rules

- **Alerts**: Highlight crucial parts using Github-style alert boxes:
  > [!NOTE]
  > Background context or architecture details
  
  > [!IMPORTANT]
  > Critical MVP boundary or security rules

  > [!WARNING]
  > Breaking change risks or API limitations
- **Mermaid Diagrams**: Always format Mermaid code blocks with ````mermaid` and keep syntax simple and correct.
- **Artifact Creation**: If writing this document inside an Antigravity conversation, you can use the `write_to_file` tool with `IsArtifact: true` and `ArtifactType: 'other'` to store it beautifully in the conversation context.
