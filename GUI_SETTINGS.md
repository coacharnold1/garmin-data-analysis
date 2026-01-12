# GUI Settings - Quick Guide

## Analysis Period Selector

### How to Use

1. **Launch the GUI**: Run `python gui.py` or click the desktop icon
2. **Click ⚙️ Settings** button (top-right corner)
3. **Select your desired analysis period**:
   - ⭕ **7 days** - Recent trends (returning from break/injury)
   - ⭕ **30 days** - Monthly view (current training block)
   - ⭕ **60 days** - Long-term patterns (**RECOMMENDED** ✓)
   - ⭕ **90 days** - Seasonal view (full build)
4. **Click 💾 Save**
5. **Run Coach Brief** to see analysis with new period

### What's Analyzed

**Performance Metrics** (Uses selected period):
- HR Zone Distribution (Z1-Z2, Z3, Z4-Z5)
- Run Aerobic Decoupling
- Swim SWOLF efficiency
- Bike Efficiency Factor trends

**Recovery Metrics** (Always 7 days):
- Resting Heart Rate (RHR)
- Body Battery levels
- Sleep Score
- Stress levels

**Training Load** (Fixed windows):
- ACWR: 7-day acute / 28-day chronic

### Example Scenarios

#### Returning from Break
```
Current: 60 days selected
Problem: Been off 7 days, only 1 workout
Solution: 
  1. Click ⚙️ Settings
  2. Select: 7 days
  3. Save
  4. Run Coach Brief
Result: Only analyzes recent activity
```

#### Planning Base Phase
```
Current: 7 days selected  
Need: Long-term training patterns
Solution:
  1. Click ⚙️ Settings
  2. Select: 60 days (RECOMMENDED)
  3. Save
  4. Run Coach Brief
Result: Shows true 2-month training distribution
```

#### Mid-Build Check
```
Current: 60 days selected
Need: Focus on current mesocycle
Solution:
  1. Click ⚙️ Settings
  2. Select: 30 days
  3. Save
  4. Run Coach Brief
Result: Analyzes current training block
```

### Settings Location

The setting is saved to `.env` file as:
```
ANALYSIS_DAYS=60
```

You can also edit this manually, but the GUI makes it easier!

### Benefits of GUI Selector

✅ **No manual file editing** - Simple radio button selection  
✅ **Instant feedback** - See your current setting  
✅ **Clear descriptions** - Know what each option means  
✅ **Visual confirmation** - Success message after saving  
✅ **Context help** - Info text explains what stays fixed  

### Current Setting

Check your current analysis period:
- Open GUI → Click ⚙️ Settings
- The selected radio button shows your current period
- Default: **60 days** (recommended)
