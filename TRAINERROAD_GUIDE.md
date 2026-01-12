# 🚴 TrainerRoad Workout Guidance

## Overview
Your Garmin app now provides **intelligent TrainerRoad workout recommendations** based on your current training state, recovery status, and performance metrics.

## How It Works

The coaching brief analyzes:
1. **ACWR (Injury Risk)** - Are you overreaching?
2. **HR Zone Distribution** - Too much intensity?
3. **Aerobic Decoupling** - Is your endurance base solid?
4. **Recent Training Load** - Are you fresh or fatigued?

Then recommends:
- **Workout Type** (Recovery, Endurance, Tempo, Sweet Spot)
- **Target TSS** (Training Stress Score)
- **Target IF** (Intensity Factor)
- **Specific TrainerRoad Workouts** with names and TSS/IF values

## Workout Types Explained

### 🟢 ENDURANCE (Zone 2)
- **Intensity Factor**: 0.65-0.75
- **When**: Building aerobic base, recovering, or after too much intensity
- **Benefits**: Mitochondrial development, fat oxidation, low stress
- **Example Workouts**: 
  - Pettit (39 TSS, IF 0.56)
  - Boarstone (60 TSS, IF 0.68)
  - Warren (60 TSS, IF 0.69)

### 🟡 TEMPO (Zone 3)
- **Intensity Factor**: 0.85-0.95
- **When**: Good aerobic base, ready for sustainable intensity
- **Benefits**: Lactate threshold improvement, race pace work
- **Example Workouts**:
  - Tallac (67 TSS, IF 0.90)
  - Baird (62 TSS, IF 0.85)

### 🟠 SWEET SPOT (Zone 3/4 Border)
- **Intensity Factor**: 0.88-0.93
- **When**: Solid base, need efficient training stimulus
- **Benefits**: High training stress with manageable fatigue
- **Example Workouts**:
  - Carson (60 TSS, IF 0.88) - Classic
  - Antelope (70 TSS, IF 0.89)
  - Monitor (54 TSS, IF 0.87)

### 🔴 RECOVERY
- **Intensity Factor**: 0.45-0.60
- **When**: ACWR > 1.5, elevated HR, poor sleep, or muscle soreness
- **Benefits**: Active recovery, promotes blood flow
- **Example Workouts**:
  - Lazy Mountain (24 TSS, IF 0.46)
  - Pettit (39 TSS, IF 0.56)

## Decision Logic

### If ACWR > 1.5 (HIGH INJURY RISK)
```
→ RECOVERY or REST DAY
→ Target TSS: 30
→ Target IF: 0.55
→ Workouts: Pettit, Lazy Mountain
```

### If ACWR > 1.3 (Elevated Risk)
```
→ ENDURANCE
→ Target TSS: 50
→ Target IF: 0.68
→ Workouts: Boarstone, Fletcher
```

### If Z4-Z5 Time > 30% (Too Much Intensity)
```
→ ENDURANCE
→ Target TSS: 60
→ Target IF: 0.70
→ Workouts: Pettit +1, Warren
→ Reason: Need more Zone 2 aerobic base
```

### If Z1-Z2 Time < 70% (Not Enough Easy Work)
```
→ ENDURANCE
→ Target TSS: 70
→ Target IF: 0.72
→ Workouts: Boarstone +2, Gibbs
→ Reason: Build aerobic base (80/20 rule)
```

### If Aerobic Decoupling > 5% (Poor Endurance)
```
→ SWEET SPOT
→ Target TSS: 55
→ Target IF: 0.88
→ Workouts: Carson, Monitor
→ Reason: Build sustainable power efficiency
```

### If Everything Looks Good
```
→ TEMPO or SWEET SPOT
→ Target TSS: 65
→ Target IF: 0.90
→ Workouts: Antelope, Tallac, Baird
→ Reason: Ready for productive intensity
```

## Your Current Recommendation

Run the coaching brief to see your personalized recommendation:
```bash
python main.py coach
```

Or click **🏆 Coach Brief** in the GUI.

