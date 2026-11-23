# ALP-ttbar Toy MC v2.8 — Post-Registration Results: Trimmed Tag Estimator as Default Discriminator

**Author:** Won Shik Paik (Independent Researcher, Auckland, New Zealand)  
**Date:** 2026-11-22  
**DOI:** [10.5281/zenodo.24437855](https://doi.org/10.5281/zenodo.24437855)  
**Preregistration:** [10.5281/zenodo.24414960](https://doi.org/10.5281/zenodo.24414960)

## Overview

Post-registration results for ALP-ttbar Toy MC v2.8, testing the **trimmed Tag estimator (k = 1%)** as the default discriminator across a 50-seed ensemble (i = 50–99) independent from v2.7 (i = 0–49).

Nine predictions were preregistered covering stability (S1–S3), degradation ratio (D1–D4), and diagnostic properties (X1–X2) at two ALP masses (17 MeV and 200 MeV).

### Key Results

| Prediction | Description | Observed | Verdict |
|:---:|:---|:---:|:---:|
| **S1** | CV(trim) < CV(untrim)/10 | 0.091% < 0.684% | **CONFIRMED** |
| **S2** | CV(trim) < 1% | 0.091% | **CONFIRMED** |
| **S3** | \|ΔCV\| < 0.1% at 200 MeV | 0.078% | **CONFIRMED** |
| **D1** | mean(deg_T) < mean(deg_U) | 1.0648 < 1.5762 | **CONFIRMED** |
| **D2** | mean(deg_T) < 1.2 | 1.0648 | **CONFIRMED** |
| **D3** | frac(deg_T < deg_U) > 0.8 | 1.00 | **CONFIRMED** |
| **D4** | \|Δmean\| < 0.05 at 200 MeV | 0.0067 | **CONFIRMED** |
| X1 | median \|Δt_opt\| > 0 | 0.00 | REFUTED |
| **X2** | CV(Δdeg) < 50% | 21.1% | **CONFIRMED** |

**Score: 8/9 CONFIRMED — Core: 5/5 CONFIRMED**

At 17 MeV, the trimmed Tag achieves a **~75-fold reduction in CV** (0.091% vs 6.84%) with a mean degradation ratio of **1.0648** vs 1.5762 (untrimmed). All 50 seeds show trimmed-Tag superiority. Both secondary predictions (S3, D4) confirmed — §7 criterion for 'common default' adoption fully met.

## Companion References

- **[E1]** Alimena et al., "Hunting for Long-Lived ALPs in Top Events via Displaced Dielectron Pairs at the LHC," [arXiv:2610.38932](https://arxiv.org/abs/2610.38932) (2026)
- **[E2]** Rygaard et al., "Top Secrets: Long-Lived ALPs in Top Production," [arXiv:2306.08686](https://arxiv.org/abs/2306.08686) (2023)

## Configuration

- **Config E3:** f = 0.25, 9-disk z precision, η = 2.0, 17-band geometry
- **Seed range:** i = 50–99 (independent from v2.7's i = 0–49)
- **Masses:** 17 MeV, 200 MeV
- **Trim fraction:** k = 1% (top + bottom tails removed)
- **N_sig:** up to 50,000; **N_conv:** up to 100,000

## Repository Structure

```
├── README.md                          # This file
├── run_v28_trimmed_tag.py             # Simulation orchestrator (seeds 50–99, seed-0 auto-validation)
├── generate_figures.py                # Matplotlib figure generator (8 figures)
├── generate_v28_postreg.py            # ReportLab PDF generator
├── v28_results.json                   # Per-seed results (JSON)
├── v28_results.npz                    # Per-seed results (NumPy arrays)
├── frozen/
│   ├── endcap_sim.py                  # Simulation engine (frozen since v2.5)
│   ├── mtag_v24.py                    # 17-band Tag formula (frozen since v2.4)
│   └── mtag_v22.py                    # 9-band baseline (frozen since v2.2)
├── fig1_deg_ratio_17MeV.png           # Degradation ratio at 17 MeV
├── fig2_deg_ratio_200MeV.png          # Degradation ratio at 200 MeV
├── fig3_cv_comparison.png             # CV comparison bar chart
├── fig4_deg_histogram_17MeV.png       # Degradation ratio histograms
├── fig5_scorecard.png                 # Prediction scorecard
├── fig6_delta_deg_17MeV.png           # Per-seed improvement Δ(deg)
├── fig7_cross_version_cv.png          # Cross-version CV validation
├── fig8_trimmed_vs_hv.png             # Trimmed Tag vs HV comparison
└── ALP-ttbar_Toy-MC_v2.8_Post-Registration_Trimmed-Tag-Estimator-Results_2026-11-22.pdf
```

## Frozen Module Integrity

| Module | MD5 Hash | Frozen Since |
|:---|:---|:---:|
| endcap_sim.py | `7daa81b2723a1c13df68ee69b428c2d0` | v2.5 |
| mtag_v24.py | `39451a2189d71ec4a9d5990eacb54c6e` | v2.4 |
| mtag_v22.py | `a687701efe4476a999e27b32341c8c39` | v2.2 |

## Reproducing Results

```bash
# 1. Run simulation (requires numpy, scipy)
#    Includes seed-0 auto-validation (§4.3): compares against v2.7
#    reference values and aborts on mismatch before running seeds 50–99.
python run_v28_trimmed_tag.py

# 2. Generate figures (requires numpy, matplotlib)
python generate_figures.py

# 3. Generate PDF (requires reportlab, matplotlib, numpy)
python generate_v28_postreg.py
```

**Note:** The full simulation takes approximately 5–10 minutes on a modern CPU. Seed-0 validation runs automatically at the start; if it fails, the script aborts before the main ensemble.

## DOI Chain

| Version | DOI |
|:---|:---|
| v2.8 post-reg (this) | [10.5281/zenodo.24437855](https://doi.org/10.5281/zenodo.24437855) |
| v2.8 prereg | [10.5281/zenodo.24414960](https://doi.org/10.5281/zenodo.24414960) |
| v2.7 post-reg | [10.5281/zenodo.24408990](https://doi.org/10.5281/zenodo.24408990) |
| v2.7 prereg | [10.5281/zenodo.24388228](https://doi.org/10.5281/zenodo.24388228) |
| v2.6 post-reg | [10.5281/zenodo.24373115](https://doi.org/10.5281/zenodo.24373115) |
| v2.6 prereg | [10.5281/zenodo.24361872](https://doi.org/10.5281/zenodo.24361872) |
| v2.5 post-reg | [10.5281/zenodo.24341050](https://doi.org/10.5281/zenodo.24341050) |
| v2.5 prereg | [10.5281/zenodo.24329044](https://doi.org/10.5281/zenodo.24329044) |
| v2.4 post-reg | [10.5281/zenodo.24302619](https://doi.org/10.5281/zenodo.24302619) |
| v2.4 prereg | [10.5281/zenodo.24296796](https://doi.org/10.5281/zenodo.24296796) |

## Disclaimer

Independent personal toy study, not affiliated with the authors of arXiv:2610.38932 or arXiv:2306.08686, nor with the CMS, ATLAS, LHCb or ALICE Collaborations or the FCC study. Detector numbers are assumed; only qualitative trends and ratios are meaningful.

## License

MIT
