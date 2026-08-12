#!/usr/bin/env python3
"""Quick worker benchmark: 200 samples per config, measures wall-clock + timing."""
from __future__ import annotations
import gc, json, os, shutil, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulator" / "src"))

import numpy as np
from semicon.geometry.raster import save_library
from semicon.geometry.structures import build_structure_library
from semicon.orchestration.pipeline import APP_VERSION, RuntimeContext, build_context, run_pipeline

BENCH_SEED = 5005
BENCH_N = 200
OFFSET = 95000  # Safe offset - well beyond any production index

# Full parameter ranges (same as production)
RANGES = {
    "cd": (10.0, 500.0), "height": (20.0, 200.0), "pitch": (20.0, 1000.0),
    "beam": (0.3, 30.0), "current": (1.0, 1000.0), "diameter": (0.5, 10.0),
    "ler3sig": (0.0, 5.0), "lerxi": (5.0, 100.0), "overlay": (0.0, 10.0),
    "cdu": (0.0, 2.0),
}
DIST = {"dense_ls":20,"contact":15,"iso_line":15,"via":10,"fin":10,"gate":10,"trench":8,"sti":5,"bimaterial":4,"pitch_std":3}
TYPES = []
for s,w in DIST.items():
    TYPES.extend([s]*int(round(BENCH_N*w/sum(DIST.values()))))
while len(TYPES)<BENCH_N: TYPES.append("iso_line")
TYPES = TYPES[:BENCH_N]

def make_plan():
    import random
    rng = random.Random(BENCH_SEED)
    rng.shuffle(TYPES)
    plan = []
    for i,st in enumerate(TYPES):
        plan.append({"i":i, "st":st, "ov":{
            "structure.structure_type":st, "structure.cd_nm":rng.uniform(*RANGES["cd"]),
            "structure.height_nm":rng.uniform(*RANGES["height"]),
            "structure.pitch_nm":rng.uniform(*RANGES["pitch"]),
            "structure.width_nm":1024.0, "structure.height_nm_fov":1024.0,
            "structure.pixel_size_nm":1.0,
            "variability.ler_3sigma_nm":rng.uniform(*RANGES["ler3sig"]),
            "variability.ler_xi_nm":rng.uniform(*RANGES["lerxi"]),
            "variability.overlay_dx_nm":rng.uniform(*RANGES["overlay"])*rng.uniform(-1,1),
            "variability.overlay_dy_nm":rng.uniform(*RANGES["overlay"])*rng.uniform(-1,1),
            "variability.cdu_sigma_nm":rng.uniform(*RANGES["cdu"]),
            "physics.beam_energy_keV":rng.uniform(*RANGES["beam"]),
            "physics.probe_current_pA":rng.uniform(*RANGES["current"]),
            "physics.probe_diameter_nm":rng.uniform(*RANGES["diameter"]),
        }})
    return plan

_CTX = None
_DEFS = None

def _init(lib, defs):
    global _CTX, _DEFS
    _CTX = build_context(lib, app_version=APP_VERSION, git_hash="bench")
    _DEFS = defs

def _run(item, out_dir, seed, name, offset):
    global _CTX, _DEFS
    from semicon.orchestration.config import _apply_overrides, _to_config, validate, load_config
    idx = item["i"] + offset
    try:
        cfg = validate(_to_config(_apply_overrides(load_config(None, defaults_path=_DEFS).merged(), item["ov"])))
        t0 = time.perf_counter()
        r = run_pipeline(_CTX, cfg, Path(out_dir), idx, name, seed, write_outputs=True)
        return {"idx":idx, "st":item["st"], "ok":r.status=="OK", "wall":time.perf_counter()-t0, "timing":r.timing, "err":r.error}
    except Exception as e:
        return {"idx":idx, "st":item["st"], "ok":False, "wall":0, "timing":{}, "err":str(e)}

