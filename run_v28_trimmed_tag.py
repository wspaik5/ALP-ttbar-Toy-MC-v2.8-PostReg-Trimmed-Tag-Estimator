#!/usr/bin/env python3
"""
ALP-ttbar Toy MC v2.8 — Post-Registration Runner
Trimmed Tag Estimator (k=1%) as Default Discriminator

Runs the 50-seed ensemble (i=50–99) at 17 MeV and 200 MeV.
Computes: trimmed Tag (k=1%), untrimmed Tag (k=0), HV for each seed.
Outputs: v28_results.json + v28_results.npz

Config E3: f=0.25, 9-disk z precision, eta=2.0, 17-band geometry.
HV baseline uses scan_v15_endcap (material veto + exemption grid),
matching v2.7 methodology.

Author: Won Shik Paik (Independent Researcher, Auckland, NZ)
"""

import sys, os, json, time

# ── Set material scale BEFORE importing endcap_sim ────────
# Config E3 specifies f = 0.25.  endcap_sim reads V16_F at
# import time; this must precede the import statement.
os.environ['V16_F'] = '0.25'

import numpy as np

# Add frozen modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frozen'))

import endcap_sim as es
import mtag_v24 as mtag

# Verify f was applied
assert abs(es.F_MAT - 0.25) < 1e-9, f"F_MAT={es.F_MAT}, expected 0.25"

# ── Configuration ──────────────────────────────────────────
CONFIG     = 'E3'
ETA_REF    = 2.0
MASSES     = [0.017, 0.200]           # GeV
K_TRIM     = 1.0                      # trim fraction (%)
N_SIG_GEN  = 300_000
N_CONV_GEN = 1_500_000
N_SIG_MAX  = 50_000
N_CONV_MAX = 100_000
SEED_RANGE = range(50, 100)           # i = 50..99 (independent from v2.7)

# ── Trimming helper ────────────────────────────────────────
def trim_mask(lam_arr, base_mask, k_pct):
    """Boolean removal mask: remove top+bottom k% tails of lam among base vertices."""
    if k_pct <= 0:
        return np.ones(len(lam_arr), bool)
    idx_base = np.where(base_mask)[0]
    vals = lam_arr[idx_base]
    n_rem = int(np.floor(k_pct * len(vals) / 100.0))
    if n_rem == 0:
        return np.ones(len(lam_arr), bool)
    order = np.argsort(vals)
    remove_idx = np.concatenate([idx_base[order[:n_rem]],
                                  idx_base[order[-n_rem:]]])
    keep = np.ones(len(lam_arr), bool)
    keep[remove_idx] = False
    return keep

# ── Mass-window extraction helper ─────────────────────────
def find_optimal_mass_window_tag(m, sig, bkg, lam_s, lam_c, t_opt):
    """Find which mass-window candidate yielded the best limit at threshold t_opt."""
    if t_opt is None:
        ts = np.ones(len(sig['z']), bool)
        tb = np.ones(len(bkg['z']), bool)
    else:
        ts = lam_s >= t_opt
        tb = lam_c >= t_opt

    # Same mass-window candidates as scan_tag_endcap
    cands = [(None, None)]  # (None, None) = no mass cut
    for lo in np.linspace(0, 1.5 * m, 31):
        for hi in (3 * m + 0.01, np.inf):
            cands.append((lo, hi))

    best_lim = np.inf
    best_lo, best_hi = None, None
    for lo, hi in cands:
        if lo is None:
            ms = np.ones(len(sig['z']), bool)
            mb = np.ones(len(bkg['z']), bool)
        else:
            ms = (sig['m'] > lo) & (sig['m'] < hi)
            mb = (bkg['m'] > lo) & (bkg['m'] < hi)
        cs = sig['base'] & ts & ms
        cb = bkg['base'] & tb & mb
        S = sig['w'][cs].sum()
        B = bkg['w'][cb].sum()
        lim = es.upper_limit(S, B)
        if lim < best_lim:
            best_lim = lim
            best_lo = lo
            best_hi = hi
    # Convert to MeV for readability; None means no mass cut
    if best_lo is None:
        return {'mw_lo': None, 'mw_hi': None}
    return {'mw_lo': round(best_lo * 1000, 2), 'mw_hi': round(best_hi * 1000, 2) if np.isfinite(best_hi) else None}


