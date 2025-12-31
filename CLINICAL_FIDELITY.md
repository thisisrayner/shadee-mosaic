# Project MosAIc: Clinical Fidelity Blueprint
**Document Status:** Draft / Brainstorming
**Audience:** Stakeholders, Clinical Experts, AI Agents

## 1. Executive Summary
Project MosAIc has evolved into a high-fidelity **Dynamic Research Engine**. It moves beyond simple retrieval to perform recursive sampling with AI-led thematic saturation audits. This document outlines the path from **Thematic Discovery** to **Clinical Fidelity**—shifting from general patterns to actionable, diagnostic-grade insights.

---

## 2. Current Architecture (Phases 1-4)
### Pipeline Overview
1.  **Ingestion (The "Top-End"):** Automated daily scrapes of Reddit (PRAW), YouTube (Google API), and Tumblr via GitHub Actions in the `social-listen` repository.
2.  **Privacy Layer (Shadow Write):** PII is non-destructively scrubbed. Raw data is preserved in `content` while `content_scrubbed` stores anonymized versions.
3.  **Vectorization:** `text-embedding-004` generates high-dimensional vectors for semantic context.
4.  **Dynamic Research (Recursive RAG):** 
    - **Stage 1 (N=25):** Initial thematic scan and saturation audit.
    - **Stage 2 (N=120):** Secondary audit if thematic variance is high.
    - **Stage 3 (N=500):** Final expansion for categorical depth.
5.  **Intelligence Layer:** Gemini 3.0 Flash Preview (Senior Youth Mental Health Researcher Persona) synthesizes the finalized dataset into a Markdown research report.
6.  **Audit Trail:** Every step is logged in a "Protocol Trace" UI and a `research_logs` table for analytical audibility.

### 2.5 Top-End Funnel Analysis (Social-Listen)
The ingestion pipeline in `social-listen` provides the following foundational metadata and constraints:
- **Unique Identifier:** Composite key of `post_url` + `platform` (ensures deduplication).
- **Source Depth:** Currently pulling from `r/Singapore`, `r/MentalHealth`, and specific YouTube clinical keywords.
- **Legacy Classification:** `src/utils/classification.py` uses `BUCKET_PATTERN` (Regex) for initial triage. This forms our "Tier 1" baseline.
- **Regional Context:** Posts are flagged as `Singapore` vs `Global`.

### Current Methodology
- **Classification:** Hybrid approach using Tier 1 (Deterministic/Regex) and Tier 2 (Probabilistic/LLM) classifiers.
- **Synthesis:** Empathetic, thematic summarization based on semantic proximity.
- **Discovery UX:** A dual-pane interface (Synthesis vs. Evidence) for manual audit by clinicians.

---

## 3. The Path to Clinical Fidelity (Fidelity Tiers)

### Tier 1: Thematic Recognition (BASELINE)
- **Goal:** Identifying *what* is being said using existing Regex rules.
- **Implementation:** `social-listen/src/utils/classification.py`.
- **Output:** Qualitative buckets (e.g., `identity_confusion`, `chronic_fatigue`).
- **Confidence:** Fixed/Deterministic.

### Tier 2: Causal & Kinetic Mapping (NEXT)
- **Goal:** Identifying *why* and *how* distress is manifesting.
- **New Requirements:**
    - **Causal Extraction:** Identifying specific triggers (input stressors) vs. reactive symptoms (output behaviors).
    - **Kinetic Chains:** Narrating the progression (e.g., Exam Failure -> Social Withdrawal -> Sleep Disruption).
- **Implementation:** Enhanced Prompt Engineering for causal feature extraction.

### Tier 3: Quantifiable Diagnostics (FUTURE)
- **Goal:** Extracting "Vital Signs" from unstructured text.
- **New Requirements:**
    - **KPI Extraction:** Frequency (times/week), Intensity (severity scales), and Duration (weeks/months).
    - **Structured Summaries:** Tabular clinical summaries (Symptoms | Frequency | History).
    - **External Validation:** Mapping extracted symptoms to ICD-11 or DSM-5 criteria markers.

---

## 4. Key Fidelity Pillars (Roadmap)

### A. Advanced NLP Integration
- **Relationship Extraction:** Moving beyond "bag of keywords" to "graph of stressors."
- **Sentiment Nuance:** Detecting ambivalence, sarcasm, and desperation levels.

### B. Human-in-the-Loop (HITL)
- **Clinical Validation:** Mechanisms for human specialists to "upvote/downvote" AI-extracted causal mappings to refine the model.
- **Expert UI:** Tools for clinicians to correct the "AI Explanation" snippets, creating a high-fidelity training set for Phase 6.

### C. Explainability (XAI)
- **Specialist Reasoning:** The AI must explain *why* it linked a specific narrative to a clinical theme (e.g., "The phrasing 'weight on my chest' is strongly indicative of physical anxiety symptoms common in this demographic").

---

## 5. Stakeholder Discussion Points
1.  **Risk Management:** How do we handle "Hallucinations" when the AI moves from summary to diagnostic inference?
2.  **Breadth vs. Depth:** Do we prioritize scanning 10,000 records superficially, or 100 records with extreme high-fidelity?
3.  **Ethical Guardrails:** Ensuring the "Diagnostic" persona stays within "Assistant" boundaries and never crosses into "Autonomous Physician" territory.
