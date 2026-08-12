# DS5 Chunk Migration Audit

**Date:** 2026-08-03
**Status:** READY FOR MIGRATION

---

## Current State

| Metric | Value |
|--------|-------|
| Checkpoint completed | 11,064 |
| Last completed ID | 11,658 |
| Images on disk | 11,177 |
| GT JSON on disk | 11,177 |
| GT Material on disk | 11,177 |
| Metadata on disk | 11,177 x 3 |
| Has existing chunks | NO |

---

## Chunk Plan

| Chunk | Sample Range | Count |
|-------|-------------|-------|
| chunk_000 | 0 - 999 | 1,000 |
| chunk_001 | 1,000 - 1,999 | 1,000 |
| chunk_002 | 2,000 - 2,999 | 1,000 |
| chunk_003 | 3,000 - 3,999 | 1,000 |
| chunk_004 | 4,000 - 4,999 | 1,000 |
| chunk_005 | 5,000 - 5,999 | 1,000 |
| chunk_006 | 6,000 - 6,999 | 1,000 |
| chunk_007 | 7,000 - 7,999 | 1,000 |
| chunk_008 | 8,000 - 8,999 | 1,000 |
| chunk_009 | 9,000 - 9,999 | 1,000 |
| chunk_010 | 10,000 - 10,999 | 1,000 |
| chunk_011 | 11,000 - 11,063 | 64 |

Total: 12 chunks, 11,064 samples

---

## Migration Rules

- Files MOVED, not copied
- No rewriting
- No recompression
- No regeneration
- No renaming
- Checksums preserved
- Scientific data untouched
