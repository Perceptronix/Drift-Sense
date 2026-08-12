# Release Notes Template

Use this template for each dataset release.

---

# Release Notes — {dataset_name} v{version}

**Date:** {release_date}
**Certification:** {CERTIFIED | PENDING}

## Summary

- {n} samples generated
- Generation config: `{config_path}` (frozen)
- Master seed: `{seed}`
- Validation result: L1–L5 {PASS/PASS with notes}

## Changes Since Previous Version

- {change 1}
- {change 2}

## Validation Report

| Level | Result |
|---|---|
| L1 File completeness | PASS |
| L2 Metadata consistency | PASS |
| L3 Ground-truth accuracy | PASS |
| L4 Scientific validation | PASS/NA |
| L5 Reproducibility | PASS |

## Known Limitations

- {limitation 1}
- {limitation 2}

## Verification

```
sh checksums/verify_checksums.sh <dataset_root>
semicon-sim --validate <dataset_root> --level L5
```

## Sign-off

- [ ] Dataset Engineering Lead
- [ ] Scientific Lead
- [ ] Program Manager

---

*Template frozen in Phase 5.5.*
