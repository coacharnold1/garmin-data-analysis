# 🏆 Elite Coaching Brief - Feature Documentation

## Overview
Implements Gemini AI's elite-level coaching recommendations for comprehensive triathlon training analysis. This feature generates a structured "Coach's Brief" with metrics designed to guide adaptive training plans.

## Implementation Date
January 4, 2026

## Features Implemented

### 1️⃣ Physiological Baseline (Recovery Readiness)
- **HRV Status**: Tracks heart rate variability trends (limited by Garmin API)
- **Resting Heart Rate**: 7-day average vs overall baseline
- **Sleep Score**: Placeholder (not available via Garmin API)

**What the coach sees**: Whether your "engine" is ready for hard work or needs recovery

### 2️⃣ Training Load & Volume Distribution
- **Acute Load**: Last 7 days of training volume (minutes)
- **Chronic Load**: Last 28 days average training volume
- **ACWR (Acute:Chronic Workload Ratio)**:
  - 🟢 **0.8-1.3**: Optimal training load
  - 🟡 **>1.3**: Elevated injury risk - monitor closely
  - 🔴 **>1.5**: HIGH risk - reduce volume immediately!

- **Time in HR Zones**:
  - Zone 1-2 (Easy aerobic): Should be ~80%
  - Zone 3 (Tempo): ~10%
  - Zone 4-5 (Hard): ~10%
  - **80/20 Rule**: Helps prevent overtraining

### 3️⃣ Efficiency Metrics

#### Run Decoupling (Aerobic Efficiency)
- **< 5%**: Strong aerobic base, ready for intensity
- **> 5%**: Aerobic deficiency, need more Zone 2 volume
- **Formula**: Measures HR drift during long steady-state efforts

#### Swim SWOLF
- **Score = Strokes + Time per length**
- Lower is better (indicates efficient technique)
- Typical good score: 30-40
- Your current: ~46 (room for improvement via drills)

#### Bike Efficiency Factor (EF)
- **Formula**: Speed / Heart Rate ratio over time
- **Improving ↗**: Getting fitter
- **Declining ↘**: Fatigue or overtraining
- **Stable →**: Maintaining fitness

### 4️⃣ Triathlon-Specific Metrics

#### Brick Performance Analysis
- Detects bike-to-run transitions
- Measures "pace lag" (how much slower you run after biking)
- Helps optimize race-day transitions

#### TSS by Sport
- Already implemented in `triathlon_analysis.py`
- Shows training stress distribution across swim/bike/run

## Coaching Recommendations Engine

The system generates adaptive recommendations based on:

1. **ACWR Thresholds**:
   - Warns if injury risk is elevated
   - Suggests volume reductions

2. **Aerobic Decoupling**:
   - High decoupling → More Zone 2 work needed
   - Low decoupling → Ready for intensity

3. **HR Zone Distribution**:
   - Checks 80/20 compliance
   - Alerts if too much high-intensity work

4. **Sport-Specific Metrics**:
   - Swim technique recommendations based on SWOLF
   - Bike efficiency trends

## Output Formats

### 1. Human-Readable Console Output
Formatted with emojis and clear sections for quick scanning:
```
🏆 ELITE COACHING BRIEF - Comprehensive Training Analysis
======================================================================

1️⃣ PHYSIOLOGICAL BASELINE (Recovery)
2️⃣ TRAINING LOAD & VOLUME
3️⃣ EFFICIENCY METRICS
4️⃣ TRIATHLON-SPECIFIC

📝 COACHING RECOMMENDATIONS
```

### 2. JSON Export
Saved to `data/coaching_brief.json` with structured data:
```json
{
  "athlete": "Tim Arnold",
  "period": "Last 7 Days",
  "readiness": {...},
  "load": {...},
  "performance": {...},
  "triathlon_specific": {...},
  "coaching_notes": [...]
}
```

**Use Case**: Copy this JSON to AI coaches (ChatGPT, Claude, Gemini) for personalized training advice!

## Usage

### CLI
```bash
python main.py coach
```

### GUI
Click the **"🏆 Coach Brief"** button

### Complete Pipeline
```bash
python main.py all
```
Runs in order: Download → Analyze → Triathlon → **Coach Brief** → Visualize

## Technical Implementation

### New Module: `coaching_brief.py`
- 400+ lines of advanced training science algorithms
- Implements Gemini's specific recommendations
- Uses both CSV and JSON data for richest metrics

### Integration Points
- ✅ `main.py`: Added 'coach' command
- ✅ `gui.py`: Added "🏆 Coach Brief" button (row 1, column 1)
- ✅ Data flow: Reads from `data/activities.json` for HR zones, strokes, etc.

## Limitations & Future Enhancements

### Current Limitations
1. **No Time-Series Data**: Garmin API doesn't provide per-second HR/power data
   - Aerobic decoupling is estimated, not precise
   - Can't calculate true EF drift within workouts

2. **HRV Not Available**: Garmin Connect API doesn't expose HRV data consistently
   - Using RHR as proxy

3. **Sleep Data Missing**: Not available via API
   - Important recovery metric not tracked

4. **Power Data**: Only available for some cycling activities
   - Using speed/HR as proxy when power unavailable

### Future Enhancements
1. **Garmin Health API Integration**: For HRV, sleep, stress scores
2. **FIT File Parsing**: Download .FIT files for time-series analysis
3. **Training Peaks Integration**: Export TSS to structured training plans
4. **Trend Visualizations**: Charts showing EF, SWOLF, ACWR over time
5. **ML-Based Load Prediction**: Predict optimal training load for next week

## Scientific Basis

This implementation is based on:

- **ACWR**: Research by Tim Gabbett (2016) on injury prevention
- **80/20 Training**: Dr. Stephen Seiler's polarized training research
- **Aerobic Decoupling**: Dr. Philip Maffetone's aerobic efficiency testing
- **SWOLF**: Standard swim efficiency metric used by coaches worldwide
- **TSS**: Training Stress Score by TrainingPeaks

## Example Output Interpretation

```
Time in Zones:
   Zone 1-2 (Easy):  19.6%
   Zone 3 (Tempo):   35.5%
   Zone 4-5 (Hard):  44.9%

📝 COACHING RECOMMENDATIONS
   📊 Only 20% time in Z1-Z2 - aim for 80/20 split
```

**Translation**: You're doing too much hard work! 80% of your training should be easy Zone 1-2 (conversational pace). Right now you're at only 20% easy, which risks burnout and injury. Back off the intensity and build aerobic base.

## Questions?

- **"Why is my ACWR 1.52?"** → You increased training load too quickly. Reduce next week's volume by 20-30%.
- **"Why is SWOLF important?"** → It's the only metric that combines efficiency (strokes) with speed (time). Lower = faster with less effort.
- **"What if I don't have HR data?"** → Some metrics won't be available. Garmin watch must be worn during activities for HR tracking.

## Credits

Feature designed based on conversation with **Gemini AI (Maestro-MPD)** who provided elite coaching insights on what metrics matter for triathlon training optimization.

Implementation by **GitHub Copilot + Claude Sonnet 4.5** on January 4, 2026.
