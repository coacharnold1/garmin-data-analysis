# 🗓️ Quick Start: Periodization & AI Coach Integration

## Set Your Race Date (Optional)

Edit your `.env` file and add:

```bash
# Race Planning
RACE_DATE=2026-06-15
RACE_TYPE=half_ironman
RACE_PRIORITY=A
```

**Race Types:**
- `sprint` - Sprint distance
- `olympic` - Olympic distance  
- `half_ironman` - 70.3 distance
- `full_ironman` - Full Ironman

**Race Priority:**
- `A` - Main goal race (peak for this)
- `B` - Tune-up race (practice, not taper)
- `C` - Training race (no taper)

## Run the Coaching Brief

```bash
python main.py coach
```

or click **🏆 Coach Brief** in the GUI.

## What You'll Get

### 1. Automated Phase Detection
The app will tell you which training phase you're in:
- **BASE** (12-20 weeks out) - Build aerobic foundation
- **BUILD** (8-12 weeks out) - Increase intensity
- **PEAK** (4-8 weeks out) - Race-specific work
- **TAPER** (2-4 weeks) - Reduce volume
- **RACE_WEEK** - Final prep
- **OFF_SEASON** - No race planned

### 2. Phase-Specific Recommendations
- Weekly TSS targets for your phase
- Intensity split (% easy vs. hard)
- Specific TrainerRoad workouts for the phase
- Focus areas (base building, threshold work, etc.)

### 3. Ready-to-Use AI Prompt
The app generates a complete prompt you can copy and paste into:
- **Gemini** (your preferred AI coach)
- ChatGPT
- Claude

The prompt includes:
- Your current training data (JSON format)
- Race date and phase information
- Specific questions about your training
- Request for periodized plan

## Example Output (With Race Set)

```
📅 TRAINING PERIODIZATION
======================================================================
   🏁 Race Date:       June 15, 2026
   🏆 Race Type:       Half Ironman
   ⏱️  Weeks to Race:   23.3

   📍 Current Phase:   OFF_SEASON
   📖 Description:     Off-season - General fitness, cross-training

   🎯 Phase Targets:
      Weekly TSS:      300
      Intensity Split: 90% Z1-Z2, 10% Z3+
      Focus:           General fitness, cross-training, skill work

   🚴 Phase-Specific Workouts:
      • Pettit (39 TSS, IF 0.56)
      • Boarstone (60 TSS, IF 0.68)
      • Gibbs (75 TSS, IF 0.70)

🤖 AI COACH PROMPT (Copy this to Gemini/ChatGPT/Claude)
======================================================================

I'm a triathlete using data-driven training. Please analyze my current state...

🏁 RACE INFORMATION:
===================
- Race Date: June 15, 2026 (23 weeks away)
- Race Type: Half Ironman
- Priority: A-Race (Main Goal)

CURRENT TRAINING PHASE: OFF_SEASON
- Phase Description: Off-season - General fitness, cross-training
- Target Weekly TSS: 300
- Intensity Split: 90% Z1-Z2, 10% Z3+
- Phase Focus: General fitness, cross-training, skill work

[... rest of prompt with your training data ...]

🎯 WHAT I NEED FROM YOU:
========================

1. **Immediate Next Steps** (this week)
2. **Medium-Term Plan** (next 4 weeks)
3. **Long-Term Periodization** (to race day):
   - Phase breakdown with dates and focus
   - When to transition from OFF_SEASON to next phase?
   - Peak week timing and taper strategy
   - Race week protocol
```

## Using the AI Prompt

1. **Run**: `python main.py coach`
2. **Scroll** to the AI COACH PROMPT section
3. **Copy** the entire prompt (from "I'm a triathlete..." to the end)
4. **Paste** into Gemini/ChatGPT/Claude
5. **Get** your personalized training plan!

## What to Ask Gemini

The prompt is pre-loaded with specific questions:

### Immediate (This Week)
- What TrainerRoad workout tomorrow?
- Should I adjust based on ACWR?
- Any recovery red flags?

### Medium-Term (4 Weeks)
- Weekly TSS targets for current phase
- How many hard days per week?
- When to schedule recovery weeks?
- Swim/bike/run volume distribution

### Long-Term (To Race Day)
- Full periodization with phase dates
- When to transition between phases?
- Peak week and taper strategy
- Race week protocol

## Example Conversation with Gemini

```
You: [paste the AI coach prompt]

Gemini: Based on your data, you're 23 weeks out from your Half Ironman. 
Here's your periodized plan:

PHASE 1: OFF-SEASON (Weeks 1-4, Jan 4 - Feb 1)
- Weekly TSS: 300
- Focus: Build aerobic base, swim technique
- TrainerRoad: 
  * Mon: REST
  * Tue: Pettit +1 (46 TSS)
  * Wed: Swim drills
  * Thu: Boarstone (60 TSS)
  * Fri: REST
  * Sat: Warren (60 TSS)
  * Sun: Long run (easy pace)

Your ACWR of 1.13 is good, but your Zone distribution (20% Z1-Z2) is concerning...
[detailed analysis continues]

You: Should I do more long rides or more sweet spot work?

Gemini: At 23 weeks out, prioritize long endurance rides. Here's why...
```

## Tips for Best Results

1. **Download Fresh Data** before running coach brief:
   ```bash
   python main.py download
   python main.py coach
   ```

2. **Update Race Date** as it gets closer for phase transitions

3. **Re-run Weekly** to get updated recommendations

4. **Use JSON Export** for detailed AI analysis:
   - Scroll to bottom of output
   - Copy the entire JSON structure
   - Give to Gemini for deeper dive

5. **Track Phase Changes**:
   - OFF_SEASON → BASE (at 20 weeks)
   - BASE → BUILD (at 12 weeks)
   - BUILD → PEAK (at 8 weeks)
   - PEAK → TAPER (at 4 weeks)
   - TAPER → RACE_WEEK (at 2 weeks)

## Without a Race Date

If you don't set `RACE_DATE`, the app defaults to OFF_SEASON and gives general fitness guidance. This is perfect for:
- General triathlon training
- Between race seasons
- Building base fitness
- Recovering from previous race

## Next Steps

1. ✅ Set race date in `.env` (if you have one)
2. ✅ Run `python main.py coach`
3. ✅ Copy AI prompt
4. ✅ Paste into Gemini
5. ✅ Get your personalized 20-week plan!
6. ✅ Update weekly and adjust based on progress

Happy training! 🏊🚴🏃
