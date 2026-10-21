# -*- coding: utf-8 -*-
"""Generate Figure 3.1 (high-level architecture) and Figure 3.2
(emulator self-validation detail) as PNGs using matplotlib."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

plt.rcParams['font.family'] = 'DejaVu Sans'

C_GEN = '#E8F1FB'; C_GEN_E = '#2E5395'
C_FC = '#FBF3E3'; C_FC_E = '#B8860B'
C_SIM = '#EAF6EC'; C_SIM_E = '#3A7D44'
C_EV = '#FDECEA'; C_EV_E = '#B03A2E'
C_DASH = '#F3EAF6'; C_DASH_E = '#7D3C98'


def box(ax, x, y, w, h, face, edge, title, lines, title_size=9.5, body_size=8.2,
        title_weight='bold', lw=1.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle='round,pad=0.02,rounding_size=0.03',
                 linewidth=lw, edgecolor=edge, facecolor=face))
    cx = x + w / 2
    n_titles = title.count('\n') + 1
    # body text starts below the (possibly multi-line) title
    title_h = 0.11 + 0.16 * (n_titles - 1)
    body_top = y + h - title_h - 0.17
    ax.text(cx, y + h - 0.11, title, ha='center', va='top',
            fontsize=title_size, fontweight=title_weight, color=edge)
    if lines:
        ax.text(cx, body_top, '\n'.join(lines), ha='center', va='top',
                fontsize=body_size, color='#222222')


def arrow(ax, p1, p2, label='', color='#333333', style='-|>', lw=1.5,
          dashed=False, rad=0.0, label_off=(0, 0.03), fs=7.6):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14,
                        lw=lw, color=color,
                        linestyle=(0, (5, 3)) if dashed else 'solid',
                        connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(a)
    if label:
        mx = (p1[0] + p2[0]) / 2 + label_off[0]
        my = (p1[1] + p2[1]) / 2 + label_off[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=fs,
                style='italic', color=color,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))


# ================= FIGURE 3.1 =================
fig, ax = plt.subplots(figsize=(12.5, 7.4))
ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis('off')

# component containers
box(ax, 0.3, 2.6, 3.1, 3.5, C_GEN, C_GEN_E, '1. SYNTHETIC WORLD\nGENERATOR',
    ['', 'stores, products,', 'warehouse, rules', '', 'daily sales history', '(training window)', '',
     'hidden future true demand', '(ground truth,', 'evaluation-only)'])
box(ax, 4.4, 4.0, 3.3, 2.2, C_FC, C_FC_E, '2. FORECASTER (pluggable)',
    ['predict(history, horizon) -> forecasts', '',
     '(a) Error-injection emulator  [MUST]', 'controllable bias/variance/drift', '',
     '(b) Optional real model  [SHOULD]', 'LightGBM / statistical, same interface'])
box(ax, 4.4, 0.5, 3.3, 2.1, C_SIM, C_SIM_E, '3. REPLENISHMENT\nSIMULATOR',
    ['', 'rules: min stock, pack size,', 'warehouse availability', '', 'daily ship decisions,', 'inventory, stock-outs'])
box(ax, 8.5, 2.2, 3.9, 3.2, C_EV, C_EV_E, '4. EVALUATION FRAMEWORK',
    ['(core deliverable)', '', 'forecast vs true demand', 'WAPE / MAPE / bias', '',
     'forecast vs shipped', 'deviation cause:', 'model / stock / rule / other', '',
     'outcomes: stock-outs,', 'overstock, lost sales'])
box(ax, 8.7, 0.4, 3.5, 0.95, C_DASH, C_DASH_E, '5. DASHBOARD',
    ['Streamlit - store / category / season drill-downs'])

# arrows
arrow(ax, (3.4, 4.55), (4.4, 5.0), 'history', label_off=(-0.35, 0.05))
arrow(ax, (3.4, 1.55), (4.4, 1.55), 'rules, catalog, warehouse', label_off=(0, 0.1))
arrow(ax, (7.7, 5.0), (8.5, 4.35), 'forecasts', rad=0.15, label_off=(0.15, 0.12))
arrow(ax, (7.7, 1.55), (8.5, 2.6), 'decisions + outcomes', rad=-0.15, label_off=(0.3, 0.14))
# ground truth: routed BELOW the forecaster box to avoid crossing it
arrow(ax, (1.85, 2.6), (8.5, 2.55), 'ground truth (evaluation only)',
      color='#B03A2E', dashed=True, rad=0.12, label_off=(-2.4, -0.28))
arrow(ax, (10.45, 2.2), (10.45, 1.35), 'metrics + causes', label_off=(0.95, 0.02))

ax.text(6.5, 7.6, 'Figure 3.1 - High-Level System Architecture',
        ha='center', fontsize=12, fontweight='bold', color='#1F3864')
fig.tight_layout()
fig.savefig(r'C:\Users\KaganSahin\Desktop\replenishment-decision-quality\docs\design\architecture.png',
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)

# ================= FIGURE 3.2 =================
fig, ax = plt.subplots(figsize=(11.5, 6.0))
ax.set_xlim(0, 12); ax.set_ylim(0, 6.4); ax.axis('off')

box(ax, 0.3, 3.1, 3.2, 1.8, C_FC, C_FC_E, 'EMULATOR (2a)',
    ['', 'known-cause injection:', 'bias / variance / seasonal drift', '+ seeded stock & rule limits'])
box(ax, 0.3, 0.4, 3.2, 1.6, C_SIM, C_SIM_E, 'REPLENISHMENT\nSIMULATOR (3)',
    ['', 'applies business rules', '-> shipped vs requested'])
box(ax, 4.5, 1.5, 3.2, 2.6, C_EV, C_EV_E, 'EVALUATION\nFRAMEWORK (4)',
    ['', 'classifies each deviation', 'model / stock / rule / other'])
box(ax, 8.7, 1.7, 3.0, 2.1, C_DASH, C_DASH_E, 'KNOWN-ANSWER\nTEST (NFR-03b)',
    ['', 'expected cause = injected cause', 'PASS / FAIL'])

arrow(ax, (3.5, 3.9), (4.5, 3.4), 'forecasts w/ known cause', rad=0.1,
      label_off=(-0.15, 0.1))
arrow(ax, (3.5, 1.2), (4.5, 2.0), 'decisions', rad=-0.1, label_off=(-0.1, -0.12))
arrow(ax, (7.7, 2.75), (8.7, 2.75), 'classified causes', label_off=(0, 0.12))
ax.text(6.0, 4.65, 'emulator injects cause X  =>  framework must output X',
        ha='center', fontsize=9, style='italic', color='#7D3C98',
        bbox=dict(boxstyle='round,pad=0.25', fc='#F3EAF6', ec='#7D3C98', lw=0.9))
ax.text(6.0, 5.85, 'Figure 3.2 - Forecaster Self-Validation (Known-Answer Loop)',
        ha='center', fontsize=12, fontweight='bold', color='#1F3864')
fig.tight_layout()
fig.savefig(r'C:\Users\KaganSahin\Desktop\replenishment-decision-quality\docs\design\emulator-selfvalidation.png',
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)

print('done')
