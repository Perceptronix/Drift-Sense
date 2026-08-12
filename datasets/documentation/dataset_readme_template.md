# Dataset README Template

Use this template to generate the `README.md` inside each populated dataset directory.

---

# {dataset_name} — {dataset_title}

**Version:** {version} | **Generated:** {date} | **Size:** {size}

## Overview

{Purpose, 1 paragraph.}

## Contents

- `images/` — {N} TIFF SEM images, {W}x{H}, {bit_depth}-bit, {pixel_size} nm/px
- `ground_truth/` — edge maps, CD values, segmentation, contours
- `metadata/` — per-sample config, metadata, timing
- `splits/` — train/val/test file lists (if applicable)
- `dataset_index.json` — sample index with hashes

## Structures

| Structure | Count | CD range (nm) | Height range (nm) | Pitch range (nm) |
|---|---|---|---|---|
| iso_line | | | | |
| dense_ls | | | | |
| contact | | | | |
| via | | | | |
| trench | | | | |
| fin | | | | |
| gate | | | | |
| sti | | | | |
| bimaterial | | | | |
| pitch_std | | | | |

## Materials

List material stacks and their frequencies.

## Imaging Parameters

| Parameter | Range |
|---|---|
| Beam energy | |
| Probe current | |
| Probe diameter | |
| LER 3σ | |
| LER ξ | |
| Overlay | |

## Reproducibility

- Master seed: `{seed}`
- Generation config: `{config path}`
- Simulator version / git hash: `{version} / {hash}`
- Checksums: `SHA256SUMS` — verify with `checksums/verify_checksums.sh`

## Validation

- L1 file completeness: PASS/FAIL
- L2 metadata consistency: PASS/FAIL
- L3 ground-truth accuracy: PASS/FAIL
- L4 scientific validation: PASS/FAIL
- L5 reproducibility: PASS/FAIL

## License

CC BY 4.0. Cite the SEMICON 2026 simulator.

## Release Notes

See `release_notes.md`.