def bench(nw, plan, lib, defs, seed):
    out = ROOT/"datasets"/f"bench_{nw}w"
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    name = f"bench_{nw}w"

    gc.collect()
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=nw, initializer=_init, initargs=(lib,defs)) as ex:
        futs = {ex.submit(_run, it, str(out), seed, name, OFFSET): it["i"] for it in plan}
        for f in as_completed(futs):
            try:
                results.append(f.result(timeout=600))
            except Exception as e:
                results.append({"idx":futs[f]+OFFSET,"ok":False,"wall":0,"timing":{},"err":str(e)})
    wall = time.time()-t0

    nok = sum(1 for r in results if r["ok"])
    nf = sum(1 for r in results if not r["ok"])
    walls = [r["wall"] for r in results if r["wall"]>0]

    # Stage timing
    stages = {}
    for r in results:
        if r.get("timing"):
            for k,v in r["timing"].items():
                stages.setdefault(k,[]).append(v)
    avg_stages = {k:np.mean(v) for k,v in stages.items()}

    # Disk
    dsk = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())

    spm = nok/(wall/60) if wall>0 else 0
    pps = wall/nok if nok>0 else 0

    return {
        "workers":nw, "n_ok":nok, "n_fail":nf, "wall_s":round(wall,1),
        "spm":round(spm,1), "pps":round(pps,3),
        "avg_wall_per_sample":round(np.mean(walls),3) if walls else 0,
        "p50":round(float(np.percentile(walls,50)),3) if walls else 0,
        "p95":round(float(np.percentile(walls,95)),3) if walls else 0,
        "disk_mb":round(dsk/1024/1024,1),
        "avg_stages":{k:round(v,4) for k,v in avg_stages.items()},
        "failures":[{"idx":r["idx"],"err":r.get("err","")} for r in results if not r["ok"]][:5],
    }

def verify(a_dir, b_dir, n=5):
    a_imgs = sorted((a_dir/"images").glob("*.tiff"))[:n]
    b_imgs = sorted((b_dir/"images").glob("*.tiff"))[:n]
    if len(a_imgs)!=len(b_imgs): return False
    return all(a.read_bytes()==b.read_bytes() for a,b in zip(a_imgs,b_imgs))

def main():
    lib_path = str(ROOT/"datasets"/"ds5_final_training"/"_lib_validation.gds")
    defs_path = str(ROOT/"simulator"/"configs"/"defaults.yml")
    if not Path(lib_path).exists():
        lib = build_structure_library(fov_nm=1024.0, cd_nm=40.0, height_nm=70.0)
        save_library(lib, Path(lib_path))

    plan = make_plan()
    print(f"Plan: {len(plan)} samples, {len(set(p['st'] for p in plan))} types")

    all_results = []
    for nw in [4, 6, 8]:
        gc.collect()
        time.sleep(2)
        print(f"\n{'='*50}\nBenchmark: {nw} workers x {BENCH_N} samples\n{'='*50}")
        r = bench(nw, plan, lib_path, defs_path, BENCH_SEED)
        all_results.append(r)
        print(f"  OK: {r['n_ok']}, Failed: {r['n_fail']}")
        print(f"  Wall: {r['wall_s']}s, Rate: {r['spm']}/min, Per-sample: {r['pps']}s")
        print(f"  P50: {r['p50']}s, P95: {r['p95']}s, Disk: {r['disk_mb']}MB")
        if r['avg_stages']:
            print(f"  Stages: {', '.join(f'{k}={v:.3f}s' for k,v in sorted(r['avg_stages'].items()))}")

    # Verify bit-identity
    if len(all_results)>=2:
        d0 = ROOT/"datasets"/f"bench_{all_results[0]['workers']}w"
        d1 = ROOT/"datasets"/f"bench_{all_results[1]['workers']}w"
        ok = verify(d0, d1)
        print(f"\nBit-identity (config 0 vs 1): {'PASS' if ok else 'FAIL'}")

    # Save
    with open(ROOT/"reports"/"benchmark_results.json","w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved to reports/benchmark_results.json")

    # Cleanup
    for r in all_results:
        d = ROOT/"datasets"/f"bench_{r['workers']}w"
        if d.exists(): shutil.rmtree(d)
    print("Benchmark directories cleaned.")

    # Summary
    print(f"\n{'='*60}")
    print(f"{'Workers':>8} {'Rate':>10} {'Per-smp':>10} {'P50':>8} {'P95':>8} {'Disk':>8}")
    for r in all_results:
        print(f"{r['workers']:>8} {r['spm']:>8.1f}/m {r['pps']:>8.3f}s {r['p50']:>6.3f}s {r['p95']:>6.3f}s {r['disk_mb']:>6.1f}MB")

    base = all_results[0]
    print(f"\nScaling:")
    for r in all_results:
        ideal = r['workers']/base['workers']
        actual = base['pps']/r['pps'] if r['pps']>0 else 0
        eff = actual/ideal*100 if ideal>0 else 0
        print(f"  {r['workers']}w: {actual:.2f}x (ideal {ideal:.2f}x, eff {eff:.0f}%)")

if __name__=="__main__":
    main()