## Example Output

```
🚴 TRAINERROAD WORKOUT GUIDANCE
======================================================================
   📋 Next Workout:    ENDURANCE
   🎯 Target TSS:      60
   ⚡ Target IF:        0.70

   💡 Why?
      • 45% time in Z4-5: Too much intensity
      • Need more Zone 2 aerobic base work

   📝 Suggested TrainerRoad Workouts:
      • Pettit +1 (46 TSS, IF 0.65) - Endurance
      • Warren (60 TSS, IF 0.69) - Steady endurance
```

## Tips for Using TrainerRoad

1. **Trust the Recommendation**: If it says ENDURANCE, don't go Sweet Spot
2. **Match TSS Target**: Pick workouts within ±10 TSS of target
3. **Consider Duration**: Longer workouts = more TSS at same IF
4. **Check IF Range**: Stay within 0.05 of target IF
5. **Listen to Your Body**: Override if you feel terrible

## Intensity Factor (IF) Quick Reference

| IF Range | Zone | Feel | Example |
|----------|------|------|---------|
| 0.45-0.60 | Recovery | Very easy, conversational | Active recovery spin |
| 0.60-0.75 | Endurance | Easy, can talk in sentences | Base building |
| 0.75-0.85 | Tempo | Moderate, can talk in phrases | Tempo intervals |
| 0.85-0.95 | Sweet Spot | Hard but sustainable | Sweet spot intervals |
| 0.95-1.05 | Threshold | Very hard, few words | FTP intervals |
| 1.05+ | VO2 Max | Extremely hard, gasping | All-out efforts |

## Integration with 80/20 Training

The recommendations enforce **polarized training**:
- 80% of time should be in Zone 1-2 (Easy/Endurance)
- 20% of time in Zone 3-5 (Tempo/Sweet Spot/Threshold)

If your zone distribution is off, the app will guide you back to 80/20.

## Scientific Basis

- **ACWR Research**: Tim Gabbett (2016) on injury prevention through load management
- **Polarized Training**: Dr. Stephen Seiler's research on elite endurance athletes
- **Sweet Spot Training**: Andrew Coggan's power-based training zones
- **TSS/IF**: TrainingPeaks metrics for quantifying training load

## Questions?

**Q: Why does it recommend easy workouts when I feel good?**
A: Your metrics (HR zones, ACWR) show accumulated fatigue. Trust the data over feelings.

**Q: Can I do Sweet Spot if it recommends Endurance?**
A: Not advised. You risk overtraining and injury. Follow the recommendation.

**Q: What if I don't have a power meter?**
A: TrainerRoad uses virtual power on smart trainers. IF is still accurate.

**Q: How often should I check recommendations?**
A: Before each ride. Your training state changes daily.

**Q: What if I just did a hard workout yesterday?**
A: Download fresh data first (`python main.py download`), then check recommendations.

## Advanced: Understanding Your Specific Recommendation

Your current state shows:
- ✅ ACWR: 1.13 (optimal)
- ⚠️ Z1-Z2: Only 20% (need 80%!)
- ⚠️ Z4-Z5: 45% (way too much!)
- ⚠️ Aerobic decoupling: 10% (poor endurance base)

**Translation**: You're doing too many hard workouts and not enough easy miles. This leads to:
1. Accumulated fatigue without aerobic adaptation
2. Increased injury risk (even though ACWR looks OK)
3. Poor endurance efficiency (high HR drift on long rides)

**Solution**: Back off intensity, build aerobic base with ENDURANCE workouts at IF 0.65-0.72 for the next 2-3 weeks.

## Next Steps

1. ✅ Run coaching brief: `python main.py coach`
2. ✅ Note the TrainerRoad recommendation
3. ✅ Open TrainerRoad app
4. ✅ Search for recommended workout (e.g., "Pettit +1")
5. ✅ Complete the workout
6. ✅ Sync with Garmin
7. ✅ Download fresh data: `python main.py download`
8. ✅ Check updated recommendation before next ride

Happy training! 🚴💨
