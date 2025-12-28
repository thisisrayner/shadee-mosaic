# State of the Data Report: Project Shadee-Intelligence

## Executive Summary
- **Total Records:** 55607
- **Analyzed Sample:** 1000

## Platform Distribution (Sample)
| platform   |   count |
|:-----------|--------:|
| Tumblr     |    1000 |

## Bucket Distribution (Sample)
| bucket_id             |   count |
|:----------------------|--------:|
| other                 |     688 |
| chronic_fatigue       |      81 |
| therapy_discussion    |      44 |
| infrastructure_policy |      41 |
| social_support_prayer |      35 |
| critique_trolling     |      31 |
| loneliness_isolation  |      20 |
| relationship_breakup  |      17 |
| self_harm             |      15 |
| depression_misery     |      15 |
| family_conflict       |       4 |
| self_blame            |       4 |
| identity_confusion    |       2 |
| work_burnout          |       2 |
| failed_outreach       |       1 |

## Schema Audit
The `social_posts` table contains the following core columns:
- `id`
- `post_dt`
- `platform`
- `bucket_id` (Legacy/Regex)
- `ai_bucket_id`
- `ai_confidence`
- `ai_explanation`

**Missing for Shadow Tracking:**
- `is_anonymized` (Boolean)
- `verified_bucket_id` (UUID/Int)

## Schema Audit
The `social_posts` table already contains several "Shadow Tracking" columns:
- `ai_bucket_id`
- `ai_confidence`
- `ai_explanation`
- `is_anonymized`
- `verified_bucket_id`

## Recommendations
1. **Bulk Anonymization:** Only a fraction of the data appears to be marked as anonymized. We should run the `src/data/scrubber.py` logic in a bulk job.
2. **Backfill Labels:** Many records might missing high-confidence AI labels.
