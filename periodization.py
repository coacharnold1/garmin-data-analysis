#!/usr/bin/env python3
"""
Periodization Module - Training phase detection and planning
"""
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


def get_race_info():
    """Load race information from .env"""
    race_date_str = os.getenv('RACE_DATE', '').strip()
    race_type = os.getenv('RACE_TYPE', '').strip()
    race_priority = os.getenv('RACE_PRIORITY', 'A').strip()
    
    if not race_date_str:
        return None
    
    try:
        race_date = datetime.strptime(race_date_str, '%Y-%m-%d')
        return {
            'date': race_date,
            'type': race_type,
            'priority': race_priority
        }
    except:
        return None


def calculate_training_phase(race_date=None):
    """
    Determine current training phase based on race date.
    
    Phases:
    - OFF_SEASON: > 20 weeks out or no race planned
    - BASE: 12-20 weeks out - Build aerobic foundation
    - BUILD: 8-12 weeks out - Increase intensity, race-specific work
    - PEAK: 4-8 weeks out - High intensity, VO2 max work
    - TAPER: 2-4 weeks out - Reduce volume, maintain intensity
    - RACE_WEEK: 0-2 weeks out - Final preparation
    - RECOVERY: 1-2 weeks post-race - Active recovery
    """
    if not race_date:
        return {
            'phase': 'OFF_SEASON',
            'weeks_to_race': None,
            'description': 'No race planned - General fitness maintenance'
        }
    
    today = datetime.now()
    days_to_race = (race_date - today).days
    weeks_to_race = days_to_race / 7
    
    # Post-race recovery
    if days_to_race < 0 and days_to_race > -14:
        return {
            'phase': 'RECOVERY',
            'weeks_to_race': weeks_to_race,
            'description': 'Post-race recovery - Easy aerobic work only'
        }
    
    # Race week
    if 0 <= weeks_to_race < 2:
        return {
            'phase': 'RACE_WEEK',
            'weeks_to_race': weeks_to_race,
            'description': 'Race week - Short openers, rest, final prep'
        }
    
    # Taper
    if 2 <= weeks_to_race < 4:
        return {
            'phase': 'TAPER',
            'weeks_to_race': weeks_to_race,
            'description': 'Taper phase - Reduce volume 30-50%, maintain intensity'
        }
    
    # Peak
    if 4 <= weeks_to_race < 8:
        return {
            'phase': 'PEAK',
            'weeks_to_race': weeks_to_race,
            'description': 'Peak phase - Race-specific intensity, VO2 max work'
        }
    
    # Build
    if 8 <= weeks_to_race < 12:
        return {
            'phase': 'BUILD',
            'weeks_to_race': weeks_to_race,
            'description': 'Build phase - Sweet Spot, tempo, race-specific volume'
        }
    
    # Base
    if 12 <= weeks_to_race < 20:
        return {
            'phase': 'BASE',
            'weeks_to_race': weeks_to_race,
            'description': 'Base phase - High volume, low intensity, Zone 2 focus'
        }
    
    # Off-season
    return {
        'phase': 'OFF_SEASON',
        'weeks_to_race': weeks_to_race,
        'description': 'Off-season - General fitness, cross-training'
    }


