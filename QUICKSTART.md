# Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- Garmin Connect account

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials
Copy the example environment file and add your credentials:
```bash
cp .env.example .env
```

Edit `.env` and add your Garmin Connect credentials:
```
GARMIN_EMAIL=your.email@example.com
GARMIN_PASSWORD=your_password_here
```

### 3. Run the App

**Option A: Run everything at once**
```bash
python main.py all
```

**Option B: Run step by step**
```bash
# Download data from Garmin
python main.py download

# Analyze the data
python main.py analyze

# Create visualizations
python main.py visualize
```

**Option C: Run individual scripts**
```bash
python download_data.py
python analyze_data.py
python visualize_data.py
```

## What Gets Created

After running the app, you'll find:
- `data/activities.json` - Raw activity data
- `data/activities.csv` - Processed activity data
- `data/visualizations/` - Charts and graphs

## Features

### Download (`download_data.py`)
- Connects to Garmin Connect API
- Downloads your recent activities (default: last 100)
- Saves data in JSON and CSV formats

### Analysis (`analyze_data.py`)
- Overall statistics (distance, time, calories)
- Activity type breakdown
- Monthly trends
- Personal records
- Weekly patterns

### Visualization (`visualize_data.py`)
- Activity timeline
- Monthly trends
- Activity type distribution
- Heart rate analysis
- Running pace analysis
- Weekly activity patterns

## Configuration

Edit `.env` to customize:
- `MAX_ACTIVITIES` - Number of activities to download (default: 100)
- `DATA_DIR` - Directory for data storage (default: ./data)

## Troubleshooting

**Authentication Error:**
- Verify your Garmin Connect credentials in `.env`
- Try logging into Garmin Connect website to ensure account is active

**No Data Found:**
- Run `python download_data.py` first to download data

**Missing Charts:**
- Some charts require specific data (e.g., heart rate, running pace)
- Charts will be skipped if data is not available