def find_optimal_mass_window_hv(m, sig, bkg, dchi_s, dchi_b, nsig_opt, k_opt):
    """Find which mass-window candidate yielded the best limit for HV at given nsig/k."""
    if nsig_opt is None:
        vs = np.ones(len(sig['z']), bool)
        vb = np.ones(len(bkg['z']), bool)
    else:
        vs = es.endcap_material_veto(sig['zm'], sig['sz'], nsig_opt)
        vb = es.endcap_material_veto(bkg['zm'], bkg['sz'], nsig_opt)
    if k_opt is not None:
        vs = vs | (dchi_s >= k_opt)
        vb = vb | (dchi_b >= k_opt)

    cands = [(None, None)]
    for lo in np.linspace(0, 1.5 * m, 31):
        for hi in (3 * m + 0.01, np.inf):
            cands.append((lo, hi))

    best_lim = np.inf
    best_lo, best_hi = None, None
    for lo, hi in cands:
        if lo is None:
            ms = np.ones(len(sig['z']), bool)
            mb = np.ones(len(bkg['z']), bool)
        else:
            ms = (sig['m'] > lo) & (sig['m'] < hi)
            mb = (bkg['m'] > lo) & (bkg['m'] < hi)
        cs = sig['base'] & vs & ms
        cb = bkg['base'] & vb & mb
        S = sig['w'][cs].sum()
        B = bkg['w'][cb].sum()
        lim = es.upper_limit(S, B)
        if lim < best_lim:
            best_lim = lim
            best_lo = lo
            best_hi = hi
    if best_lo is None:
        return {'mw_lo': None, 'mw_hi': None}
    return {'mw_lo': round(best_lo * 1000, 2), 'mw_hi': round(best_hi * 1000, 2) if np.isfinite(best_hi) else None}


# ── Single-seed worker ─────────────────────────────────────
def run_seed(i, m):
    """Run one seed at one mass. Returns dict of results."""
    seed_conv = 100 * i + 5
    seed_sig  = 100 * i + 11

    # Generate
    conv = es.endcap_conversions(n=N_CONV_GEN, seed=seed_conv,
                                  eta_ref=ETA_REF, config=CONFIG)
    sig  = es.endcap_signal(m, n=N_SIG_GEN, seed=seed_sig,
                             eta_ref=ETA_REF, config=CONFIG)

    # Subsample
    sig,  _ = es.subsample(sig,  N_SIG_MAX)
    conv, _ = es.subsample(conv, N_CONV_MAX)

    # Δχ² and λ
    dchi_s, _ = es.compute_dchi2_endcap(sig,  eta_ref=ETA_REF)
    dchi_c, _ = es.compute_dchi2_endcap(conv, eta_ref=ETA_REF)
    lam_s = mtag.lam(sig['zm'],  sig['sz'],  dchi_s)
    lam_c = mtag.lam(conv['zm'], conv['sz'], dchi_c)

    # HV baseline: scan_v15_endcap (material veto + exemption grid)
    # This matches v2.7 methodology exactly.
    res_hv = es.scan_v15_endcap(m, sig, conv, dchi_s, dchi_c,
                                 mass_window=True)
    deg_hv = res_hv['deg']

    # Untrimmed Tag (k=0)
    res_untrim = es.scan_tag_endcap(m, sig, conv, lam_s, lam_c,
                                     mass_window=True)

    # Trimmed Tag (k=1%)
    keep_sig  = trim_mask(lam_s, sig['base'],  K_TRIM)
    keep_conv = trim_mask(lam_c, conv['base'], K_TRIM)

    # Apply trim masks
    sig_trim  = dict(sig);  sig_trim['base']  = sig['base']  & keep_sig
    conv_trim = dict(conv); conv_trim['base'] = conv['base'] & keep_conv

    # S0/lim0 from original (pre-trim) base for fair comparison
    S0_orig = sig['w'][sig['base']].sum()
    lim0_orig = es.upper_limit(S0_orig, 0)

    res_trim = es.scan_tag_endcap(m, sig_trim, conv_trim, lam_s, lam_c,
                                   mass_window=True)
    deg_trim_corrected = res_trim['limit'] / lim0_orig

    # Extract optimal mass windows (§4.4)
    mw_untrim = find_optimal_mass_window_tag(m, sig, conv, lam_s, lam_c, res_untrim['t'])
    mw_trim   = find_optimal_mass_window_tag(m, sig_trim, conv_trim, lam_s, lam_c, res_trim['t'])
    mw_hv     = find_optimal_mass_window_hv(m, sig, conv, dchi_s, dchi_c,
                                             res_hv.get('nsig'), res_hv.get('k'))

    return {
        'i': i,
        'mass': m,
        'seed_conv': seed_conv,
        'seed_sig': seed_sig,
        'deg_untrim': res_untrim['deg'],
        'deg_trim': deg_trim_corrected,
        'deg_hv': deg_hv,
        't_opt_untrim': res_untrim['t'],
        't_opt_trim': res_trim['t'],
        'S_untrim': res_untrim['S'],
        'B_untrim': res_untrim['B'],
        'S_trim': res_trim['S'],
        'B_trim': res_trim['B'],
        'S_hv': float(max(3.0, 2.0*np.sqrt(res_hv['B'])) / res_hv['limit']) if res_hv['limit'] > 0 else 0.0,
        'B_hv': float(res_hv['B']),
        'lim_untrim': res_untrim['limit'],
        'lim_trim': res_trim['limit'],
        'lim_hv': float(res_hv['limit']),
        'mw_lo_untrim': mw_untrim['mw_lo'],
        'mw_hi_untrim': mw_untrim['mw_hi'],
        'mw_lo_trim': mw_trim['mw_lo'],
        'mw_hi_trim': mw_trim['mw_hi'],
        'mw_lo_hv': mw_hv['mw_lo'],
        'mw_hi_hv': mw_hv['mw_hi'],
    }