def get_phase_recommendations(phase, acwr=None, race_info=None):
    """
    Get training recommendations based on current phase.
    
    Returns TrainerRoad workout guidance and weekly TSS targets.
    Adjusted for race type (e.g., Triple T multi-day stage race).
    """
    # Check if this is a Triple T race (multi-day stage race requiring durability)
    is_triple_t = race_info and race_info.get('type') == 'triple_t'
    
    recommendations = {
        'OFF_SEASON': {
            'weekly_tss': 300,
            'intensity_split': '90% Z1-Z2, 10% Z3+',
            'workout_types': ['Endurance', 'Easy Recovery'],
            'focus': 'General fitness, cross-training, skill work',
            'trainerroad_workouts': [
                'Pettit (39 TSS, IF 0.56)',
                'Boarstone (60 TSS, IF 0.68)',
                'Gibbs (75 TSS, IF 0.70)'
            ]
        },
        'BASE': {
            'weekly_tss': 400,
            'intensity_split': '80% Z1-Z2, 20% Z3+',
            'workout_types': ['Endurance', 'Sweet Spot (1x/week)'],
            'focus': 'Aerobic base, mitochondrial density, fat adaptation',
            'trainerroad_workouts': [
                'Warren (60 TSS, IF 0.69) - Endurance',
                'Boarstone +3 (88 TSS, IF 0.70) - Long endurance',
                'Carson (60 TSS, IF 0.88) - Weekly sweet spot'
            ]
        },
        'BUILD': {
            'weekly_tss': 450,
            'intensity_split': '70% Z1-Z2, 30% Z3+',
            'workout_types': ['Sweet Spot', 'Tempo', 'Endurance'],
            'focus': 'Lactate threshold, race-specific intensity',
            'trainerroad_workouts': [
                'Antelope (70 TSS, IF 0.89) - Sweet spot intervals',
                'Tallac (67 TSS, IF 0.90) - Tempo',
                'Warren (60 TSS, IF 0.69) - Recovery endurance'
            ]
        },
        'PEAK': {
            'weekly_tss': 500,
            'intensity_split': '60% Z1-Z2, 40% Z3+',
            'workout_types': ['VO2 Max', 'Threshold', 'Race Simulation'],
            'focus': 'Peak fitness, race-specific power, neuromuscular prep',
            'trainerroad_workouts': [
                'Spencer (49 TSS, IF 1.00) - VO2 max',
                'Lamarck (69 TSS, IF 0.95) - Threshold',
                'McAdie (71 TSS, IF 0.94) - Over-unders'
            ]
        },
        'TAPER': {
            'weekly_tss': 250,
            'intensity_split': '70% Z1-Z2, 30% Z3+ (short bursts)',
            'workout_types': ['Openers', 'Short Intensity', 'Easy Spin'],
            'focus': 'Maintain sharpness, shed fatigue, mental prep',
            'trainerroad_workouts': [
                'Truuli -2 (30 TSS, IF 0.70) - Opener',
                'Lazy Mountain (24 TSS, IF 0.46) - Recovery',
                'Pettit (39 TSS, IF 0.56) - Easy spin'
            ]
        },
        'RACE_WEEK': {
            'weekly_tss': 150,
            'intensity_split': '80% Z1-Z2, 20% Z3+ (openers only)',
            'workout_types': ['Openers', 'Easy Recovery'],
            'focus': 'Rest, pre-race openers, carb loading',
            'trainerroad_workouts': [
                'Truuli -2 (30 TSS, IF 0.70) - 2 days before race',
                'Lazy Mountain (24 TSS, IF 0.46) - Easy spin',
                'REST - Day before race'
            ]
        },
        'RECOVERY': {
            'weekly_tss': 200,
            'intensity_split': '100% Z1-Z2',
            'workout_types': ['Easy Recovery', 'Active Rest'],
            'focus': 'Active recovery, rebuild glycogen, repair tissue',
            'trainerroad_workouts': [
                'Lazy Mountain (24 TSS, IF 0.46)',
                'Pettit (39 TSS, IF 0.56)',
                'Boarstone (60 TSS, IF 0.68) - Week 2 only'
            ]
        }
    }
    
    # Get base recommendation for phase
    base_rec = recommendations.get(phase, recommendations['OFF_SEASON']).copy()
    
    # TRIPLE T ADJUSTMENTS - Multi-day stage race requires different preparation
    if is_triple_t:
        if phase == 'BASE':
            base_rec['weekly_tss'] = 450  # Higher volume for durability
            base_rec['focus'] = 'Aerobic durability, back-to-back training days, brick workouts'
            base_rec['trainerroad_workouts'].append('SPECIAL: 3-day training blocks (Sat-Sun-Mon) to simulate race format')
        
        elif phase == 'BUILD':
            base_rec['weekly_tss'] = 500  # Increased for multi-day capacity
            base_rec['intensity_split'] = '65% Z1-Z2, 35% Z3+'  # More intensity tolerance needed
            base_rec['focus'] = 'Back-to-back race-pace efforts, recovery between races, heat adaptation'
            base_rec['trainerroad_workouts'] = [
                'Friday: Antelope (70 TSS, IF 0.89) - PM race simulation',
                'Saturday AM: Tallac (67 TSS, IF 0.90) - 4hr recovery',
                'Saturday PM: Carson (60 TSS, IF 0.88) - 6hr recovery',
                'Sunday: McAdie (71 TSS, IF 0.94) - Olympic pace'
            ]
        
        elif phase == 'PEAK':
            base_rec['weekly_tss'] = 550  # Peak for multi-day
            base_rec['focus'] = 'Triple-brick weekends (3 races in 3 days), race nutrition rehearsal, cumulative fatigue management'
            base_rec['trainerroad_workouts'] = [
                'RACE SIMULATION WEEKEND:',
                'Friday 6pm: Super Sprint effort (30-40 TSS)',
                'Saturday 8am: Sprint effort (60-70 TSS)',
                'Saturday 2pm: Sprint effort (60-70 TSS)',
                'Sunday 8am: Olympic effort (90-100 TSS)'
            ]
        
        elif phase == 'TAPER':
            base_rec['weekly_tss'] = 300  # Longer taper for multi-day event
            base_rec['focus'] = 'Extra recovery for 3-day event, practice transitions, race nutrition final checks'
            base_rec['trainerroad_workouts'] = [
                'Week 1: 2x opener workouts, rest of easy spin',
                'Race week: Truuli -2 on Monday/Wednesday, complete rest Thursday'
            ]
        
        elif phase == 'RACE_WEEK':
            base_rec['weekly_tss'] = 180  # Slightly higher for 3-day race prep
            base_rec['focus'] = 'REST for multi-day event, pack gear for 4 races, hydration/nutrition plan'
            base_rec['trainerroad_workouts'] = [
                'Monday: Pettit (39 TSS, IF 0.56)',
                'Tuesday: Truuli -2 (30 TSS, IF 0.70)',
                'Wednesday: Complete REST',
                'Thursday: Complete REST',
                'Friday: Pre-race swim/bike check only (no workout)'
            ]
        
        elif phase == 'RECOVERY':
            base_rec['weekly_tss'] = 150  # Extended recovery after 4 races
            base_rec['focus'] = 'Extended recovery (2 weeks minimum), massage, nutrition replenishment'
            base_rec['trainerroad_workouts'] = [
                'Week 1: Complete REST or easy 20min spins only',
                'Week 2: Lazy Mountain (24 TSS) every other day',
                'Week 3: Return to 200 TSS with all endurance'
            ]
    
    # Adjust for injury risk (overrides everything)
    if acwr and acwr > 1.5:
        # Override with recovery regardless of phase
        return {
            'weekly_tss': 200,
            'intensity_split': '100% Z1-Z2',
            'workout_types': ['Recovery Only'],
            'focus': '⚠️ INJURY RISK OVERRIDE - Active recovery only',
            'trainerroad_workouts': [
                'Lazy Mountain (24 TSS, IF 0.46)',
                'Pettit (39 TSS, IF 0.56)',
                'REST DAYS as needed'
            ]
        }
    
    return base_rec


