# Project MosAIc: Social-Listen Integration Guide
**Target Audience:** `social-listen` Development Agent
**Context:** This document outlines how the downstream analysis engine (`shadee-mosaic`) consumes the data provided by your ingestion pipeline.

---

## 1. Overview
`social-listen` serves as the **Top-End Ingestion Funnel**. Your role is to capture raw social narratives and provide them with broad categorization. `shadee-mosaic` acts as the **Downstream Specialist**, performing deep clinical analysis, PII scrubbing, and RAG-based synthesis.

## 2. Data Contract & Expectations
We rely on the following from your pipeline:

1.  **Deduplication TARGET:** We use the composite key of `post_url` and `platform` to ensure we don't index duplicate narratives. Please maintain the integrity of these fields.
2.  **Tier 1 Classification:** Your Regex-based `BUCKET_PATTERN` is our **Baseline**. We use these buckets to filter records before sending them to the more expensive AI (Tier 2) layer.
3.  **Timestamp Alignment:** The `post_dt` field is critical for our temporal analysis and for the "Youth Specialist" persona to contextualize seasonal or pandemic-related trends.

## 3. Recommended Ingestion Enhancements
To support our move toward **Visual Discovery (Phase 5)**, the following metadata enhancements in `social-listen` would be high-value:

- **Full Thread Context:** If possible, pulling parent/child comments for Reddit posts increases the signal-to-noise ratio for our causal mapping.
- **Platform-Specific "Vitals":** Capturing engagement metrics (upvotes, views) helps us prioritize high-impact narratives for synthesis.
- **Extended Sources:** As we refine the "Specialist" persona, platforms like Discord or dedicated mental health forums would provide deeper clinical signals than broad platforms like YouTube.

## 4. The Funnel Flow
1.  **Ingestion Agent (`social-listen`)**: Fetches raw text -> Regex Triage -> Supabase `social_posts`.
2.  **Analysis Agent (`shadee-mosaic`)**: `content_scrubbed` (Anonymization) -> `vector_embedding` -> **Dynamic Research flow** -> Clinical Synthesis.

## 5. Shared Schema Notes
- **Table:** `social_posts`
- **Primary downstream consumer:** `src/ai/indexer.py` (indexes any row where `is_anonymized` is NULL or FALSE).

Let's maintain this Handover/Takeover protocol to ensure the data remains "unpolluted" before it reaches the clinical analysis stage.
