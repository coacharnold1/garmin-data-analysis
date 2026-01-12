# Configurable Analysis Periods

## Overview
You can now choose how many days of training data to analyze for performance metrics (HR zones, run decoupling, swim SWOLF, bike efficiency).

## Configuration

Edit your `.env` file and set `ANALYSIS_DAYS`:

```bash
ANALYSIS_DAYS=60
```

## Options

| Days | Use Case | Description |
|------|----------|-------------|
| **7** | Recent Trends | Best for checking recent training block or returning from injury/break |
| **30** | Monthly View | Good for identifying patterns within a mesocycle |
| **60** | Long-term Patterns | **DEFAULT** - Recommended for accurate training distribution analysis |
| **90** | Seasonal View | Useful for reviewing a full training season |

## Why Split Periods?

### Performance Metrics (Configurable: 7-90 days)
- **HR Zone Distribution**: Needs longer view to see true training patterns
- **Run Decoupling**: Requires multiple runs to establish trends
- **Swim SWOLF**: Benefits from more data points
- **Bike Efficiency**: Trends emerge over weeks/months

### Recovery Metrics (Always 7 days)
- **Resting Heart Rate**: Current recovery state
- **Body Battery**: Recent energy levels
- **Sleep Score**: Recent sleep quality
- **Stress**: Current stress load

### Training Load
- **ACWR**: Always uses 7-day acute / 28-day chronic ratio (standard)

## Examples

### Default (60 days) - Recommended
```bash
ANALYSIS_DAYS=60
```
- Analyzes last 2 months of training
- Reveals true training distribution patterns
- Best for periodization planning

### After Time Off (7 days)
```bash
ANALYSIS_DAYS=7
```
- Shows only recent return-to-training activities
- Useful after injury, illness, or vacation
- Prevents skewed data from old training

### Build Analysis (30 days)
```bash
ANALYSIS_DAYS=30
```
- Reviews current training block
- Good for mid-block adjustments
- Balances recency with sufficient data

## How It Works

1. **Edit `.env`**: Change `ANALYSIS_DAYS=60` to your desired period
2. **Run Analysis**: Execute `python main.py coach` or use GUI "Coach Brief" button
3. **View Results**: The output will show:
   ```
   Analyzing 31 activities from last 60 days (100 total)
   To change analysis period, set ANALYSIS_DAYS in .env (options: 7, 30, 60, 90)
   ```

## Recommendations by Scenario

### Returning from Break/Injury
```bash
ANALYSIS_DAYS=7
```
Focus on current training load and recent patterns.

### Building Base (Off-season)
```bash
ANALYSIS_DAYS=60  # or 90
```
See long-term aerobic development and Z1-Z2 time.

### Race-Specific Block
```bash
ANALYSIS_DAYS=30
```
Analyze current block's intensity distribution.

### Post-Race Analysis
```bash
ANALYSIS_DAYS=90
```
Review entire race preparation period.

## Notes

- Recovery metrics (RHR, Body Battery, Sleep, Stress) always use 7 days
- ACWR always uses 7-day acute / 28-day chronic (injury prediction standard)
- FTP calculation always uses all available power data (best 20min effort)
- Minimum recommended: 7 days (at least a few workouts for meaningful data)
- Maximum supported: 90 days (more than 3 months may include outdated fitness level)
