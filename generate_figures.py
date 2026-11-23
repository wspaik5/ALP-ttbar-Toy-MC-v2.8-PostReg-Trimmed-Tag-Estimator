#!/usr/bin/env python3
"""Generate all 8 figures for v2.8 Post-Registration PDF.

Requires: numpy, matplotlib
Input: v28_results.npz (produced by run_v28_trimmed_tag.py)

Config E3: f=0.25, scan_v15_endcap HV baseline, seeds i=50-99.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
d = np.load(os.path.join(_DIR, 'v28_results.npz'))

# Extract arrays
du17  = d['deg_untrim_17MeV']
dt17  = d['deg_trim_17MeV']
dh17  = d['deg_hv_17MeV']
du200 = d['deg_untrim_200MeV']
dt200 = d['deg_trim_200MeV']
dh200 = d['deg_hv_200MeV']
seeds = d['seeds_17MeV']

tu17 = d['t_opt_untrim_17MeV']
tt17 = d['t_opt_trim_17MeV']

# Stats
cv_u17  = np.std(du17)/np.mean(du17)*100
cv_t17  = np.std(dt17)/np.mean(dt17)*100
cv_u200 = np.std(du200)/np.mean(du200)*100
cv_t200 = np.std(dt200)/np.mean(dt200)*100

# Dark theme
C_BG   = '#1a1a2e'
C_GRID = '#333355'
C_TEXT = '#e0e0e0'
C_RED  = '#ff6b6b'
C_GRN  = '#51cf66'
C_BLUE = '#74b9ff'
C_ORNG = '#ffa502'
C_GOLD = '#ffd43b'

def dark_style(ax, title=''):
    ax.set_facecolor(C_BG)
    ax.figure.set_facecolor(C_BG)
    ax.tick_params(colors=C_TEXT)
    ax.xaxis.label.set_color(C_TEXT)
    ax.yaxis.label.set_color(C_TEXT)
    ax.title.set_color(C_TEXT)
    for s in ax.spines.values():
        s.set_color(C_GRID)
    ax.grid(True, alpha=0.3, color=C_GRID)
    if title:
        ax.set_title(title, fontsize=11, fontweight='bold', color=C_TEXT)


# ── Figure 1: Degradation Ratio at 17 MeV ──
fig, ax = plt.subplots(figsize=(10, 5.5))
dark_style(ax, 'v2.8 Post-Registration: Degradation Ratio at 17 MeV (f=0.25)\n'
              'Trimmed vs Untrimmed Tag (50-seed ensemble, i=50-99)')
ax.plot(seeds, du17, 'o-', color=C_RED, ms=5, lw=1.2, label='Untrimmed Tag')
ax.plot(seeds, dt17, 's-', color=C_GRN, ms=4, lw=1.2, label='Trimmed Tag (k=1%)')
ax.plot(seeds, dh17, 'D-', color=C_BLUE, ms=3, lw=0.8, alpha=0.7, label='HV (scan_v15)')
ax.axhline(1.0, color=C_TEXT, ls='--', lw=0.8, alpha=0.5, label='No degradation')
ax.axhline(1.2, color=C_ORNG, ls=':', lw=1.2, label='D2 threshold (1.2)')
ax.set_xlabel('Seed index i')
ax.set_ylabel('Degradation ratio')
ax.legend(facecolor='#2a2a4a', edgecolor=C_GRID, labelcolor=C_TEXT)
fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig1_deg_ratio_17MeV.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 2: Degradation Ratio at 200 MeV ──
fig, ax = plt.subplots(figsize=(10, 5.5))
dark_style(ax, 'v2.8 Post-Registration: Degradation Ratio at 200 MeV (f=0.25)\n'
              'Trimmed vs Untrimmed Tag (50-seed ensemble, i=50-99)')
ax.plot(seeds, du200, 'o-', color=C_RED, ms=5, lw=1.2, label='Untrimmed Tag')
ax.plot(seeds, dt200, 's-', color=C_GRN, ms=4, lw=1.2, label='Trimmed Tag (k=1%)')
ax.plot(seeds, dh200, 'D-', color=C_BLUE, ms=3, lw=0.8, alpha=0.7, label='HV (scan_v15)')
ax.axhline(1.0, color=C_TEXT, ls='--', lw=0.8, alpha=0.5, label='No degradation')
ax.set_xlabel('Seed index i')
ax.set_ylabel('Degradation ratio')
ax.legend(facecolor='#2a2a4a', edgecolor=C_GRID, labelcolor=C_TEXT)
fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig2_deg_ratio_200MeV.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 3: CV Comparison ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
fig.set_facecolor(C_BG)
fig.suptitle(f'v2.8 Post-Registration: CV of Degradation Ratio\n'
             f'({cv_u17/cv_t17:.0f}x reduction at 17 MeV)',
             fontsize=12, fontweight='bold', color=C_TEXT)

for ax, title_m, cv_u, cv_t in [(ax1, '17 MeV', cv_u17, cv_t17),
                                  (ax2, '200 MeV', cv_u200, cv_t200)]:
    dark_style(ax, title_m)
    bars = ax.bar(['Untrimmed', 'Trimmed'], [cv_u, cv_t],
                  color=[C_RED, C_GRN], width=0.5, edgecolor='white', linewidth=0.5)
    ax.set_ylabel('CV (%)')
    for b, v in zip(bars, [cv_u, cv_t]):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + max(cv_u, cv_t)*0.02,
                f'{v:.2f}%', ha='center', va='bottom', color=C_TEXT, fontweight='bold')

fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig3_cv_comparison.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 4: Histogram at 17 MeV ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
fig.set_facecolor(C_BG)
fig.suptitle('v2.8 Post-Registration: Distribution of Degradation Ratio at 17 MeV (f=0.25)',
             fontsize=11, fontweight='bold', color=C_TEXT)

dark_style(ax1, 'Untrimmed Tag')
ax1.hist(du17, bins=12, color=C_RED, edgecolor='white', alpha=0.85)
ax1.axvline(np.mean(du17), color=C_TEXT, ls='--', lw=1.5,
            label=f'Mean = {np.mean(du17):.3f}')
ax1.set_xlabel('Degradation ratio')
ax1.set_ylabel('Count')
ax1.legend(facecolor='#2a2a4a', edgecolor=C_GRID, labelcolor=C_TEXT)

dark_style(ax2, 'Trimmed Tag (k=1%)')
ax2.hist(dt17, bins=12, color=C_GRN, edgecolor='white', alpha=0.85)
ax2.axvline(np.mean(dt17), color=C_TEXT, ls='--', lw=1.5,
            label=f'Mean = {np.mean(dt17):.4f}')
ax2.set_xlabel('Degradation ratio')
ax2.set_ylabel('Count')
ax2.legend(facecolor='#2a2a4a', edgecolor=C_GRID, labelcolor=C_TEXT)

fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig4_deg_histogram_17MeV.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 5: Scorecard ──
# Compute verdicts dynamically
delta_cv_200 = abs(cv_t200 - cv_u200)
delta_mean_200 = abs(np.mean(dt200) - np.mean(du200))
delta_t = np.abs(tt17 - tu17)
med_dt = np.nanmedian(delta_t)
delta_deg = du17 - dt17
cv_ddeg = np.std(delta_deg)/np.mean(delta_deg)*100

preds = [
    ('S1', f'CV(trim)={cv_t17:.2f}% < CV(untrim)/10={cv_u17/10:.2f}%',
     cv_t17 < cv_u17/10, 'Core'),
    ('S2', f'CV(trim)={cv_t17:.2f}% < 1%',
     cv_t17 < 1.0, 'Core'),
    ('S3', f'|ΔCV|={delta_cv_200:.3f}% < 0.1% at 200 MeV',
     delta_cv_200 < 0.1, 'Secondary'),
    ('D1', f'mean(deg_T)={np.mean(dt17):.4f} < mean(deg_U)={np.mean(du17):.4f}',
     np.mean(dt17) < np.mean(du17), 'Core'),
    ('D2', f'mean(deg_T)={np.mean(dt17):.4f} < 1.2',
     np.mean(dt17) < 1.2, 'Core'),
    ('D3', f'frac(deg_T<deg_U)={np.mean(dt17<du17):.2f} > 0.8',
     np.mean(dt17 < du17) > 0.8, 'Core'),
    ('D4', f'|Δmean|={delta_mean_200:.4f} < 0.05 at 200 MeV',
     delta_mean_200 < 0.05, 'Secondary'),
    ('X1', f'median|Δt_opt|={med_dt:.2f} > 0',
     med_dt > 0, 'Diagnostic'),
    ('X2', f'CV(Δdeg)={cv_ddeg:.1f}% < 50%',
     cv_ddeg < 50, 'Diagnostic'),
]

n_confirmed = sum(1 for _,_,p,_ in preds if p)
n_core = sum(1 for _,_,p,t in preds if p and t=='Core')

fig, ax = plt.subplots(figsize=(10, 7.5))
fig.set_facecolor(C_BG)
ax.set_facecolor(C_BG)
ax.set_xlim(0, 10)
ax.set_ylim(-0.5, len(preds) + 1)
ax.axis('off')

ax.text(5, len(preds) + 0.3, 'v2.8 Prediction Scorecard (f=0.25)',
        ha='center', va='bottom', fontsize=16, fontweight='bold', color=C_TEXT)

for i, (pid, desc, passed, tier) in enumerate(reversed(preds)):
    y = i
    tier_color = {'Core': C_GOLD, 'Secondary': C_BLUE, 'Diagnostic': '#888888'}[tier]
    row_bg = '#252545' if i % 2 == 0 else '#2a2a55'
    ax.add_patch(plt.Rectangle((0.3, y - 0.35), 9.4, 0.7,
                                facecolor=row_bg, edgecolor=C_GRID, lw=0.5))
    ax.text(1.0, y, pid, ha='center', va='center', fontsize=13,
            fontweight='bold', color=tier_color,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a3e', edgecolor=tier_color, lw=1.5))
    ax.text(2.0, y, desc, ha='left', va='center', fontsize=9, color=C_TEXT)
    if passed:
        ax.text(8.8, y, 'CONFIRMED', ha='center', va='center', fontsize=11,
                fontweight='bold', color=C_GRN)
    else:
        ax.text(8.8, y, 'REFUTED', ha='center', va='center', fontsize=11,
                fontweight='bold', color=C_RED)
    ax.text(9.6, y, tier, ha='center', va='center', fontsize=8, color=tier_color, alpha=0.7)

ax.text(5, -0.4, f'Score: {n_confirmed}/9 Confirmed  |  Core: {n_core}/5 Confirmed',
        ha='center', va='top', fontsize=12, fontweight='bold', color=C_GOLD)

fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig5_scorecard.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 6: Delta deg at 17 MeV ──
delta_deg = du17 - dt17

fig, ax = plt.subplots(figsize=(10, 5))
dark_style(ax, 'v2.8 Post-Registration: Per-Seed Improvement at 17 MeV (f=0.25)\n'
              '(positive = trimmed Tag is better)')
colors = [C_GRN if dd > 0 else C_RED for dd in delta_deg]
ax.bar(seeds, delta_deg, color=colors, width=0.8, edgecolor='white', linewidth=0.3)
ax.axhline(np.mean(delta_deg), color=C_ORNG, ls='--', lw=1.5,
           label=f'Mean delta = {np.mean(delta_deg):.3f}')
ax.set_xlabel('Seed index i')
ax.set_ylabel('delta(degradation ratio) = untrimmed - trimmed')
ax.legend(facecolor='#2a2a4a', edgecolor=C_GRID, labelcolor=C_TEXT)
fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig6_delta_deg_17MeV.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 7: Cross-version CV ──
# v2.7 reference: seeds 0-49 at f=0.25 with scan_v15_endcap HV
# v2.7 published values (from v2.7 post-registration)
cv_u17_v27 = 5.80   # v2.7 untrimmed CV at 17 MeV
cv_t17_v27 = 0.13   # v2.7 trimmed CV at 17 MeV

fig, ax = plt.subplots(figsize=(10, 5.5))
dark_style(ax, 'Cross-Version Validation: CV at 17 MeV\nv2.7 (seeds 0-49) vs v2.8 (seeds 50-99)')

labels = ['Untrimmed\n(v2.7)', 'Trimmed\n(v2.7)', 'Untrimmed\n(v2.8)', 'Trimmed\n(v2.8)']

bars1 = ax.bar([0], [cv_u17_v27], width=0.6, color=C_RED, edgecolor='white', linewidth=0.5)
bars2 = ax.bar([1], [cv_t17_v27], width=0.6, color=C_GRN, edgecolor='white', linewidth=0.5)
bars3 = ax.bar([2], [cv_u17], width=0.6, color=C_RED, edgecolor='white', linewidth=0.5,
               hatch='///', alpha=0.85)
bars4 = ax.bar([3], [cv_t17], width=0.6, color=C_GRN, edgecolor='white', linewidth=0.5,
               hatch='///', alpha=0.85)

for b, v in zip([bars1[0], bars2[0], bars3[0], bars4[0]],
                [cv_u17_v27, cv_t17_v27, cv_u17, cv_t17]):
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.08,
            f'{v:.2f}%', ha='center', va='bottom', color=C_TEXT, fontweight='bold')

ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(labels)
ax.set_ylabel('CV (%)')
fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig7_cross_version_cv.png'), dpi=200, facecolor=C_BG)
plt.close()

# ── Figure 8: Trimmed Tag vs HV Comparison (bar chart) ──
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), gridspec_kw={'width_ratios': [1.2, 1]})
fig.set_facecolor(C_BG)
fig.suptitle('Trimmed Tag vs HV: Near-Equivalent Performance Without a Hard Material Veto',
             fontsize=12, fontweight='bold', color=C_TEXT)

# 17 MeV panel
dark_style(ax1, '17 MeV')
methods = ['Untrimmed\nTag', 'Trimmed\nTag (k=1%)', 'HV\n(material veto)']
vals_17 = [np.mean(du17), np.mean(dt17), np.mean(dh17)]
colors_17 = [C_RED, C_GRN, C_BLUE]
bars17 = ax1.bar(methods, vals_17, color=colors_17, width=0.55,
                 edgecolor='white', linewidth=0.8)
# Annotate values
for b, v in zip(bars17, vals_17):
    ax1.text(b.get_x() + b.get_width()/2, v + 0.005,
             f'{v:.4f}', ha='center', va='bottom', color=C_TEXT,
             fontweight='bold', fontsize=10)
# Gap annotation between trimmed and HV
gap_17 = np.mean(dt17) - np.mean(dh17)
mid_y = (np.mean(dt17) + np.mean(dh17)) / 2
ax1.annotate('', xy=(2.15, np.mean(dh17)), xytext=(2.15, np.mean(dt17)),
             arrowprops=dict(arrowstyle='<->', color=C_ORNG, lw=2))
ax1.text(2.35, mid_y, f'gap\n{gap_17:.4f}\n({gap_17/np.mean(dh17)*100:.2f}%)',
         ha='left', va='center', color=C_ORNG, fontsize=9, fontweight='bold')
ax1.set_ylabel('Mean degradation ratio')
ax1.set_ylim(0.98, max(vals_17) * 1.05)
# Break axis indication for untrimmed
ax1.axhline(1.0, color=C_TEXT, ls='--', lw=0.8, alpha=0.5)

# 200 MeV panel
dark_style(ax2, '200 MeV')
vals_200 = [np.mean(du200), np.mean(dt200), np.mean(dh200)]
bars200 = ax2.bar(methods, vals_200, color=colors_17, width=0.55,
                  edgecolor='white', linewidth=0.8)
for b, v in zip(bars200, vals_200):
    ax2.text(b.get_x() + b.get_width()/2, v + 0.0003,
             f'{v:.4f}', ha='center', va='bottom', color=C_TEXT,
             fontweight='bold', fontsize=10)
gap_200 = np.mean(dt200) - np.mean(dh200)
mid_200 = (np.mean(dt200) + np.mean(dh200)) / 2
ax2.annotate('', xy=(2.15, np.mean(dh200)), xytext=(2.15, np.mean(dt200)),
             arrowprops=dict(arrowstyle='<->', color=C_ORNG, lw=2))
ax2.text(2.35, mid_200, f'gap\n{gap_200:.4f}\n({gap_200/np.mean(dh200)*100:.2f}%)',
         ha='left', va='center', color=C_ORNG, fontsize=9, fontweight='bold')
ax2.set_ylabel('Mean degradation ratio')
ax2.set_ylim(1.0, max(vals_200) * 1.003)
ax2.axhline(1.0, color=C_TEXT, ls='--', lw=0.8, alpha=0.5)

fig.tight_layout()
fig.savefig(os.path.join(_DIR, 'fig8_trimmed_vs_hv.png'), dpi=200, facecolor=C_BG)
plt.close()

print("All 8 figures generated successfully.")
