# Daily Wellness Tracker

A desktop wellness tracking application for logging and visualising daily Sleep, Mood, and Energy scores. Built with Python, Tkinter, and Matplotlib.


## Prerequisites

  Make sure to check **"Add Python to PATH"** during installation.


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


## Quick Start

| Script | Action |
|---|---|
| `run_wellness_tracker_input.vbs` | Open the data entry GUI (normal daily use) |
| `regenerate_chart.vbs` | Rebuild the chart manually — use this if you edited the CSV directly |

Double-click `run_wellness_tracker_input.vbs` each day to log your scores. The chart PNG is saved and opened automatically on every save.


## Features



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


## Architecture

### `wellness_data.py` — Data Layer


### `wellness_input.py` — GUI Layer


### `wellness_chart.py` — Chart Layer


#### Chart Area (top subplot)

#### Insights Panel (bottom subplot)

#### Key Helper Functions
| Function | Purpose |
|---|---|
| `_rolling_avg(values, window)` | Trailing rolling mean over non-None values |
| `_compute_insights(mood, energy, sleep, ...)` | Computes averages, Pearson correlations (sleep–mood, sleep–energy), zone counts, trend direction, narrative string |
| `_trend_word(values)` | Compares first half vs second half mean; returns "trending upward / downward / relatively stable" |
| `_zone_counts_for(values)` | Bins values into the 5 zones and returns a count dict |
| `_style_axes(ax)` | Removes spines, sets card background, configures tick style |
| `_draw_zones(ax, x_max)` | Draws `axhspan` zone fills + right-edge zone labels |


## Screenshots

![Sample Wellness Chart](assets/wellness_chart_2026_03%20Example.png)

![Input App Screenshot](assets/Input%20App.png)


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


## Data File Format

```csv
date,mood_score,energy_score,sleep_hours
2026-03-01,,, 
2026-03-08,6,7,6
2026-03-09,5,6,5
```



## Notes


## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
 
