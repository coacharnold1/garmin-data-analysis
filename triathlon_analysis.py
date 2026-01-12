#!/usr/bin/env python3
"""
Triathlon-Specific Training Analysis
Advanced analysis for triathlon training including recovery metrics, training load, and sport-specific insights.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict


# Configuration
DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
ACTIVITIES_CSV = DATA_DIR / 'activities.csv'


def load_activities():
    """Load activities from CSV file."""
    if not ACTIVITIES_CSV.exists():
        print(f"✗ Error: No data file found at {ACTIVITIES_CSV}")
        print("\nPlease run 'python download_data.py' first to download your data.")
        return None
    
    print(f"Loading data from {ACTIVITIES_CSV}...")
    df = pd.read_csv(ACTIVITIES_CSV)
    
    # Convert date column
    if 'startTimeLocal' in df.columns:
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])
        df['date'] = df['startTimeLocal'].dt.date
        df['week'] = df['startTimeLocal'].dt.to_period('W')
    
    print(f"✓ Loaded {len(df)} activities")
    return df


def calculate_training_stress_score(df):
    """Calculate Training Stress Score (TSS) for activities."""
    print("\n" + "="*60)
    print("TRAINING STRESS SCORE (TSS) ANALYSIS")
    print("="*60)
    
    if 'durationMin' not in df.columns:
        print("Insufficient data for TSS calculation")
        return df
    
    # Simplified TSS calculation based on duration and intensity
    # Real TSS requires FTP/threshold data, this is an approximation
    df['estimated_tss'] = 0.0
    
    if 'averageHR' in df.columns and df['averageHR'].notna().any():
        # Use HR-based TSS estimation
        # Assumes max HR of 185 (adjust based on your data)
        max_hr = df['maxHR'].max() if 'maxHR' in df.columns else 185
        threshold_hr = max_hr * 0.85  # Approximate threshold
        
        for idx, row in df.iterrows():
            if pd.notna(row['averageHR']) and pd.notna(row['durationMin']):
                intensity_factor = row['averageHR'] / threshold_hr
                tss = (row['durationMin'] / 60) * intensity_factor ** 2 * 100
                df.at[idx, 'estimated_tss'] = tss
    else:
        # Duration-based estimation (rough approximation)
        df['estimated_tss'] = df['durationMin'] * 0.8
    
    # Calculate weekly TSS
    if 'week' in df.columns:
        weekly_tss = df.groupby('week')['estimated_tss'].sum()
        print("\nWeekly Training Stress:")
        for week, tss in weekly_tss.tail(8).items():
            print(f"  Week {week}: {tss:.0f} TSS")
    
    return df


def calculate_training_load_balance(df):
    """Calculate Acute vs Chronic Training Load and Training Stress Balance."""
    print("\n" + "="*60)
    print("TRAINING LOAD BALANCE (Acute vs Chronic)")
    print("="*60)
    
    if 'estimated_tss' not in df.columns:
        df = calculate_training_stress_score(df)
    
    # Sort by date
    df_sorted = df.sort_values('startTimeLocal')
    
    # Calculate rolling averages
    # Acute Load: 7-day average
    # Chronic Load: 42-day average (6 weeks)
    df_sorted['acute_load'] = df_sorted['estimated_tss'].rolling(window=7, min_periods=1).mean()
    df_sorted['chronic_load'] = df_sorted['estimated_tss'].rolling(window=42, min_periods=7).mean()
    
    # Training Stress Balance (TSB) = Chronic - Acute
    # Positive TSB = Fresh, Negative TSB = Fatigued
    df_sorted['tsb'] = df_sorted['chronic_load'] - df_sorted['acute_load']
    
    # Acute:Chronic Workload Ratio (ACWR)
    df_sorted['acwr'] = df_sorted['acute_load'] / df_sorted['chronic_load']
    
    # Show recent trends
    recent = df_sorted.tail(10)
    print("\nRecent Training Load Trends:")
    print("{:<12} {:<12} {:<12} {:<12} {:<10}".format(
        "Date", "Acute (7d)", "Chronic (42d)", "TSB", "ACWR"
    ))
    print("-" * 60)
    
    for _, row in recent.iterrows():
        if pd.notna(row.get('date')):
            print("{:<12} {:<12.0f} {:<12.0f} {:<12.0f} {:<10.2f}".format(
                str(row['date']),
                row.get('acute_load', 0),
                row.get('chronic_load', 0),
                row.get('tsb', 0),
                row.get('acwr', 0)
            ))
    
    # Interpret current status
    if len(recent) > 0:
        latest = recent.iloc[-1]
        tsb = latest.get('tsb', 0)
        acwr = latest.get('acwr', 0)
        
        print("\n" + "="*60)
        print("CURRENT TRAINING STATUS")
        print("="*60)
        
        if tsb < -20:
            print("🔴 Status: OVERREACHING - High fatigue, recovery needed")
        elif tsb < 0:
            print("🟡 Status: BUILDING - Productive training load")
        elif tsb < 20:
            print("🟢 Status: FRESH - Ready for hard training or racing")
        else:
            print("⚪ Status: DETRAINING - May be losing fitness")
        
        print(f"\nACWR: {acwr:.2f}")
        if acwr > 1.5:
            print("⚠️  High injury risk - Consider reducing volume")
        elif acwr > 1.3:
            print("⚠️  Elevated injury risk - Monitor closely")
        elif acwr >= 0.8:
            print("✓ Optimal training zone")
        else:
            print("📉 Under-training - Room to increase load")
    
    return df_sorted


def analyze_sport_specific_metrics(df):
    """Analyze sport-specific metrics for swim, bike, run."""
    print("\n" + "="*60)
    print("SPORT-SPECIFIC PERFORMANCE METRICS")
    print("="*60)
    
    # Swimming Analysis
    swim_types = ['lap_swimming', 'open_water_swimming']
    swim_data = df[df['activityType'].isin(swim_types)]
    
    if len(swim_data) > 0:
        print("\n🏊 SWIMMING:")
        print(f"  Total sessions: {len(swim_data)}")
        if 'distanceKm' in swim_data.columns:
            total_swim = swim_data['distanceKm'].sum()
            avg_session = swim_data['distanceKm'].mean()
            print(f"  Total distance: {total_swim:.2f} km")
            print(f"  Avg per session: {avg_session:.2f} km")
        
        if 'paceMinPerKm' in swim_data.columns:
            avg_pace = swim_data['paceMinPerKm'].mean()
            if pd.notna(avg_pace) and avg_pace < 100:
                # Convert to pace per 100m
                pace_per_100m = avg_pace / 10
                print(f"  Avg pace: {pace_per_100m:.1f} min/100m")
        
        # Trend analysis
        if len(swim_data) >= 3:
            recent_pace = swim_data.tail(3)['paceMinPerKm'].mean()
            older_pace = swim_data.head(3)['paceMinPerKm'].mean()
            if pd.notna(recent_pace) and pd.notna(older_pace):
                improvement = ((older_pace - recent_pace) / older_pace) * 100
                print(f"  Pace trend: {improvement:+.1f}% (recent vs early)")
    
    # Cycling Analysis
    bike_types = ['cycling', 'road_biking', 'indoor_cycling', 'mountain_biking']
    bike_data = df[df['activityType'].isin(bike_types)]
    
    if len(bike_data) > 0:
        print("\n🚴 CYCLING:")
        print(f"  Total sessions: {len(bike_data)}")
        if 'distanceKm' in bike_data.columns:
            total_bike = bike_data['distanceKm'].sum()
            avg_session = bike_data['distanceKm'].mean()
            print(f"  Total distance: {total_bike:.2f} km")
            print(f"  Avg per session: {avg_session:.2f} km")
        
        if 'averageSpeed' in bike_data.columns:
            # Convert m/s to km/h
            bike_data_copy = bike_data.copy()
            bike_data_copy['speed_kmh'] = bike_data_copy['averageSpeed'] * 3.6
            avg_speed = bike_data_copy['speed_kmh'].mean()
            print(f"  Avg speed: {avg_speed:.1f} km/h")
        
        # HR efficiency (if available)
        if 'averageHR' in bike_data.columns and 'averageSpeed' in bike_data.columns:
            bike_data_copy = bike_data[bike_data['averageHR'].notna() & bike_data['averageSpeed'].notna()].copy()
            if len(bike_data_copy) > 0:
                bike_data_copy['hr_efficiency'] = bike_data_copy['averageSpeed'] / bike_data_copy['averageHR']
                avg_efficiency = bike_data_copy['hr_efficiency'].mean()
                print(f"  HR efficiency: {avg_efficiency:.3f} (m/s per bpm)")
    
    # Running Analysis
    run_types = ['running', 'treadmill_running', 'trail_running', 'track_running']
    run_data = df[df['activityType'].isin(run_types)]
    
    if len(run_data) > 0:
        print("\n🏃 RUNNING:")
        print(f"  Total sessions: {len(run_data)}")
        if 'distanceKm' in run_data.columns:
            total_run = run_data['distanceKm'].sum()
            avg_session = run_data['distanceKm'].mean()
            print(f"  Total distance: {total_run:.2f} km")
            print(f"  Avg per session: {avg_session:.2f} km")
        
        if 'paceMinPerKm' in run_data.columns:
            valid_pace = run_data[run_data['paceMinPerKm'].notna() & (run_data['paceMinPerKm'] < 15)]
            if len(valid_pace) > 0:
                avg_pace = valid_pace['paceMinPerKm'].mean()
                print(f"  Avg pace: {int(avg_pace)}:{int((avg_pace % 1) * 60):02d} min/km")
        
        # Cadence analysis
        if 'averageRunningCadenceInStepsPerMinute' in run_data.columns:
            valid_cadence = run_data[run_data['averageRunningCadenceInStepsPerMinute'].notna()]
            if len(valid_cadence) > 0:
                avg_cadence = valid_cadence['averageRunningCadenceInStepsPerMinute'].mean()
                print(f"  Avg cadence: {avg_cadence:.0f} spm")
                if avg_cadence < 170:
                    print("    💡 Tip: Target 180 spm for improved efficiency")


def analyze_recovery_readiness(df):
    """Analyze recovery patterns and readiness indicators."""
    print("\n" + "="*60)
    print("RECOVERY & READINESS ANALYSIS")
    print("="*60)
    
    # Check for rest days
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max())
        activity_dates = df['date'].unique()
        rest_days = len(all_dates) - len(activity_dates)
        
        print(f"\nRest Days: {rest_days} out of {len(all_dates)} total days")
        rest_percentage = (rest_days / len(all_dates)) * 100
        print(f"Recovery ratio: {rest_percentage:.1f}%")
        
        if rest_percentage < 10:
            print("⚠️  Warning: Very few rest days - overtraining risk")
        elif rest_percentage < 20:
            print("💡 Consider adding more recovery days")
        else:
            print("✓ Good recovery balance")
    
    # HR-based recovery analysis
    if 'averageHR' in df.columns:
        print("\n" + "-"*60)
        print("Heart Rate Trends:")
        
        df_sorted = df.sort_values('startTimeLocal')
        if len(df_sorted) >= 10:
            recent_hr = df_sorted.tail(5)['averageHR'].mean()
            older_hr = df_sorted.head(5)['averageHR'].mean()
            
            if pd.notna(recent_hr) and pd.notna(older_hr):
                hr_change = recent_hr - older_hr
                print(f"  Recent avg HR: {recent_hr:.0f} bpm")
                print(f"  Earlier avg HR: {older_hr:.0f} bpm")
                print(f"  Change: {hr_change:+.0f} bpm")
                
                if hr_change > 5:
                    print("  ⚠️  Elevated HR may indicate fatigue or overtraining")
                elif hr_change < -5:
                    print("  ✓ Improving cardiovascular efficiency")


def generate_training_recommendations(df):
    """Generate adaptive training recommendations based on load and recovery."""
    print("\n" + "="*60)
    print("ADAPTIVE TRAINING RECOMMENDATIONS")
    print("="*60)
    
    if 'estimated_tss' not in df.columns:
        df = calculate_training_stress_score(df)
    
    if 'tsb' not in df.columns:
        df = calculate_training_load_balance(df)
    
    # Get most recent status
    df_sorted = df.sort_values('startTimeLocal')
    if len(df_sorted) > 0:
        latest = df_sorted.iloc[-1]
        tsb = latest.get('tsb', 0)
        acwr = latest.get('acwr', 1.0)
        
        print("\nBased on your current training load:\n")
        
        # TSB-based recommendations
        if tsb < -20:
            print("🔴 HIGH FATIGUE - Immediate Action Needed:")
            print("  • Take 2-3 complete rest days")
            print("  • Next workout: Easy Z1-Z2 recovery only")
            print("  • Duration: < 30 minutes")
            print("  • Consider massage or active recovery")
        elif tsb < -10:
            print("🟡 MODERATE FATIGUE - Recovery Focus:")
            print("  • Replace next hard workout with easy session")
            print("  • Keep HR in Z1-Z2 (conversational pace)")
            print("  • Duration: 30-45 minutes max")
            print("  • Focus on technique/form work")
        elif tsb < 5:
            print("🟢 OPTIMAL TRAINING WINDOW:")
            print("  • Ready for quality interval work")
            print("  • Can handle high-intensity sessions")
            print("  • Good time for FTP/threshold tests")
            print("  • Push hard, but monitor recovery")
        else:
            print("⚪ WELL RESTED - Build Phase:")
            print("  • Increase training volume gradually")
            print("  • Add brick workouts (bike-run transitions)")
            print("  • Consider race-pace efforts")
            print("  • Good fitness maintenance or taper phase")
        
        # ACWR-based recommendations
        print("\n" + "-"*60)
        if acwr > 1.5:
            print("⚠️  INJURY RISK: Acute load too high")
            print("  • Reduce volume by 20-30% this week")
            print("  • Focus on recovery and mobility")
        elif acwr > 1.3:
            print("⚠️  ELEVATED RISK: Monitor closely")
            print("  • Maintain current volume (don't increase)")
            print("  • Extra attention to warm-up and cool-down")
        
        # Sport-specific recommendations
        print("\n" + "-"*60)
        print("Next Week's Focus Areas:")
        
        # Analyze recent activity distribution
        recent_week = df_sorted[df_sorted['startTimeLocal'] >= (df_sorted['startTimeLocal'].max() - pd.Timedelta(days=7))]
        
        swim_count = len(recent_week[recent_week['activityType'].str.contains('swim', case=False, na=False)])
        bike_count = len(recent_week[recent_week['activityType'].str.contains('cycling|bike', case=False, na=False)])
        run_count = len(recent_week[recent_week['activityType'].str.contains('running|run', case=False, na=False)])
        
        total_workouts = len(recent_week)
        
        if total_workouts > 0:
            if swim_count < bike_count * 0.3:
                print("  🏊 SWIM: Increase swim volume (currently low)")
            if bike_count < run_count * 1.5:
                print("  🚴 BIKE: Add longer bike sessions")
            if run_count < total_workouts * 0.3:
                print("  🏃 RUN: Incorporate more run sessions")
            
            if swim_count > 0 and bike_count > 0 and run_count > 0:
                print("  ✓ Good tri-sport balance!")
            else:
                print("  💡 Work on underrepresented disciplines")


def main():
    """Main execution function."""
    print("=" * 60)
    print("TRIATHLON TRAINING ANALYSIS")
    print("=" * 60)
    
    # Load data
    df = load_activities()
    if df is None:
        return
    
    # Run analyses
    df = calculate_training_stress_score(df)
    df = calculate_training_load_balance(df)
    analyze_sport_specific_metrics(df)
    analyze_recovery_readiness(df)
    generate_training_recommendations(df)
    
    print("\n" + "="*60)
    print("✓ Triathlon analysis complete!")
    print("="*60)


if __name__ == "__main__":
    main()
