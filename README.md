# Garmin Data Analysis App

A Python application to download and analyze your Garmin Connect activity data.

## Features

- 🔐 Secure authentication with Garmin Connect
- 📥 Download activities (runs, cycling, swimming, etc.)
- 📊 Analyze activity metrics (distance, pace, heart rate, etc.)
- 🏊🚴🏃 **Triathlon-specific training analysis** with TSS, load balance, and sport metrics
- 🏆 **Elite Coaching Brief** - Comprehensive training analysis with adaptive recommendations
- 📈 Visualize trends and statistics
- 💾 Store data locally for offline analysis
- 🖥️ **Graphical User Interface** for easy interaction

## Setup

### Prerequisites

- Python 3.8 or higher
- Garmin Connect account

### Installation

1. Clone or navigate to this repository:
```bash
cd /home/fausto/Garmin-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Garmin credentials:
```bash
cp .env.example .env
```

Edit `.env` and add your Garmin Connect email and password:
```
GARMIN_EMAIL=your.email@example.com
GARMIN_PASSWORD=your_password
```

## Usage

### Download Your Activity Data

```bash
python download_data.py
```

This will:
- Authenticate with Garmin Connect
- Download your recent activities
- Save them to the `data/` folder as JSON and CSV files

### Analyze Your Data

```bash
python analyze_data.py
```

This will:
- Load your activity data
- Calculate statistics (total distance, average pace, etc.)
- Show trends over time

### Triathlon Training Analysis

```bash
python main.py triathlon
```

Advanced triathlon-specific analysis including:
- Training Stress Score (TSS) calculation
- Acute vs Chronic load balance (7d vs 42d)
- ACWR (Acute:Chronic Workload Ratio) for injury prevention
- Sport-specific metrics (swim/bike/run)
- Recovery readiness and training recommendations

### Elite Coaching Brief

```bash
python main.py coach
```

Comprehensive "Coach's Brief" with:
- **Physiological Baseline**: HRV status, resting HR trends
- **Training Load**: ACWR, injury risk assessment, HR zone distribution
- **Efficiency Metrics**: Aerobic decoupling, swim SWOLF, bike efficiency factor
- **Triathlon-Specific**: Brick performance analysis
- **🚴 TrainerRoad Workout Recommendations**: Intelligent workout selection based on your current state
- **Adaptive Recommendations**: Based on your current training state
- **JSON Export**: Copy to AI coaches for personalized advice!

See [COACHING_BRIEF_FEATURES.md](COACHING_BRIEF_FEATURES.md) for detailed documentation.
See [TRAINERROAD_GUIDE.md](TRAINERROAD_GUIDE.md) for TrainerRoad workout guidance.

### Visualize Your Data

```bash
python visualize_data.py
```

This will:
- Create charts showing activity trends
- Visualize heart rate zones
- Display pace/speed analysis

### GUI Mode

Launch the graphical interface:

```bash
python gui.py
```

Features:
- 📥 Download button
- 📊 Analyze button
- 🏊🚴🏃 Triathlon analysis button
- 🏆 Coach Brief button
- 📈 Visualize button
- ⚡ Run All (complete pipeline)
- 🖼️ Image browser with prev/next navigation

### Complete Pipeline

Run everything at once:

```bash
python main.py all
```

Executes: Download → Analyze → Triathlon → Coach Brief → Visualize

## Data Structure

Downloaded data is stored in `data/` folder:
- `activities.json` - Raw activity data
- `activities.csv` - Processed activity summary
- `activity_details_<id>.json` - Detailed data for each activity

## Security Notes

- Never commit your `.env` file to version control
- Your Garmin credentials are stored locally only
- Consider using a Garmin API token for enhanced security

## Troubleshooting

**Authentication Issues**: Ensure your Garmin email and password are correct in `.env`. If you use 2FA, you may need to generate an app-specific password.

**Missing Data**: The free Garmin Connect API has rate limits. If you have many activities, download them in batches.

## License

MIT
