@echo off
echo Installing required packages...
python -m pip install -r requirements.txt --quiet
echo Starting Daily Wellness Tracker...
echo (Select any month/year, chart updates automatically when you save scores)
python src\wellness_input.py

 
