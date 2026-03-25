import csv
import os
from datetime import datetime, date
import calendar

# BASE_DIR is the data/ folder relative to this src/ file
_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

DATA_FILE = os.path.join(_BASE_DIR, 'wellness_data.csv')  # Default, will be overridden

def initialize_data_file():
    """Create the data file if it doesn't exist, or migrate if needed"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'mood_score', 'energy_score', 'sleep_hours'])
            year, month = get_current_month_year()
            _, days = calendar.monthrange(year, month)
            for day in range(1, days + 1):
                date_str = f"{year}-{month:02d}-{day:02d}"
                writer.writerow([date_str, '', '', ''])
    else:
        _migrate_data_file()

def _migrate_data_file():
    """Add missing columns (sleep_hours, energy_score) to existing CSV"""
    with open(DATA_FILE, 'r') as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames or []
        needs_sleep = 'sleep_hours' not in fields
        needs_energy = 'energy_score' not in fields
        if not needs_sleep and not needs_energy:
            return
        rows = list(reader)
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date', 'mood_score', 'energy_score', 'sleep_hours'])
        for row in rows:
            writer.writerow([
                row['date'],
                row.get('mood_score', ''),
                row.get('energy_score', ''),
                row.get('sleep_hours', '')
            ])

def get_current_month_year():
    """Get the current month and year from the data file name.
    Filename format: wellness_data_YYYY_MM.csv -> parts[-2]=YYYY, parts[-1]=MM
    """
    basename = os.path.basename(DATA_FILE)
    if '_' in basename:
        parts = basename.replace('.csv', '').split('_')
        if len(parts) >= 4:
            try:
                year = int(parts[-2])
                month = int(parts[-1])
                return year, month
            except:
                pass
    # Default to current month
    now = datetime.now()
    return now.year, now.month

def load_data():
    """Load wellness data - returns {date: {'mood_score': val, 'energy_score': val, 'sleep_hours': val}}"""
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                date_str = row['date']
                if '-' in date_str:
                    norm_date = date_str
                elif '/' in date_str:
                    try:
                        d, m, y = date_str.split('/')
                        norm_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    except Exception:
                        norm_date = date_str
                else:
                    norm_date = date_str
                data[norm_date] = {
                    'mood_score': row['mood_score'] if row.get('mood_score') else None,
                    'energy_score': row.get('energy_score') if row.get('energy_score') else None,
                    'sleep_hours': row.get('sleep_hours') if row.get('sleep_hours') else None
                }
    return data

# Keep old name as alias for backwards compatibility within this session
load_mood_data = load_data

def _write_data(data):
    """Write all data back to CSV"""
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['date', 'mood_score', 'energy_score', 'sleep_hours'])
        for d in sorted(data.keys()):
            entry = data[d]
            writer.writerow([
                d,
                entry.get('mood_score') or '',
                entry.get('energy_score') or '',
                entry.get('sleep_hours') or ''
            ])

def save_mood_score(date_str, score):
    """Save a mood score for a specific date"""
    data = load_data()
    if date_str in data:
        data[date_str]['mood_score'] = score
    else:
        data[date_str] = {'mood_score': score, 'energy_score': None, 'sleep_hours': None}
    _write_data(data)

def save_energy_score(date_str, score):
    """Save an energy score for a specific date"""
    data = load_data()
    if date_str in data:
        data[date_str]['energy_score'] = score
    else:
        data[date_str] = {'mood_score': None, 'energy_score': score, 'sleep_hours': None}
    _write_data(data)

def save_sleep_hours(date_str, hours):
    """Save sleep hours for a specific date"""
    data = load_data()
    if date_str in data:
        data[date_str]['sleep_hours'] = hours
    else:
        data[date_str] = {'mood_score': None, 'energy_score': None, 'sleep_hours': hours}
    _write_data(data)

def get_mood_scores():
    """Get mood scores as a list for the current month"""
    year, month = get_current_month_year()
    _, days = calendar.monthrange(year, month)
    data = load_data()
    scores = []
    for day in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        entry = data.get(date_str, {})
        score = entry.get('mood_score') if isinstance(entry, dict) else entry
        try:
            scores.append(float(score))
        except (TypeError, ValueError):
            scores.append(None)
    return scores

def get_energy_scores():
    """Get energy scores as a list for the current month"""
    year, month = get_current_month_year()
    _, days = calendar.monthrange(year, month)
    data = load_data()
    scores = []
    for day in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        entry = data.get(date_str, {})
        score = entry.get('energy_score') if isinstance(entry, dict) else None
        try:
            scores.append(float(score))
        except (TypeError, ValueError):
            scores.append(None)
    return scores

def get_sleep_hours():
    """Get sleep hours as a list for the current month"""
    year, month = get_current_month_year()
    _, days = calendar.monthrange(year, month)
    data = load_data()
    hours = []
    for day in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        entry = data.get(date_str, {})
        h = entry.get('sleep_hours') if isinstance(entry, dict) else None
        try:
            hours.append(float(h))
        except (TypeError, ValueError):
            hours.append(None)
    return hours