def generate_ai_coach_prompt(coaching_data, phase_info, phase_recs):
    """
    Generate a ready-to-use prompt for AI coaches (Gemini, ChatGPT, Claude).
    """
    race_info = get_race_info()
    # Build recovery status section based on available data
    recovery_section = "RECOVERY STATUS:\n"
    readiness = coaching_data['readiness']
    
    if 'resting_hr' in readiness:
        # Real wellness data available
        recovery_section += f"- Resting HR: {readiness['resting_hr']} bpm (actual RHR)\n"
        recovery_section += f"- Body Battery: {readiness['body_battery']}\n"
        recovery_section += f"- Stress (avg): {readiness['stress_avg']}\n"
        recovery_section += f"- Sleep Score: {readiness['sleep_score_avg']}\n"
        recovery_section += f"- Data Source: {readiness['data_source']}\n"
    else:
        # Fallback to activity HR
        recovery_section += f"- HRV Status: {readiness.get('hrv_status', 'N/A')} ({readiness.get('hrv_deviation', 'N/A')})\n"
        recovery_section += f"- Activity HR (avg): {readiness.get('avg_activity_hr', 'N/A')} bpm\n"
        if 'hr_note' in readiness:
            recovery_section += f"  ⚠️ NOTE: {readiness['hr_note']}\n"
        recovery_section += f"- Sleep Score: {readiness['sleep_score_avg']}\n"
    
    prompt = f"""I'm a triathlete using data-driven training. Please analyze my current state and help optimize my training plan.

📊 CURRENT TRAINING DATA:
========================

Analysis Period: {coaching_data['period']}
Note: {coaching_data.get('analysis_note', 'Performance and recovery metrics')}
Generated: {coaching_data['generated']}

{recovery_section}
TRAINING LOAD:
- Acute Load (7d): {coaching_data['load']['acute_load_min']} minutes
- Chronic Load (28d): {coaching_data['load']['chronic_load_min']} minutes
- ACWR: {coaching_data['load']['acwr']} - Risk Level: {coaching_data['load']['injury_risk']}
- HR Zone Distribution: {coaching_data['load']['distribution']['Z1_2']} in Z1-Z2 (target: 80%)

PERFORMANCE METRICS ({coaching_data['period']}):
- Run Aerobic Decoupling: {coaching_data['performance']['run_decoupling']}
- Swim SWOLF: {coaching_data['performance']['swim_swolf_avg']}
- Bike Efficiency Trend: {coaching_data['performance']['bike_ef_trend']}
"""

    if race_info:
        race_type_display = race_info['type'].replace('_', ' ').title()
        
        # Add special description for Triple T
        if race_info['type'] == 'triple_t':
            race_type_display = "Triple T (Multi-Day Stage Race)"
            race_details = """
  Race Format - 4 triathlons in 3 days:
    • Friday 6pm: Super Sprint (400m swim, 10mi bike, 2mi run)
    • Saturday 8am: Sprint (750m swim, 20km bike, 5km run)
    • Saturday 2pm: Sprint (750m swim, 20km bike, 5km run)
    • Sunday 8am: Olympic (1500m swim, 40km bike, 10km run)
  Total Distance: 3000m swim, 90km bike, 22km run
  Key Challenge: Cumulative fatigue, 4-6hr recovery between races, heat management
"""
        else:
            race_details = ""
        
        prompt += f"""
🏁 RACE INFORMATION:
===================
- Race Date: {race_info['date'].strftime('%B %d, %Y')} ({int(phase_info['weeks_to_race'])} weeks away)
- Race Type: {race_type_display}
- Priority: {race_info['priority']}-Race (Main Goal)
{race_details}
CURRENT TRAINING PHASE: {phase_info['phase']}
- Phase Description: {phase_info['description']}
- Target Weekly TSS: {phase_recs['weekly_tss']}
- Intensity Split: {phase_recs['intensity_split']}
- Phase Focus: {phase_recs['focus']}
"""
    else:
        prompt += f"""
🏁 RACE INFORMATION:
===================
- No race currently scheduled
- Current Phase: {phase_info['phase']}
- Training for general fitness
"""

    prompt += f"""
📝 CURRENT APP RECOMMENDATIONS:
==============================
{chr(10).join(coaching_data['coaching_notes'])}

🎯 WHAT I NEED FROM YOU:
========================
Please provide:

1. **Immediate Next Steps** (this week):
   - What TrainerRoad workout should I do tomorrow?
   - Should I adjust volume or intensity based on my ACWR?
   - Any red flags in my recovery metrics?

2. **Medium-Term Plan** (next 4 weeks):
"""

    if race_info:
        prompt += f"""   - Weekly TSS targets for {phase_info['phase']} phase
   - Key workouts per week (how many hard days?)
   - When should I schedule recovery weeks?
   - Swim/bike/run volume distribution
   - Race-specific workouts for {race_info['type'].replace('_', ' ')}

3. **Long-Term Periodization** (to race day):
   - Phase breakdown with dates and focus
   - When to transition from {phase_info['phase']} to next phase?
   - Peak week timing and taper strategy
   - Race week protocol
"""
    else:
        prompt += f"""   - Should I set a goal race? If so, when and what distance?
   - Weekly TSS targets for fitness maintenance
   - How to balance swim/bike/run without a target race?
   - Seasonal periodization suggestions

3. **Long-Term Planning**:
   - Should I plan a training season around A/B/C races?
   - Off-season timing and focus
"""

    prompt += f"""
4. **Specific Concerns**:
   - My HR zone distribution shows {coaching_data['load']['distribution']['Z1_2']} in Zone 1-2 (need 80%). How to fix this?
   - Aerobic decoupling at {coaching_data['performance']['run_decoupling']} - what does this mean for my endurance?
   - Am I ready for high-intensity work, or should I build more base?

5. **TrainerRoad Workout Selection**:
   - Given my current phase and metrics, which specific workouts from TrainerRoad?
   - How many hard days per week should I do?
   - When to schedule endurance vs. sweet spot vs. tempo?

COACHING PHILOSOPHY:
I follow polarized training (80/20 rule) and use TrainerRoad for structured indoor cycling. I want to avoid overtraining and injury while making steady progress toward race fitness.

Please be specific with dates, TSS numbers, and workout names. Thank you!
"""

    return prompt


def main():
    """Test periodization module"""
    race_info = get_race_info()
    print("Race Info:", race_info)
    
    if race_info:
        phase_info = calculate_training_phase(race_info['date'])
    else:
        phase_info = calculate_training_phase()
    
    print(f"\nCurrent Phase: {phase_info['phase']}")
    print(f"Weeks to Race: {phase_info.get('weeks_to_race', 'N/A')}")
    print(f"Description: {phase_info['description']}")
    
    phase_recs = get_phase_recommendations(phase_info['phase'])
    print(f"\nWeekly TSS Target: {phase_recs['weekly_tss']}")
    print(f"Intensity Split: {phase_recs['intensity_split']}")
    print(f"Focus: {phase_recs['focus']}")


if __name__ == "__main__":
    main()
