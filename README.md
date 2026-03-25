# Daily Wellness Tracker

A desktop wellness tracking application for logging and visualising daily Sleep, Mood, and Energy scores. Built with Python, Tkinter, and Matplotlib.

---

## Prerequisites

- **Python 3.10+** — download from [python.org](https://www.python.org/downloads/)  
  Make sure to check **"Add Python to PATH"** during installation.
- **Tkinter** — included with the standard Python installer on Windows; no extra steps needed.

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/bobby063/wellness-tracker
cd SavedPath\wellness-tracker

# 2. (Optional but recommended) create a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

After setup just use the `.vbs` shortcuts below — they launch silently with no terminal flash.

---

## Quick Start

| Script | Action |
|---|---|
| `run_wellness_tracker_input.vbs` | Open the data entry GUI (normal daily use) |
| `regenerate_chart.vbs` | Rebuild the chart manually — use this if you edited the CSV directly |

Double-click `run_wellness_tracker_input.vbs` each day to log your scores. The chart PNG is saved and opened automatically on every save.

---

## Features

- Modern, colorblind-safe wellness chart with smooth lines and color-matched markers
- Large, easy-to-read daily score dots (historical and latest day)
- Data privacy: your wellness data stays local and is never committed to git
- One-click GUI for daily entry, no terminal required
- Automated insights and trends panel
- Fully documented, modular codebase

---

## Project Structure

```
wellness-tracker/
├── src/
│   ├── wellness_input.py               # Tkinter GUI — main entry point
│   ├── wellness_chart.py               # Matplotlib chart generator
│   └── wellness_data.py                # CSV data layer
├── data/
│   └── wellness_data_YYYY_MM.csv       # one file per month (git-ignored)
├── run_wellness_tracker_input.vbs      # double-click launcher (no terminal flash)
├── run_wellness_tracker_input.bat
├── regenerate_chart.vbs                # manual chart rebuild launcher
├── regenerate_chart.bat
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Architecture

### `wellness_data.py` — Data Layer

- **Storage format**: CSV with columns `date, mood_score, energy_score, sleep_hours`
- **`initialize_data_file()`** — creates a new monthly CSV if it doesn't exist; auto-migrates legacy files missing the `energy_score` or `sleep_hours` columns by appending them
- **`get_mood_scores()` / `get_energy_scores()` / `get_sleep_hours()`** — return a list of 28–31 values (`None` for untracked days), one per day of the current month, by parsing the CSV date column against the configured `year`/`month`
- **`save_mood_score()` / `save_energy_score()` / `save_sleep_hours()`** — upsert a row for the given day (read-modify-write on the CSV)
- **`DATA_FILE`** module-level variable is overridden at runtime by `wellness_chart.generate_chart()` to support arbitrary month/year files

### `wellness_input.py` — GUI Layer

- **Framework**: Tkinter with fully custom canvas widgets (no ttk theming)
- **`ModernSlider`** — custom `Canvas`-based slider; `TRACK_H=4`, `THUMB_R=8`; emits a callback on drag
- **`RoundButton`** — `Frame + Canvas` composition (avoids a TclError on `Canvas` subclassing); draws a rounded rectangle with hover state
- **Window**: `520×580`, fixed size, title "Daily Wellness Tracker"
- **Colour tokens**: `BG="#F5F7FA"`, `CARD="#FFFFFF"`, `MOOD_C="#4F8EF7"`, `ENERGY_C="#10B981"`, `SLEEP_C="#7C5CFC"`
- **Font**: Segoe UI throughout
- **Save flow**: validates day selection → calls `wellness_data.save_*()` for all three metrics → calls `wellness_chart.generate_chart()` via direct import → opens the PNG via `os.startfile()` → updates status bar label (no popup dialog)
- **Chart flow**: `generate_chart_silent()` saves PNG silently; `view_chart()` calls `generate_chart(save_only=False)` to open the viewer

### `wellness_chart.py` — Chart Layer

- **Backend**: `matplotlib.Agg` (no display dependency; avoids subprocess/sys.executable mismatch)
- **Figure size**: `16 × 10.5 inches` at `200 dpi`
- **Layout**: `GridSpec(2, 1, height_ratios=[5, 2.2])` — chart row + insights panel row

#### Chart Area (top subplot)
- **X-axis**: every 3rd day labelled (`day\nWeekday`); unlabelled days get minor tick marks only — reduces clutter while preserving readability
- **Y-axis**: 1–10, integer ticks; horizontal gridlines only (`yaxis.grid`)
- **Zone bands**: 5 `axhspan` fills (Low / Below Avg / Normal / Above Avg / High) at 18–30% opacity; zone labels drawn to the right with `clip_on=False`
- **Sleep**: vertical stems (`alpha=0.22`) from the baseline to each raw data point + a 2-day rolling-average smoothed line on top
- **Mood / Energy**: raw data as faint dotted lines (`alpha=0.30, linestyle=':'`) + 2-day rolling-average solid lines with a white glow (`patheffects.Stroke` foreground white, then `Normal`)
- **Markers**: large, color-matched shaped markers on historical points (`s=36, alpha=0.75`); extra-large marker on the latest point (`s=110`); distinct shapes per metric: Sleep=square, Mood=circle, Energy=diamond; marker color always matches the line
- **"Today" line**: rose `#CC79A7` dashed vertical with a pill-shaped label badge
- **Legend**: 3-column pill legend anchored to top-right of the axes area

#### Insights Panel (bottom subplot)
- **Coordinate system**: `xlim=(0, 6)`, `ylim=(0, 1)` — cards are drawn in **data space** (not axes-fraction), so each card occupies exactly 1 data unit of width. This eliminates all fraction-arithmetic alignment drift.
- **KPI cards**: 6 `mpatches.Rectangle` patches with a colour-coded accent bar flush at the top. Each card: label (7.5pt muted), bold value (15pt), unit caption (6.5pt muted)
- **Zone breakdown row**: colour-coded line bullets + zone counts for Mood / Energy / Sleep in three equal segments
- **Narrative summary**: 2–3 sentence italic trend interpretation generated by `_compute_insights()`

#### Key Helper Functions
| Function | Purpose |
|---|---|
| `_rolling_avg(values, window)` | Trailing rolling mean over non-None values |
| `_compute_insights(mood, energy, sleep, ...)` | Computes averages, Pearson correlations (sleep–mood, sleep–energy), zone counts, trend direction, narrative string |
| `_trend_word(values)` | Compares first half vs second half mean; returns "trending upward / downward / relatively stable" |
| `_zone_counts_for(values)` | Bins values into the 5 zones and returns a count dict |
| `_style_axes(ax)` | Removes spines, sets card background, configures tick style |
| `_draw_zones(ax, x_max)` | Draws `axhspan` zone fills + right-edge zone labels |

---

## Screenshots

![Sample Wellness Chart](assets/wellness_chart_2026_03%20Example.png)

![Input App Screenshot](assets/Input%20App.png)

---

## Colour Palette — Oura / Apple Health Style

| Metric | Colour | Hex |
|---|---|---|
| Sleep | Soft teal | `#2A9D8F` |
| Mood | Muted purple | `#8E7CC3` |
| Energy | Warm coral | `#E76F51` |
| "Today" marker | Rose | `#CC79A7` |
| Background | Cool off-white | `#F8F9FB` |
| Card | White | `#FFFFFF` |

All three metric colours are colour-blind-safe with consistent perceptual luminance (distinguishable under deuteranopia and protanopia).

---

## Data File Format

```csv
date,mood_score,energy_score,sleep_hours
2026-03-01,,, 
2026-03-08,6,7,6
2026-03-09,5,6,5
```

- One row per day of the month, created on initialisation
- Empty cells = untracked days (read back as `None`)
- File is named `wellness_data_YYYY_MM.csv` and lives in `data\`

---

## Notes

- The generated chart PNG (`wellness_chart_YYYY_MM.png`) is saved to the project root and is git-ignored.
- Your CSV data files are git-ignored — no personal data is committed to the repo.
- On first run the app creates the `data/` folder and current month's CSV automatically.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