# ── Seed-0 validation (§4.3) ──────────────────────────────
# v2.7 reference values at f=0.25, seed 0 (from v2.7 post-registration).
# These are the ground truth for cross-version reproducibility.
V27_REF = {
    0.017: {'deg_untrim': 1.66106, 'deg_trim': 1.06525, 'deg_hv': 1.05788},
    0.200: {'deg_untrim': 1.02470, 'deg_trim': 1.02942, 'deg_hv': 1.02610},
}
SEED0_TOL = 1e-4   # absolute tolerance for reproducibility check

def validate_seed0():
    """
    §4.3 of the preregistration requires seed-0 Tag and HV values to
    match v2.7 reference values before proceeding with seeds 50–99.
    Automatically compares and aborts on mismatch.
    """
    print("\n" + "="*60)
    print("  SEED-0 VALIDATION (auto-compare against v2.7, §4.3)")
    print("="*60)
    all_ok = True
    for m in MASSES:
        m_label = f"{m*1000:.0f} MeV"
        r = run_seed(0, m)
        ref = V27_REF[m]
        print(f"\n  {m_label}  seed=0:")
        for key, label in [('deg_untrim', 'deg_untrim (Tag) '),
                           ('deg_trim',   'deg_trim   (Tag) '),
                           ('deg_hv',     'deg_hv (v15 scan)')]:
            obs = r[key]
            exp = ref[key]
            match = abs(obs - exp) < SEED0_TOL
            status = "OK" if match else "MISMATCH"
            print(f"    {label} = {obs:.5f}  (v2.7: {exp:.5f})  [{status}]")
            if not match:
                all_ok = False
    if not all_ok:
        print("\n  *** SEED-0 VALIDATION FAILED — aborting. ***")
        print("  Fix the configuration and re-run.\n")
        sys.exit(1)
    print("\n  → All seed-0 values match v2.7 reference. Proceeding.\n")

# ── Main ───────────────────────────────────────────────────
if __name__ == '__main__':
    t0 = time.time()

    # Step 1: seed-0 validation
    validate_seed0()

    # Step 2: run i=50..99
    all_results = []
    for m in MASSES:
        m_label = f"{m*1000:.0f} MeV"
        print(f"\n{'='*60}")
        print(f"  Mass = {m_label}")
        print(f"{'='*60}")
        for idx, i in enumerate(SEED_RANGE):
            t1 = time.time()
            r = run_seed(i, m)
            dt = time.time() - t1
            all_results.append(r)
            print(f"  [{idx+1:2d}/50] i={i:3d}  "
                  f"deg_U={r['deg_untrim']:.4f}  "
                  f"deg_T={r['deg_trim']:.4f}  "
                  f"deg_HV={r['deg_hv']:.4f}  "
                  f"({dt:.1f}s)")

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.0f}s ({elapsed/60:.1f} min)")

    # ── Save results ──
    out_dir = os.path.dirname(os.path.abspath(__file__))

    # JSON
    json_path = os.path.join(out_dir, 'v28_results.json')
    for r in all_results:
        for k in ('t_opt_untrim', 't_opt_trim'):
            if r[k] is None:
                r[k] = 'None'
    with open(json_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved {json_path}")

    # NPZ arrays
    all_npz = {}
    for m in MASSES:
        m_key = f"{m*1000:.0f}MeV"
        subset = [r for r in all_results if abs(r['mass'] - m) < 1e-6]
        subset.sort(key=lambda x: x['i'])
        for key in ('deg_untrim', 'deg_trim', 'deg_hv',
                     'S_untrim', 'B_untrim', 'S_trim', 'B_trim',
                     'S_hv', 'B_hv', 'lim_untrim', 'lim_trim', 'lim_hv'):
            all_npz[f'{key}_{m_key}'] = np.array([r[key] for r in subset])
        for tk in ('t_opt_untrim', 't_opt_trim'):
            vals = []
            for r in subset:
                v = r[tk]
                if v == 'None' or v is None:
                    vals.append(np.nan)
                else:
                    vals.append(float(v))
            all_npz[f'{tk}_{m_key}'] = np.array(vals)
        all_npz[f'seeds_{m_key}'] = np.array([r['i'] for r in subset])
        # Mass window arrays (§4.4): None → NaN
        for mwk in ('mw_lo_untrim', 'mw_hi_untrim', 'mw_lo_trim', 'mw_hi_trim',
                     'mw_lo_hv', 'mw_hi_hv'):
            all_npz[f'{mwk}_{m_key}'] = np.array(
                [r[mwk] if r[mwk] is not None else np.nan for r in subset])

    npz_path = os.path.join(out_dir, 'v28_results.npz')
    np.savez_compressed(npz_path, **all_npz)
    print(f"Saved {npz_path}")
    print("Done.")
