#!/usr/bin/env python3
"""
Coaching Brief Generator - Elite-level training analysis
Implements Gemini's recommendations for comprehensive athlete monitoring
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import periodization
import os
from dotenv import load_dotenv

# Load environment variables for FTP
load_dotenv()


def load_data():
    """Load activities from JSON (richer data) and CSV"""
    json_path = Path("./data/activities.json")
    csv_path = Path("./data/activities.csv")
    
    if not json_path.exists() or not csv_path.exists():
        raise FileNotFoundError("Data files not found. Run download first.")
    
    with open(json_path, 'r') as f:
        activities_json = json.load(f)
    
    df = pd.read_csv(csv_path)
    df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])
    df = df.sort_values('startTimeLocal').reset_index(drop=True)
    
    return df, activities_json


def load_sleep_data():
    """Load sleep data from JSON if available"""
    sleep_path = Path("./data/sleep.json")
    
    if not sleep_path.exists():
        return None
    
    try:
        with open(sleep_path, 'r') as f:
            sleep_data = json.load(f)
        return sleep_data if sleep_data else None
    except Exception as e:
        print(f"Warning: Could not load sleep data: {e}")
        return None


def load_wellness_data():
    """Load wellness data (RHR, stress, body battery) from JSON if available"""
    wellness_path = Path("./data/wellness.json")
    
    if not wellness_path.exists():
        return None
    
    try:
        with open(wellness_path, 'r') as f:
            wellness_data = json.load(f)
        return wellness_data if wellness_data else None
    except Exception as e:
        print(f"Warning: Could not load wellness data: {e}")
        return None


def load_training_stats():
    """Load training stats (VO2 max, FTP, etc.) from JSON if available"""
    stats_path = Path("./data/training_stats.json")
    
    if not stats_path.exists():
        return None
    
    try:
        with open(stats_path, 'r') as f:
            stats_data = json.load(f)
        return stats_data if stats_data else None
    except Exception as e:
        print(f"Warning: Could not load training stats: {e}")
        return None


def calculate_ftp_from_activities(activities_json):
    """
    Calculate FTP (Functional Threshold Power) from activity power data or .env config.
    
    Priority:
    1. Use FTP from .env file (TrainerRoad value)
    2. Estimate from best 20-minute power × 0.95
    
    This matches TrainerRoad's FTP calculation method.
    """
    # Check for configured FTP first (from TrainerRoad or testing)
    configured_ftp = os.getenv('FTP')
    if configured_ftp:
        try:
            ftp_value = int(configured_ftp)
            return {
                'ftp_watts': ftp_value,
                'source': 'TrainerRoad / Manual',
                'note': 'Configured value from .env file'
            }
        except ValueError:
            pass
    
    # Fall back to calculating from activities
    cycling_with_power = []
    for activity in activities_json:
        activity_type = activity.get('activityType', {}).get('typeKey', '').lower()
        if 'cycling' in activity_type:
            max_20min = activity.get('max20MinPower')
            if max_20min and max_20min > 0:
                cycling_with_power.append({
                    'date': activity.get('startTimeLocal', '')[:10],
                    'name': activity.get('activityName', 'Unknown'),
                    'max_20min_power': max_20min,
                    'avg_power': activity.get('avgPower', 0),
                    'norm_power': activity.get('normPower', 0)
                })
    
    if not cycling_with_power:
        return None
    
    # Find best 20-minute power
    best_activity = max(cycling_with_power, key=lambda x: x['max_20min_power'])
    best_20min = best_activity['max_20min_power']
    estimated_ftp = int(best_20min * 0.95)
    
    return {
        'ftp_watts': estimated_ftp,
        'source': 'Estimated',
        'best_20min_watts': int(best_20min),
        'best_20min_date': best_activity['date'],
        'best_20min_workout': best_activity['name'],
        'activities_analyzed': len(cycling_with_power),
        'note': 'Estimated from best 20min power. Update FTP=xxx in .env for accurate value.'
    }


def calculate_aerobic_decoupling(activity_json):
    """
    Calculate aerobic decoupling (Pa:Hr) for steady-state workouts >60 min.
    
    Decoupling % = ((EF_first - EF_second) / EF_first) * 100
    where EF = Power or Pace / Heart Rate
    
    < 5%: Strong aerobic base (ready for intensity)
    > 5%: Aerobic deficiency (needs more Zone 2 volume)
    """
    duration_min = activity_json.get('duration', 0) / 60
    
    # Only calculate for workouts > 60 minutes
    if duration_min < 60:
        return None
    
    avg_hr = activity_json.get('averageHR', 0)
    if avg_hr == 0 or avg_hr is None:
        return None
    
    # For cycling: use power if available, else speed
    activity_type = activity_json.get('activityType', {}).get('typeKey', '')
    
    # Get HR zone times to approximate first/second half distribution
    zone_times = {
        'z1': activity_json.get('hrTimeInZone_1', 0),
        'z2': activity_json.get('hrTimeInZone_2', 0),
        'z3': activity_json.get('hrTimeInZone_3', 0),
        'z4': activity_json.get('hrTimeInZone_4', 0),
        'z5': activity_json.get('hrTimeInZone_5', 0)
    }
    
    total_time = sum(zone_times.values())
    if total_time == 0:
        return None
    
    # Estimate HR drift by checking if higher zones become more dominant
    # This is an approximation without time-series data
    avg_speed = activity_json.get('averageSpeed', 0)
    max_hr = activity_json.get('maxHR', 0)
    
    if avg_speed == 0 or max_hr == 0:
        return None
    
    # Simple heuristic: if max HR is significantly higher than avg HR,
    # and workout is long, there's likely some drift
    hr_range = max_hr - avg_hr
    
    # Estimate decoupling based on HR range relative to workout duration
    # This is approximate without time-series data
    estimated_decoupling = (hr_range / avg_hr) * (duration_min / 120) * 100
    
    return min(estimated_decoupling, 15)  # Cap at 15%


def analyze_hr_zones(df, activities_json):
    """
    Analyze time in HR zones to check 80/20 distribution.
    
    Ideal: 80% in Zone 1-2 (easy aerobic), 20% in Zone 3-5 (moderate-hard)
    """
    total_z1_z2 = 0
    total_z3 = 0
    total_z4_z5 = 0
    
    for activity in activities_json:
        z1 = activity.get('hrTimeInZone_1', 0) or 0
        z2 = activity.get('hrTimeInZone_2', 0) or 0
        z3 = activity.get('hrTimeInZone_3', 0) or 0
        z4 = activity.get('hrTimeInZone_4', 0) or 0
        z5 = activity.get('hrTimeInZone_5', 0) or 0
        
        total_z1_z2 += (z1 + z2)
        total_z3 += z3
        total_z4_z5 += (z4 + z5)
    
    total_time = total_z1_z2 + total_z3 + total_z4_z5
    
    if total_time == 0:
        return {"Z1_2": "N/A", "Z3": "N/A", "Z4_5": "N/A"}
    
    z1_z2_pct = (total_z1_z2 / total_time) * 100
    z3_pct = (total_z3 / total_time) * 100
    z4_z5_pct = (total_z4_z5 / total_time) * 100
    
    return {
        "Z1_2": f"{z1_z2_pct:.1f}%",
        "Z3": f"{z3_pct:.1f}%",
        "Z4_5": f"{z4_z5_pct:.1f}%"
    }


def calculate_swim_swolf(activities_json):
    """
    SWOLF = Strokes + Time (per length)
    Lower = better efficiency
    """
    swim_swolf_values = []
    
    for activity in activities_json:
        if activity.get('activityType', {}).get('typeKey') == 'lap_swimming':
            avg_strokes = activity.get('avgStrokes', 0)
            duration_sec = activity.get('duration', 0)
            distance_m = activity.get('distance', 0)
            
            if avg_strokes > 0 and distance_m > 0:
                # Approximate time per 25m length (assuming 25m pool)
                num_lengths = distance_m / 25
                if num_lengths > 0:
                    time_per_length = duration_sec / num_lengths
                    swolf = avg_strokes + time_per_length
                    swim_swolf_values.append(swolf)
    
    if swim_swolf_values:
        return np.mean(swim_swolf_values)
    return None


def calculate_bike_efficiency_factor(df, activities_json):
    """
    Efficiency Factor (EF) = Power / Heart Rate
    
    If EF is improving over time, fitness is increasing.
    """
    bike_activities = []
    
    for idx, activity in enumerate(activities_json):
        activity_type = activity.get('activityType', {}).get('typeKey', '')
        if 'cycling' in activity_type or 'bike' in activity_type:
            avg_hr = activity.get('averageHR', 0)
            avg_speed = activity.get('averageSpeed', 0)
            
            if avg_hr > 0 and avg_speed > 0:
                # Use speed as proxy for power (without actual power meter data)
                ef = avg_speed / avg_hr
                date = activity.get('startTimeLocal', '')
                bike_activities.append({'date': date, 'ef': ef})
    
    if len(bike_activities) < 2:
        return "Insufficient data"
    
    # Check trend: compare first 3 vs last 3 activities
    first_batch = bike_activities[:min(3, len(bike_activities)//2)]
    last_batch = bike_activities[-min(3, len(bike_activities)//2):]
    
    avg_first = np.mean([a['ef'] for a in first_batch])
    avg_last = np.mean([a['ef'] for a in last_batch])
    
    if avg_last > avg_first * 1.05:
        return "Improving ↗"
    elif avg_last < avg_first * 0.95:
        return "Declining ↘"
    else:
        return "Stable →"


def calculate_readiness_metrics(df, sleep_data=None, wellness_data=None):
    """
    Analyze recovery readiness using real RHR, sleep, stress, and body battery data.
    
    Now uses actual wellness data from Garmin:
    - Resting Heart Rate from wellness API
    - Sleep quality scores
    - Stress levels
    - Body Battery (Garmin's recovery metric)
    """
    # Get real resting HR from wellness data
    resting_hr = None
    body_battery = None
    stress_avg = None
    
    if wellness_data:
        # Extract resting heart rate
        hr_data = wellness_data.get('heart_rates', {})
        resting_hr = hr_data.get('restingHeartRate')
        
        # Extract body battery
        bb_data = wellness_data.get('body_battery', [])
        if bb_data:
            if isinstance(bb_data, list) and len(bb_data) > 0:
                bb_values = [item.get('charged', 0) for item in bb_data if isinstance(item, dict)]
                if bb_values:
                    body_battery = max(bb_values)  # Peak body battery for the day
            elif isinstance(bb_data, dict):
                body_battery = bb_data.get('charged')
        
        # Extract stress average
        stress_data = wellness_data.get('stress', {})
        if isinstance(stress_data, dict):
            stress_avg = stress_data.get('avgStressLevel')
    
    # Fall back to activity HR if no wellness data
    if resting_hr is None:
        recent_df = df[df['averageHR'] > 0].tail(7).copy()
        all_hr = df[df['averageHR'] > 0]['averageHR']
        recent_avg_hr = recent_df['averageHR'].mean() if len(recent_df) > 0 else 0
        overall_avg_hr = all_hr.mean() if len(all_hr) > 0 else 0
    
    # Calculate sleep score if data available
    sleep_score = calculate_sleep_score(sleep_data) if sleep_data else None
    
    # Build response with real data
    if resting_hr:
        # We have real resting HR!
        return {
            "resting_hr": resting_hr,
            "body_battery": body_battery if body_battery else "N/A",
            "stress_avg": stress_avg if stress_avg else "N/A",
            "sleep_score_avg": sleep_score if sleep_score else "N/A (not available)",
            "data_source": "Garmin Wellness API"
        }
    else:
        # Fallback to activity HR with warnings
        if overall_avg_hr == 0 or recent_avg_hr == 0:
            return {
                "hrv_status": "N/A",
                "hrv_deviation": "N/A",
                "avg_activity_hr": "N/A",
                "note": "⚠️ No wellness data available",
                "sleep_score_avg": sleep_score if sleep_score else "N/A (not available)"
            }
        
        if recent_avg_hr <= overall_avg_hr * 1.02:
            status = "Balanced"
            deviation = f"+{((recent_avg_hr - overall_avg_hr) / overall_avg_hr * 100):.1f}%"
        else:
            status = "Elevated"
            deviation = f"+{((recent_avg_hr - overall_avg_hr) / overall_avg_hr * 100):.1f}%"
    
        return {
            "hrv_status": status,
            "hrv_deviation": deviation,
            "avg_activity_hr": int(recent_avg_hr) if not pd.isna(recent_avg_hr) else "N/A",
            "note": "⚠️ This is ACTIVITY HR (~100-120 bpm), NOT resting HR (~40-60 bpm)",
            "sleep_score_avg": sleep_score if sleep_score else "N/A (not available)"
        }


def calculate_sleep_score(sleep_data):
    """
    Calculate average sleep score from Garmin sleep data (last 7 days).
    
    Returns average sleep score or None if no valid data.
    """
    if not sleep_data or len(sleep_data) == 0:
        return None
    
    try:
        # Get recent sleep data (last 7 days)
        recent_sleep = sleep_data[:7]
        
        sleep_scores = []
        for sleep_entry in recent_sleep:
            # Garmin sleep data structure varies, try multiple fields
            score = None
            
            # Try overallSleepScore first (0-100)
            if 'overallSleepScore' in sleep_entry:
                score = sleep_entry['overallSleepScore'].get('value')
            
            # Try sleepScores object
            elif 'sleepScores' in sleep_entry:
                scores_obj = sleep_entry['sleepScores']
                if 'overall' in scores_obj:
                    score = scores_obj['overall'].get('value')
            
            # Try dailySleepDTO structure
            elif 'dailySleepDTO' in sleep_entry:
                dto = sleep_entry['dailySleepDTO']
                if 'sleepScores' in dto:
                    score = dto['sleepScores'].get('overall', {}).get('value')
            
            if score and isinstance(score, (int, float)) and 0 <= score <= 100:
                sleep_scores.append(score)
        
        if sleep_scores:
            avg_score = np.mean(sleep_scores)
            return f"{avg_score:.0f}/100 (7-day avg, n={len(sleep_scores)})"
        else:
            return "N/A (no valid scores)"
            
    except Exception as e:
        print(f"Warning: Error calculating sleep score: {e}")
        return "N/A (parse error)"


def calculate_acute_chronic_ratio(df):
    """
    ACWR = Acute Load (7 days) / Chronic Load (28 days)
    
    Ideal: 0.8 - 1.3
    > 1.5: High injury risk - back off!
    """
    if len(df) < 7:
        return None
    
    # Use duration as proxy for load
    acute = df.tail(7)['duration'].sum() / 60  # minutes
    chronic = df.tail(28)['duration'].sum() / 60 if len(df) >= 28 else acute
    
    if chronic == 0:
        return None
    
    acwr = acute / (chronic / 4)  # Normalize to weekly average
    return acwr


def analyze_brick_performance(df, activities_json):
    """
    Detect bike-to-run transitions and measure pace lag.
    
    "Brick" workouts are when cycling is immediately followed by running.
    """
    brick_transitions = []
    
    for i in range(len(df) - 1):
        current = df.iloc[i]
        next_activity = df.iloc[i + 1]
        
        time_gap = (next_activity['startTimeLocal'] - current['startTimeLocal']).total_seconds() / 60
        
        # If bike followed by run within 30 minutes, it's a brick
        if ('cycling' in current['activityType'] or 'bike' in current['activityType']) and \
           'running' in next_activity['activityType'] and \
           time_gap < 30:
            
            run_pace = next_activity['paceMinPerKm']
            avg_run_pace = df[df['activityType'].str.contains('running', na=False)]['paceMinPerKm'].median()
            
            if not pd.isna(run_pace) and not pd.isna(avg_run_pace):
                pace_lag = ((run_pace - avg_run_pace) / avg_run_pace) * 100
                brick_transitions.append(pace_lag)
    
    if brick_transitions:
        return f"{np.mean(brick_transitions):.1f}% slower"
    return "No brick workouts detected"


def calculate_run_decoupling(activities_json):
    """Calculate decoupling specifically for running activities"""
    run_decouplings = []
    
    for activity in activities_json:
        if activity.get('activityType', {}).get('typeKey') == 'running':
            decoupling = calculate_aerobic_decoupling(activity)
            if decoupling is not None:
                run_decouplings.append(decoupling)
    
    if run_decouplings:
        return f"{np.mean(run_decouplings):.1f}%"
    return "N/A"


def recommend_trainerroad_workout(df, activities_json, acwr, hr_zones, run_decoupling):
    """
    Provide specific TrainerRoad workout recommendations based on current training state.
    
    Workout Types:
    - Endurance: Low intensity (Z2), builds aerobic base, IF ~0.65-0.75
    - Tempo: Moderate intensity (Z3), sustainable power, IF ~0.85-0.95
    - Sweet Spot: High-moderate intensity (Z3/Z4 border), efficient training, IF ~0.88-0.93
    """
    # Analyze TrainerRoad workouts
    tr_workouts = df[df['activityName'].str.contains('TrainerRoad', case=False, na=False)]
    
    # Get recent TSS from triathlon analysis
    recent_tss = df.tail(7)['duration'].sum() / 60  # Rough proxy
    
    # Decision tree for workout recommendations
    recommendations = {
        "workout_type": "",
        "target_tss": 0,
        "target_if": 0.0,
        "reasoning": [],
        "specific_workouts": []
    }
    
    # Parse HR zone percentages - handle N/A values
    z1_z2_str = hr_zones.get('Z1_2', '0%')
    z4_z5_str = hr_zones.get('Z4_5', '0%')
    z1_z2_pct = 0.0 if z1_z2_str == 'N/A' else float(z1_z2_str.replace('%', ''))
    z4_z5_pct = 0.0 if z4_z5_str == 'N/A' else float(z4_z5_str.replace('%', ''))
    
    # High injury risk - recovery needed
    if acwr and acwr > 1.5:
        recommendations["workout_type"] = "RECOVERY or REST"
        recommendations["target_tss"] = 30
        recommendations["target_if"] = 0.55
        recommendations["reasoning"].append("ACWR > 1.5: HIGH injury risk - prioritize recovery")
        recommendations["reasoning"].append("Take a rest day or very easy spin")
        recommendations["specific_workouts"].append("Pettit (39 TSS, IF 0.56) - Easy endurance")
        recommendations["specific_workouts"].append("Lazy Mountain (24 TSS, IF 0.46) - Recovery spin")
        
    # Elevated risk but manageable
    elif acwr and acwr > 1.3:
        recommendations["workout_type"] = "ENDURANCE"
        recommendations["target_tss"] = 50
        recommendations["target_if"] = 0.68
        recommendations["reasoning"].append("ACWR > 1.3: Elevated risk - stick to endurance pace")
        recommendations["reasoning"].append("Build aerobic base without adding stress")
        recommendations["specific_workouts"].append("Boarstone (60 TSS, IF 0.68) - Endurance")
        recommendations["specific_workouts"].append("Fletcher (60 TSS, IF 0.66) - Long endurance")
        
    # Too much high intensity (Zone 4-5)
    elif z4_z5_pct > 30:
        recommendations["workout_type"] = "ENDURANCE"
        recommendations["target_tss"] = 60
        recommendations["target_if"] = 0.70
        recommendations["reasoning"].append(f"{z4_z5_pct:.0f}% time in Z4-5: Too much intensity")
        recommendations["reasoning"].append("Need more Zone 2 aerobic base work")
        recommendations["specific_workouts"].append("Pettit +1 (46 TSS, IF 0.65) - Endurance")
        recommendations["specific_workouts"].append("Warren (60 TSS, IF 0.69) - Steady endurance")
        
    # Low aerobic base (not enough Z1-Z2)
    elif z1_z2_pct < 70:
        recommendations["workout_type"] = "ENDURANCE"
        recommendations["target_tss"] = 70
        recommendations["target_if"] = 0.72
        recommendations["reasoning"].append(f"Only {z1_z2_pct:.0f}% in Z1-2: Build aerobic base")
        recommendations["reasoning"].append("Target 80/20 split - more easy miles")
        recommendations["specific_workouts"].append("Boarstone +2 (74 TSS, IF 0.69) - Long endurance")
        recommendations["specific_workouts"].append("Gibbs (75 TSS, IF 0.70) - Steady aerobic")
        
    # High aerobic decoupling (poor endurance)
    elif run_decoupling != "N/A":
        decoupling_val = float(run_decoupling.replace('%', ''))
        if decoupling_val > 5:
            recommendations["workout_type"] = "SWEET SPOT"
            recommendations["target_tss"] = 55
            recommendations["target_if"] = 0.88
            recommendations["reasoning"].append("Aerobic base OK but efficiency needs work")
            recommendations["reasoning"].append("Sweet Spot builds sustainable power efficiently")
            recommendations["specific_workouts"].append("Carson (60 TSS, IF 0.88) - Classic sweet spot")
            recommendations["specific_workouts"].append("Monitor (54 TSS, IF 0.87) - Short sweet spot")
    
    # Good base, ready for intensity
    else:
        recommendations["workout_type"] = "TEMPO or SWEET SPOT"
        recommendations["target_tss"] = 65
        recommendations["target_if"] = 0.90
        recommendations["reasoning"].append("Strong aerobic base, balanced load")
        recommendations["reasoning"].append("Ready for productive intensity work")
        recommendations["specific_workouts"].append("Antelope (70 TSS, IF 0.89) - Sweet spot intervals")
        recommendations["specific_workouts"].append("Tallac (67 TSS, IF 0.90) - Tempo")
        recommendations["specific_workouts"].append("Baird (62 TSS, IF 0.85) - Tempo intervals")
    
    return recommendations


def generate_coaching_brief():
    """
    Generate a comprehensive "Coach's Brief" with all metrics.
    
    Output formats:
    - JSON for AI coaches
    - Markdown for human-readable summary
    """
    print("=" * 70)
    print("🏆 ELITE COACHING BRIEF - Comprehensive Training Analysis")
    print("=" * 70)
    print()
    
    df, activities_json = load_data()
    sleep_data = load_sleep_data()
    wellness_data = load_wellness_data()
    training_stats = load_training_stats()
    
    # Get analysis period from environment (default 60 days)
    analysis_days = int(os.getenv('ANALYSIS_DAYS', '60'))
    
    # Filter activities for performance analysis
    # Recovery metrics use last 7 days, but performance needs longer view
    today = datetime.now()
    cutoff_date = today - timedelta(days=analysis_days)
    
    # Filter activities JSON
    activities_filtered = []
    for activity in activities_json:
        activity_date_str = activity.get('startTimeLocal', '')
        if activity_date_str:
            try:
                activity_date = datetime.fromisoformat(activity_date_str.replace('Z', '+00:00'))
                if activity_date.replace(tzinfo=None) >= cutoff_date:
                    activities_filtered.append(activity)
            except:
                # Include activities with parsing errors to avoid losing data
                activities_filtered.append(activity)
    
    print(f"Analyzing {len(activities_filtered)} activities from last {analysis_days} days ({len(activities_json)} total)")
    print(f"To change analysis period, set ANALYSIS_DAYS in .env (options: 7, 30, 60, 90)")
    
    # Calculate all metrics using filtered data for performance
    readiness = calculate_readiness_metrics(df, sleep_data, wellness_data)  # Uses 7-day window internally
    acwr = calculate_acute_chronic_ratio(df)  # Uses 7d/28d windows
    hr_zones = analyze_hr_zones(df, activities_filtered)
    run_decoupling = calculate_run_decoupling(activities_filtered)
    swim_swolf = calculate_swim_swolf(activities_filtered)
    bike_ef = calculate_bike_efficiency_factor(df, activities_filtered)
    brick_perf = analyze_brick_performance(df, activities_json)  # Keep all for brick analysis
    ftp_data = calculate_ftp_from_activities(activities_json)  # Keep all for best FTP
    
    # Calculate TSS by sport
    acute_load = df.tail(7)['duration'].sum() / 60
    chronic_load = df.tail(28)['duration'].sum() / 60 if len(df) >= 28 else acute_load
    
    # Get TrainerRoad workout recommendations
    tr_recommendations = recommend_trainerroad_workout(df, activities_json, acwr, hr_zones, run_decoupling)
    
    # Get periodization info
    race_info = periodization.get_race_info()
    if race_info:
        phase_info = periodization.calculate_training_phase(race_info['date'])
    else:
        phase_info = periodization.calculate_training_phase()
    phase_recs = periodization.get_phase_recommendations(phase_info['phase'], acwr, race_info)
    
    # Create structured JSON output
    # Build readiness section based on data availability
    if 'resting_hr' in readiness:
        readiness_data = {
            "resting_hr": readiness["resting_hr"],
            "body_battery": readiness["body_battery"],
            "stress_avg": readiness["stress_avg"],
            "sleep_score_avg": readiness["sleep_score_avg"],
            "data_source": readiness["data_source"]
        }
    else:
        readiness_data = {
            "hrv_status": readiness.get("hrv_status", "N/A"),
            "hrv_deviation": readiness.get("hrv_deviation", "N/A"),
            "avg_activity_hr": readiness.get("avg_activity_hr", "N/A"),
            "hr_note": readiness.get("note", ""),
            "sleep_score_avg": readiness["sleep_score_avg"],
            "interpretation": "Fallback to activity HR - wellness data not available"
        }
    
    coaching_data = {
        "athlete": "Tim Arnold",
        "period": f"Last {analysis_days} Days",
        "analysis_note": f"Performance metrics from {analysis_days} days, Recovery metrics from 7 days",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "readiness": readiness_data,
        "load": {
            "acute_load_min": f"{acute_load:.0f}",
            "chronic_load_min": f"{chronic_load:.0f}",
            "acwr": f"{acwr:.2f}" if acwr else "N/A",
            "injury_risk": "HIGH - Reduce volume!" if acwr and acwr > 1.5 else 
                          "Elevated" if acwr and acwr > 1.3 else "Optimal",
            "distribution": hr_zones
        },
        "performance": {
            "run_decoupling": run_decoupling,
            "run_interpretation": "< 5%: Strong aerobic base | > 5%: Need more Zone 2",
            "swim_swolf_avg": f"{swim_swolf:.1f}" if swim_swolf else "N/A",
            "swim_interpretation": "Lower is better (strokes + time per length)",
            "bike_ef_trend": bike_ef,
            "bike_interpretation": "EF = Speed/HR ratio trending",
            "ftp": ftp_data if ftp_data else "N/A"
        },
        "triathlon_specific": {
            "brick_performance": brick_perf,
            "brick_interpretation": "Pace lag on bike-to-run transitions"
        },
        "periodization": {
            "race_date": race_info['date'].strftime('%Y-%m-%d') if race_info else None,
            "race_type": race_info['type'] if race_info else None,
            "weeks_to_race": f"{phase_info['weeks_to_race']:.1f}" if phase_info['weeks_to_race'] else None,
            "current_phase": phase_info['phase'],
            "phase_description": phase_info['description'],
            "weekly_tss_target": phase_recs['weekly_tss'],
            "intensity_split": phase_recs['intensity_split'],
            "phase_focus": phase_recs['focus'],
            "phase_workouts": phase_recs['trainerroad_workouts']
        },
        "trainerroad_recommendation": {
            "workout_type": tr_recommendations["workout_type"],
            "target_tss": tr_recommendations["target_tss"],
            "target_intensity_factor": tr_recommendations["target_if"],
            "reasoning": tr_recommendations["reasoning"],
            "specific_workouts": tr_recommendations["specific_workouts"]
        },
        "coaching_notes": []
    }
    
    # Generate coaching recommendations
    notes = []
    
    if acwr and acwr > 1.5:
        notes.append("⚠️ ACWR at {:.2f} - CUT volume by 30% to avoid injury!".format(acwr))
    elif acwr and acwr > 1.3:
        notes.append("⚡ ACWR at {:.2f} - Monitor fatigue closely".format(acwr))
    
    if run_decoupling != "N/A":
        decoupling_val = float(run_decoupling.replace('%', ''))
        if decoupling_val > 5:
            notes.append("🏃 Aerobic decoupling high - increase Zone 2 volume")
        else:
            notes.append("✅ Strong aerobic base - ready for intensity")
    
    # Parse HR zone percentage - handle N/A values
    z1_z2_str = hr_zones.get('Z1_2', '0%')
    z1_z2 = 0.0 if z1_z2_str == 'N/A' else float(z1_z2_str.replace('%', ''))
    if z1_z2 > 0 and z1_z2 < 70:
        notes.append("📊 Only {:.0f}% time in Z1-Z2 - aim for 80/20 split".format(z1_z2))
    
    if swim_swolf and swim_swolf > 40:
        notes.append("🏊 SWOLF at {:.1f} - work on technique drills".format(swim_swolf))
    
    if "Declining" in bike_ef:
        notes.append("🚴 Bike efficiency declining - check fatigue/recovery")
    
    coaching_data["coaching_notes"] = notes
    
    # Print human-readable summary
    print("📅 TRAINING ANALYSIS PERIOD")
    print("-" * 70)
    print(f"   Performance Metrics: Last {analysis_days} days ({len(activities_filtered)} activities)")
    print(f"   Recovery Metrics:    Last 7 days")
    print(f"   Training Load:       ACWR (7d acute / 28d chronic)")
    print(f"   Change period:       Edit ANALYSIS_DAYS in .env (7/30/60/90)")
    print(f"📊 Generated: {coaching_data['generated']}")
    print()
    
    print("1️⃣ PHYSIOLOGICAL BASELINE (Recovery - Last 7 Days)")
    print("-" * 70)
    
    # Display based on whether we have real wellness data or fallback
    if 'resting_hr' in readiness:
        # We have real wellness data!
        print(f"   Resting HR:        {readiness['resting_hr']} bpm (actual RHR)")
        print(f"   Body Battery:      {readiness['body_battery']}")
        print(f"   Stress (avg):      {readiness['stress_avg']}")
        print(f"   Sleep Score:       {readiness['sleep_score_avg']}")
        print(f"   Data Source:       {readiness['data_source']}")
    else:
        # Fallback to activity HR
        print(f"   HRV Status:        {readiness.get('hrv_status', 'N/A')} ({readiness.get('hrv_deviation', 'N/A')})")
        print(f"   Activity HR (avg): {readiness.get('avg_activity_hr', 'N/A')} bpm")
        if 'note' in readiness:
            print(f"   ⚠️  NOTE: {readiness['note']}")
        print(f"   Sleep Score:       {readiness['sleep_score_avg']}")
    print()
    
    print("2️⃣ TRAINING LOAD & VOLUME")
    print("-" * 70)
    print(f"   Acute Load (7d):   {acute_load:.0f} minutes")
    print(f"   Chronic Load (28d): {chronic_load:.0f} minutes")
    print(f"   ACWR:              {acwr:.2f}" if acwr else "   ACWR:              N/A")
    if acwr:
        if acwr > 1.5:
            print(f"   ⚠️  RISK LEVEL:       🔴 HIGH - Reduce volume immediately!")
        elif acwr > 1.3:
            print(f"   ⚡ RISK LEVEL:       🟡 ELEVATED - Monitor closely")
        else:
            print(f"   ✅ RISK LEVEL:       🟢 OPTIMAL (0.8-1.3)")
    
    print()
    print(f"   Time in Zones ({analysis_days}-day analysis):")
    print(f"      Zone 1-2 (Easy):  {hr_zones['Z1_2']}")
    print(f"      Zone 3 (Tempo):   {hr_zones['Z3']}")
    print(f"      Zone 4-5 (Hard):  {hr_zones['Z4_5']}")
    print(f"   Target: 80% in Z1-2, 20% in Z3-5")
    print()
    
    print(f"3️⃣ EFFICIENCY METRICS ({analysis_days}-Day Analysis)")
    print("3️⃣ EFFICIENCY METRICS (60-Day Analysis)")
    print("-" * 70)
    print(f"   🏃 Run Decoupling:    {run_decoupling}")
    print(f"      < 5%: Strong aerobic base, ready for intensity")
    print(f"      > 5%: Need more Zone 2 volume")
    print()
    print(f"   🏊 Swim SWOLF:        {swim_swolf:.1f}" if swim_swolf else "   🏊 Swim SWOLF:        N/A")
    print(f"      Lower = better technique (strokes + time per length)")
    print()
    print(f"   🚴 Bike EF Trend:     {bike_ef}")
    print(f"      Efficiency Factor (Speed/HR) over time")
    print()
    
    # Display FTP if available
    if ftp_data:
        print(f"   🔋 FTP (Power):       {ftp_data['ftp_watts']}W ({ftp_data['source']})")
        if 'best_20min_watts' in ftp_data:
            print(f"      Activity estimate: {ftp_data.get('best_20min_watts', 'N/A')}W from best 20min")
            print(f"      Latest power workout: {ftp_data.get('best_20min_workout', 'N/A')[:50]}")
        if 'note' in ftp_data:
            print(f"      {ftp_data['note']}")
    else:
        print(f"   🔋 FTP (Power):       N/A (no power data)")
        print(f"      Set FTP=xxx in .env for TrainerRoad value")
    print()
    
    print("4️⃣ TRIATHLON-SPECIFIC")
    print("-" * 70)
    print(f"   Brick Performance: {brick_perf}")
    print(f"      Pace lag on bike-to-run transitions")
    print()
    
    print("🚴 TRAINERROAD WORKOUT GUIDANCE")
    print("=" * 70)
    print(f"   📋 Next Workout:    {tr_recommendations['workout_type']}")
    print(f"   🎯 Target TSS:      {tr_recommendations['target_tss']}")
    print(f"   ⚡ Target IF:        {tr_recommendations['target_if']:.2f}")
    print()
    print("   💡 Why?")
    for reason in tr_recommendations["reasoning"]:
        print(f"      • {reason}")
    print()
    print("   📝 Suggested TrainerRoad Workouts:")
    for workout in tr_recommendations["specific_workouts"]:
        print(f"      • {workout}")
    print()
    
    print("📅 TRAINING PERIODIZATION")
    print("=" * 70)
    if race_info:
        print(f"   🏁 Race Date:       {race_info['date'].strftime('%B %d, %Y')}")
        print(f"   🏆 Race Type:       {race_info['type'].replace('_', ' ').title()}")
        print(f"   ⏱️  Weeks to Race:   {phase_info['weeks_to_race']:.1f}")
        print()
    print(f"   📍 Current Phase:   {phase_info['phase']}")
    print(f"   📖 Description:     {phase_info['description']}")
    print()
    print(f"   🎯 Phase Targets:")
    print(f"      Weekly TSS:      {phase_recs['weekly_tss']}")
    print(f"      Intensity Split: {phase_recs['intensity_split']}")
    print(f"      Focus:           {phase_recs['focus']}")
    print()
    print(f"   🚴 Phase-Specific Workouts:")
    for workout in phase_recs['trainerroad_workouts']:
        print(f"      • {workout}")
    print()
    print()
    
    print("=" * 70)
    print("🤖 AI COACH PROMPT (Copy this to Gemini/ChatGPT/Claude)")
    print("=" * 70)
    print()
    
    # Generate AI coach prompt
    ai_prompt = periodization.generate_ai_coach_prompt(coaching_data, phase_info, phase_recs)
    print(ai_prompt)
    print()
    print("=" * 70)
    print("Copy the prompt above and paste it into your AI coach for detailed guidance!")
    print("=" * 70)
    print()
    print("📝 ADDITIONAL COACHING RECOMMENDATIONS")
    print("=" * 70)
    if notes:
        for note in notes:
            print(f"   {note}")
    else:
        print("   ✅ Training load and metrics look balanced - keep going!")
    print()
    
    # Add AI prompt to coaching data before saving
    coaching_data['ai_coach_prompt'] = ai_prompt
    
    # Save JSON output
    json_output_path = Path("./data/coaching_brief.json")
    with open(json_output_path, 'w') as f:
        json.dump(coaching_data, f, indent=2)
    
    print(f"💾 Saved JSON coaching brief to: {json_output_path}")
    print()
    print("📋 COPY FOR AI COACH:")
    print("-" * 70)
    print(json.dumps(coaching_data, indent=2))
    print()


def main():
    """Entry point"""
    try:
        generate_coaching_brief()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please download data first using the Download button.")
    except Exception as e:
        print(f"Error generating coaching brief: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
