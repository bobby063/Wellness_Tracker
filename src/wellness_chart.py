"""
Daily Wellness Dashboard — Final production-quality chart.
Pixel-perfect alignment grid, CB-safe palette, vertical sleep stems,
3-day rolling averages, card-style KPI panel, narrative insights.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches
import numpy as np
from scipy.interpolate import CubicSpline
import datetime
import calendar
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wellness_data

_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# ══════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════
# Spacing grid: all vertical/horizontal positions snap to 0.01 in
# axes-fraction space (≈ 10 px at 200 dpi on a 16×10 figure).
#
# Typography
#   Title:      20 pt  bold   _TEXT
#   Subtitle:   10.5 pt       _TEXT2
#   Axis label: 9 pt          _TEXT2
#   KPI value:  15 pt  bold   _TEXT
#   KPI label:  7.5 pt        _TEXT3
#   KPI unit:   6.5 pt        _TEXT3
#   Zone text:  7 pt          _TEXT2
#   Narrative:  7.8 pt italic _TEXT2
#
# Line weights
#   Smoothed:   2.4 pt  + 4 pt white glow
#   Raw dotted: 0.8 pt  alpha 0.30
#   Sleep stems:1.4 pt  alpha 0.22
#   Gridlines:  0.5 pt  alpha 0.55
# ══════════════════════════════════════════════════════════════════

_BG     = '#F8F9FB'
_CARD   = '#FFFFFF'
_GRID   = '#E8ECF1'
_BORDER = '#D4DAE3'
_TEXT   = '#1A1D23'
_TEXT2  = '#5A6270'
_TEXT3  = '#9CA3AF'

_SLEEP  = '#2A9D8F'
_MOOD   = '#8E7CC3'
_ENERGY = '#E76F51'
_ACCENT = '#CC79A7'
_FONT   = 'Segoe UI'

_SLEEP_MK  = 's'
_MOOD_MK   = 'o'
_ENERGY_MK = 'D'

_ZONE_CFG = [
    (1,  3,  '#DBEAFE', 0.30, 'Low'),
    (3,  5,  '#E0F2FE', 0.20, 'Below Avg'),
    (5,  7,  '#ECFDF5', 0.18, 'Normal'),
    (7,  9,  '#FEF9C3', 0.18, 'Above Avg'),
    (9, 10,  '#FEE2E2', 0.24, 'High'),
]

# ── Alignment constants (axes-fraction) ──────────────────────────
_L = 0.06          # unified left margin (fig-fraction)
_R = 0.92          # right margin
_PANEL_LEFT = 0.0  # inside panel axes, left edge


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _style_axes(ax):
    ax.set_facecolor(_CARD)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(axis='both', colors=_TEXT2, labelsize=8, length=0, pad=6)
    ax.yaxis.grid(True, color=_GRID, linewidth=0.5, alpha=0.55)
    ax.xaxis.grid(False)


def _draw_zones(ax, x_max):
    for y0, y1, colour, alpha, label in _ZONE_CFG:
        ax.axhspan(y0, y1, color=colour, alpha=alpha, zorder=0)
        ax.text(x_max + 0.35, (y0 + y1) / 2, label,
                va='center', ha='left', fontsize=6.5,
                color=_TEXT3, family=_FONT, clip_on=False)


def _smooth_spline(xs, ys, pts_per_day=12):
    """Return dense (x, y) arrays tracing a cubic spline through (xs, ys).
    Passes exactly through every supplied point; purely visual."""
    xs, ys = np.array(xs, dtype=float), np.array(ys, dtype=float)
    if len(xs) < 2:
        return xs, ys
    cs = CubicSpline(xs, ys)
    x_dense = np.linspace(xs[0], xs[-1], int((xs[-1] - xs[0]) * pts_per_day) + 2)
    return x_dense, cs(x_dense)


def _rolling_avg(values, window=2):
    out = []
    for i in range(len(values)):
        seg = [v for v in values[max(0, i - window + 1):i + 1] if v is not None]
        out.append(sum(seg) / len(seg) if seg else None)
    return out


def _zone_counts_for(values):
    counts = {lbl: 0 for _, _, _, _, lbl in _ZONE_CFG}
    for v in values:
        if v is None:
            continue
        for y0, y1, _, _, lbl in _ZONE_CFG:
            if y0 <= v < y1 or (y1 == 10 and v == 10):
                counts[lbl] += 1
                break
    return counts


def _trend_word(values):
    vals = [v for v in values if v is not None]
    if len(vals) < 4:
        return 'insufficient data'
    first = np.mean(vals[:len(vals) // 2])
    second = np.mean(vals[len(vals) // 2:])
    diff = second - first
    if diff > 0.4:
        return 'trending upward'
    if diff < -0.4:
        return 'trending downward'
    return 'relatively stable'


def _compute_insights(mood, energy, sleep, month_name, year):
    m = [v for v in mood if v is not None]
    e = [v for v in energy if v is not None]
    s = [v for v in sleep if v is not None]
    info = {}

    info['avg_sleep']    = f'{np.mean(s):.1f}' if s else '\u2014'
    info['avg_mood']     = f'{np.mean(m):.1f}' if m else '\u2014'
    info['avg_energy']   = f'{np.mean(e):.1f}' if e else '\u2014'
    info['days_tracked'] = str(len(m))
    info['total_days']   = str(len(mood))

    paired_sm, paired_se = [], []
    for mi, ei, si in zip(mood, energy, sleep):
        if mi is not None and si is not None:
            paired_sm.append((si, mi))
        if ei is not None and si is not None:
            paired_se.append((si, ei))

    def _corr(pairs):
        if len(pairs) < 3:
            return '\u2014'
        a, b = zip(*pairs)
        a, b = np.array(a, dtype=float), np.array(b, dtype=float)
        if np.std(a) == 0 or np.std(b) == 0:
            return '\u2014'
        r = float(np.corrcoef(a, b)[0, 1])
        strength = 'strong' if abs(r) >= 0.6 else 'mod' if abs(r) >= 0.3 else 'weak'
        sign = '+' if r > 0 else '\u2212'
        return f'{r:+.2f} ({strength} {sign})'

    info['corr_sleep_mood']   = _corr(paired_sm)
    info['corr_sleep_energy'] = _corr(paired_se)

    info['mood_zones']   = _zone_counts_for(mood)
    info['energy_zones'] = _zone_counts_for(energy)
    info['sleep_zones']  = _zone_counts_for(sleep)

    mt = _trend_word(mood)
    et = _trend_word(energy)
    st = _trend_word(sleep)
    narrative = (
        f"In {month_name} {year}, mood was {mt} (avg {info['avg_mood']}), "
        f"energy was {et} (avg {info['avg_energy']}), "
        f"and sleep averaged {info['avg_sleep']} hrs/night ({st}). "
    )
    if s:
        avg_s = np.mean(s)
        if avg_s < 6:
            narrative += 'Sleep is below the 7\u20139 hr target \u2014 consider earlier bedtimes.'
        elif avg_s >= 7:
            narrative += 'Sleep is within a healthy range \u2014 keep it up!'
        else:
            narrative += 'Sleep is slightly below optimal \u2014 small gains could boost mood & energy.'
    info['narrative'] = narrative
    return info


# ══════════════════════════════════════════════════════════════════
# MAIN CHART
# ══════════════════════════════════════════════════════════════════

def generate_chart(data_file, save_only=False):
    wellness_data.DATA_FILE = data_file
    wellness_data.initialize_data_file()

    year, month = wellness_data.get_current_month_year()
    month_name = datetime.date(year, month, 1).strftime('%B')

    mood_scores   = wellness_data.get_mood_scores()
    energy_scores = wellness_data.get_energy_scores()
    sleep_hours   = wellness_data.get_sleep_hours()

    _, days_in_month = calendar.monthrange(year, month)
    day_nums = list(range(1, days_in_month + 1))
    dates = [datetime.date(year, month, d) for d in day_nums]

    # ── Figure + GridSpec ─────────────────────────────────────────
    fig = plt.figure(figsize=(16, 10.5), facecolor=_BG)
    gs = gridspec.GridSpec(
        2, 1, height_ratios=[5, 2.2],
        hspace=0.08,
        left=_L, right=_R, top=0.89, bottom=0.03,
    )
    ax     = fig.add_subplot(gs[0])
    ax_info = fig.add_subplot(gs[1])

    _style_axes(ax)

    x_pad = 0.5
    ax.set_xlim(1 - x_pad, days_in_month + x_pad)
    ax.set_ylim(0.5, 10.5)
    ax.set_yticks(range(1, 11))

    # X-axis — every day
    ax.set_xticks(day_nums)
    ax.set_xticklabels(
        [f"{d}\n{dates[d-1].strftime('%a')}" for d in day_nums],
        fontsize=6.5, color=_TEXT2, linespacing=1.35, family=_FONT,
    )

    # ── Zone bands ───────────────────────────────────────────────
    _draw_zones(ax, days_in_month)

    # ── Weekend shading ──────────────────────────────────────────
    for d, dt in zip(day_nums, dates):
        if dt.weekday() >= 5:   # Saturday=5, Sunday=6
            ax.axvspan(d - 0.5, d + 0.5, color='#B0BEC5', alpha=0.10, zorder=0, lw=0)

    # ── Title + subtitle (aligned to _L) ─────────────────────────
    fig.text(_L, 0.955, 'Daily Wellness Dashboard',
             fontsize=20, fontweight='bold', color=_TEXT, family=_FONT)
    fig.text(_L, 0.925, f'Sleep, Mood & Energy  \u2014  {month_name} {year}',
             fontsize=10.5, color=_TEXT2, family=_FONT)

    ax.set_ylabel('Score / Hours', fontsize=9, color=_TEXT2,
                  labelpad=8, family=_FONT)

    # ── Plot helper ──────────────────────────────────────────────
    def plot_metric(data_list, colour, label, marker, zorder=5):
        valid = [(day_nums[i], v) for i, v in enumerate(data_list) if v is not None]
        if not valid:
            return
        xs, ys = zip(*valid)

        # Raw — faint dotted
        ax.plot(xs, ys, color=colour, linewidth=0.8, alpha=0.30,
                linestyle=':', zorder=zorder)

        # 2-day rolling avg — rendered as smooth spline (visual only)
        ra = _rolling_avg(data_list, window=2)
        ra_valid = [(day_nums[i], v) for i, v in enumerate(ra) if v is not None]
        if len(ra_valid) > 1:
            rx, ry = zip(*ra_valid)
            sx, sy = _smooth_spline(rx, ry)
            line, = ax.plot(sx, sy, color=colour, linewidth=2.4,
                            solid_capstyle='round', zorder=zorder + 1,
                            label=f'{label} (2d avg)')
            line.set_path_effects([
                pe.Stroke(linewidth=4.0, foreground=_CARD, alpha=0.6),
                pe.Normal(),
            ])

        # Markers — small for history, large for latest
        if len(xs) > 1:
            ax.scatter(xs[:-1], ys[:-1], color=colour, marker=marker,
                       s=36, zorder=zorder + 2, edgecolors='white',
                       linewidths=0.8, alpha=0.75)
        ax.scatter([xs[-1]], [ys[-1]], color=colour, marker=marker,
                   s=110, zorder=zorder + 3, edgecolors='white', linewidths=2)

    # ── Sleep: vertical stems + smoothed line ────────────────────
    sleep_valid = [(day_nums[i], h) for i, h in enumerate(sleep_hours) if h is not None]
    if sleep_valid:
        data_sx, data_sy = zip(*sleep_valid)  # actual data points — kept for markers

        # Vertical stems
        for x, y in zip(data_sx, data_sy):
            ax.plot([x, x], [0.5, y], color=_SLEEP, linewidth=1.4,
                    solid_capstyle='round', alpha=0.22, zorder=2)

        # Sleep 2-day rolling avg — rendered as smooth spline (visual only)
        ra = _rolling_avg(sleep_hours, window=2)
        ra_valid = [(day_nums[i], v) for i, v in enumerate(ra) if v is not None]
        if len(ra_valid) > 1:
            rx, ry = zip(*ra_valid)
            spline_sx, spline_sy = _smooth_spline(rx, ry)
            line, = ax.plot(spline_sx, spline_sy, color=_SLEEP, linewidth=2.4,
                            solid_capstyle='round', zorder=3,
                            label='Sleep (2d avg)')
            line.set_path_effects([
                pe.Stroke(linewidth=4.0, foreground=_CARD, alpha=0.6),
                pe.Normal(),
            ])

        # Markers — placed at actual data points (not spline)
        if len(data_sx) > 1:
            ax.scatter(data_sx[:-1], data_sy[:-1], color=_SLEEP, marker=_SLEEP_MK,
                       s=36, zorder=4, edgecolors='white',
                       linewidths=0.8, alpha=0.75)
        ax.scatter([data_sx[-1]], [data_sy[-1]], color=_SLEEP, marker=_SLEEP_MK,
                   s=110, zorder=5, edgecolors='white', linewidths=2)

    # ── Mood & Energy ────────────────────────────────────────────
    plot_metric(mood_scores,   _MOOD,   'Mood',   _MOOD_MK,   zorder=7)
    plot_metric(energy_scores, _ENERGY, 'Energy', _ENERGY_MK, zorder=9)

    # ── "Today" line ─────────────────────────────────────────────
    today = datetime.date.today()
    if today.year == year and today.month == month:
        td = today.day
        ax.axvline(td, color=_ACCENT, linewidth=1.0, linestyle=(0, (4, 3)),
                   alpha=0.50, zorder=1)
        ax.text(td, 10.42, 'Today', ha='center', fontsize=7.5,
                color=_CARD, fontweight='bold', family=_FONT,
                bbox=dict(boxstyle='round,pad=0.25', fc=_ACCENT,
                          ec='none', alpha=0.82), zorder=12)

    # ── Legend (pill, top-right) ─────────────────────────────────
    leg = ax.legend(loc='upper right', fontsize=8, frameon=True,
                    facecolor=_CARD, edgecolor=_BORDER, framealpha=0.92,
                    ncol=3, bbox_to_anchor=(1.0, 1.10),
                    borderpad=0.6, handlelength=1.8, columnspacing=1.2,
                    handletextpad=0.5)
    leg.get_frame().set_boxstyle('round,pad=0.3')
    leg.get_frame().set_linewidth(0.5)
    for t in leg.get_texts():
        t.set_color(_TEXT)
        t.set_fontfamily(_FONT)

    # ══════════════════════════════════════════════════════════════
    # INSIGHTS PANEL — grid-aligned
    # ══════════════════════════════════════════════════════════════
    info = _compute_insights(mood_scores, energy_scores, sleep_hours,
                             month_name, year)

    # Use data coordinates for the panel so card widths are mathematically exact.
    # xlim = (0, N_CARDS): card i occupies [i, i+1] in x-space.
    # ylim = (0, 1): full vertical range.
    N_CARDS = 6
    GAP_D   = 0.10   # gap in data units between cards
    ax_info.set_facecolor(_BG)
    for sp in ax_info.spines.values():
        sp.set_visible(False)
    ax_info.set_xticks([])
    ax_info.set_yticks([])
    ax_info.set_xlim(0, N_CARDS)
    ax_info.set_ylim(0, 1)

    # ── Thin divider at top of panel (transAxes) ──────────────────
    ax_info.axhline(0.97, color=_GRID, linewidth=0.6, zorder=1)

    # ── KPI cards — each card occupies exactly 1 data unit ───────
    card_h = 0.58   # in data-y units (ylim 0-1)
    card_y = 0.36
    bar_h  = 0.065

    kpi_data = [
        ('Avg Sleep',         info['avg_sleep'],          'hrs / night',  _SLEEP),
        ('Avg Mood',          info['avg_mood'],            'out of 10',    _MOOD),
        ('Avg Energy',        info['avg_energy'],          'out of 10',    _ENERGY),
        ('Days Tracked',      info['days_tracked'],
         f'of {info["total_days"]} days',                                  _TEXT2),
        ('Sleep\u2013Mood',   info['corr_sleep_mood'],     'correlation',  _SLEEP),
        ('Sleep\u2013Energy', info['corr_sleep_energy'],   'correlation',  _ENERGY),
    ]

    for i, (label, value, unit, accent) in enumerate(kpi_data):
        x0 = i + GAP_D / 2
        x1 = i + 1 - GAP_D / 2
        cw = x1 - x0
        mid = (x0 + x1) / 2

        # Card background
        ax_info.add_patch(mpatches.Rectangle(
            (x0, card_y), cw, card_h,
            facecolor=_CARD, edgecolor=_BORDER, linewidth=0.5,
            zorder=2, clip_on=False))

        # Accent bar — sits flush at top inside card
        ax_info.add_patch(mpatches.Rectangle(
            (x0, card_y + card_h - bar_h), cw, bar_h,
            facecolor=accent, edgecolor='none', alpha=0.72,
            zorder=3, clip_on=False))

        # Label (top)
        ax_info.text(mid, card_y + card_h - bar_h - 0.03, label,
                     ha='center', va='top',
                     fontsize=7.5, color=_TEXT3, family=_FONT, zorder=4)
        # Value (middle)
        ax_info.text(mid, card_y + card_h / 2 - 0.01, value,
                     ha='center', va='center',
                     fontsize=15, fontweight='bold', color=_TEXT,
                     family=_FONT, zorder=4)
        # Unit (bottom)
        ax_info.text(mid, card_y + 0.04, unit,
                     ha='center', va='bottom',
                     fontsize=6.5, color=_TEXT3, family=_FONT, zorder=4)

    # ── Zone breakdown — three equal segments in data space ───────
    zone_y = 0.22
    seg_w  = N_CARDS / 3   # = 2.0

    def _zone_line(metric_name, zones, colour, seg_idx):
        parts = [f'{lbl}: {cnt}' for lbl, cnt in zones.items() if cnt > 0]
        txt = '  \u00B7  '.join(parts) if parts else '\u2014'
        x0 = seg_idx * seg_w + GAP_D / 2
        ax_info.plot([x0, x0 + 0.22], [zone_y, zone_y], color=colour,
                     linewidth=2.5, solid_capstyle='round', zorder=3, clip_on=False)
        ax_info.text(x0 + 0.30, zone_y, f'{metric_name}   {txt}',
                     fontsize=7, color=_TEXT2, family=_FONT,
                     va='center', zorder=3)

    _zone_line('Mood',   info['mood_zones'],   _MOOD,   0)
    _zone_line('Energy', info['energy_zones'], _ENERGY, 1)
    _zone_line('Sleep',  info['sleep_zones'],  _SLEEP,  2)

    # ── Narrative ─────────────────────────────────────────────────
    ax_info.text(GAP_D / 2, 0.12, info['narrative'],
                 fontsize=7.8, color=_TEXT2, family=_FONT,
                 va='top', style='italic', wrap=True)

    # ── Save ─────────────────────────────────────────────────────
    out = os.path.join(_PROJECT_ROOT, f'wellness_chart_{year}_{month:02d}.png')
    fig.savefig(out, dpi=200, facecolor=fig.get_facecolor(),
                bbox_inches='tight', pad_inches=0.25)
    plt.close(fig)
    if not save_only:
        plt.show()
    return out


if __name__ == '__main__':
    save_only = '--save-only' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    data_file = args[0] if args else wellness_data.DATA_FILE
    path = generate_chart(data_file, save_only=save_only)
    print(f"Chart saved as '{path}'")

 
