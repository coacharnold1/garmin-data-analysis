#!/usr/bin/env python3
"""
Garmin Data Analysis Script
Analyzes downloaded Garmin activity data and generates statistics.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


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
        df['month'] = df['startTimeLocal'].dt.to_period('M')
        df['week'] = df['startTimeLocal'].dt.to_period('W')
    
    print(f"✓ Loaded {len(df)} activities")
    return df


def analyze_overall_stats(df):
    """Calculate overall statistics."""
    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)
    
    # Total activities
    print(f"\nTotal Activities: {len(df)}")
    
    # Activity types breakdown
    if 'activityType' in df.columns:
        print("\nActivity Types:")
        for activity_type, count in df['activityType'].value_counts().items():
            print(f"  {activity_type}: {count}")
    
    # Distance stats
    if 'distanceKm' in df.columns:
        total_distance = df['distanceKm'].sum()
        avg_distance = df['distanceKm'].mean()
        max_distance = df['distanceKm'].max()
        print(f"\nDistance:")
        print(f"  Total: {total_distance:.2f} km")
        print(f"  Average per activity: {avg_distance:.2f} km")
        print(f"  Longest activity: {max_distance:.2f} km")
    
    # Duration stats
    if 'durationMin' in df.columns:
        total_time = df['durationMin'].sum()
        avg_time = df['durationMin'].mean()
        print(f"\nDuration:")
        print(f"  Total: {total_time/60:.2f} hours")
        print(f"  Average per activity: {avg_time:.2f} minutes")
    
    # Calories
    if 'calories' in df.columns:
        total_calories = df['calories'].sum()
        avg_calories = df['calories'].mean()
        print(f"\nCalories:")
        print(f"  Total: {total_calories:,.0f} kcal")
        print(f"  Average per activity: {avg_calories:.0f} kcal")
    
    # Heart rate stats
    if 'averageHR' in df.columns and df['averageHR'].notna().any():
        avg_hr = df['averageHR'].mean()
        max_hr = df['maxHR'].max() if 'maxHR' in df.columns else None
        print(f"\nHeart Rate:")
        print(f"  Average: {avg_hr:.0f} bpm")
        if max_hr:
            print(f"  Maximum recorded: {max_hr:.0f} bpm")


def analyze_by_activity_type(df):
    """Analyze statistics by activity type."""
    if 'activityType' not in df.columns:
        return
    
    print("\n" + "="*60)
    print("STATISTICS BY ACTIVITY TYPE")
    print("="*60)
    
    for activity_type in df['activityType'].unique():
        activity_df = df[df['activityType'] == activity_type]
        print(f"\n{activity_type}:")
        print(f"  Count: {len(activity_df)}")
        
        if 'distanceKm' in df.columns:
            print(f"  Total Distance: {activity_df['distanceKm'].sum():.2f} km")
            print(f"  Avg Distance: {activity_df['distanceKm'].mean():.2f} km")
        
        if 'paceMinPerKm' in df.columns and activity_df['paceMinPerKm'].notna().any():
            avg_pace = activity_df['paceMinPerKm'].mean()
            # Only show pace if it's a reasonable value (not infinity or too slow)
            if avg_pace < 100 and not pd.isna(avg_pace):
                print(f"  Avg Pace: {int(avg_pace)}:{int((avg_pace % 1) * 60):02d} min/km")


def analyze_trends(df):
    """Analyze trends over time."""
    if 'month' not in df.columns:
        return
    
    print("\n" + "="*60)
    print("MONTHLY TRENDS")
    print("="*60)
    
    # Group by month
    monthly = df.groupby('month').agg({
        'activityId': 'count',
        'distanceKm': 'sum',
        'durationMin': 'sum'
    }).rename(columns={'activityId': 'count'})
    
    print("\n{:<15} {:<10} {:<15} {:<15}".format(
        "Month", "Count", "Distance (km)", "Time (hrs)"
    ))
    print("-" * 60)
    
    for month, row in monthly.iterrows():
        print("{:<15} {:<10} {:<15.2f} {:<15.2f}".format(
            str(month),
            int(row['count']),
            row['distanceKm'],
            row['durationMin'] / 60
        ))
    
    # Calculate growth
    if len(monthly) >= 2:
        first_month_dist = monthly['distanceKm'].iloc[0]
        last_month_dist = monthly['distanceKm'].iloc[-1]
        growth = ((last_month_dist - first_month_dist) / first_month_dist) * 100
        print(f"\nDistance change from first to last month: {growth:+.1f}%")


def analyze_personal_records(df):
    """Find personal records."""
    print("\n" + "="*60)
    print("PERSONAL RECORDS")
    print("="*60)
    
    # Longest distance
    if 'distanceKm' in df.columns and df['distanceKm'].notna().any():
        longest_idx = df['distanceKm'].idxmax()
        longest = df.loc[longest_idx]
        print(f"\nLongest Distance:")
        print(f"  {longest['distanceKm']:.2f} km")
        if 'activityName' in df.columns:
            print(f"  Activity: {longest['activityName']}")
        if 'startTimeLocal' in df.columns:
            print(f"  Date: {longest['startTimeLocal']}")
    
    # Fastest pace (running)
    if 'paceMinPerKm' in df.columns and df['paceMinPerKm'].notna().any():
        fastest_idx = df['paceMinPerKm'].idxmin()
        fastest = df.loc[fastest_idx]
        pace = fastest['paceMinPerKm']
        print(f"\nFastest Pace:")
        print(f"  {int(pace)}:{int((pace % 1) * 60):02d} min/km")
        if 'distanceKm' in df.columns:
            print(f"  Distance: {fastest['distanceKm']:.2f} km")
        if 'startTimeLocal' in df.columns:
            print(f"  Date: {fastest['startTimeLocal']}")
    
    # Most calories burned
    if 'calories' in df.columns and df['calories'].notna().any():
        max_calories_idx = df['calories'].idxmax()
        max_cal = df.loc[max_calories_idx]
        print(f"\nMost Calories Burned:")
        print(f"  {max_cal['calories']:,.0f} kcal")
        if 'activityName' in df.columns:
            print(f"  Activity: {max_cal['activityName']}")
        if 'startTimeLocal' in df.columns:
            print(f"  Date: {max_cal['startTimeLocal']}")


def analyze_weekly_patterns(df):
    """Analyze weekly activity patterns."""
    if 'startTimeLocal' not in df.columns:
        return
    
    print("\n" + "="*60)
    print("WEEKLY PATTERNS")
    print("="*60)
    
    # Add day of week
    df['dayOfWeek'] = pd.to_datetime(df['startTimeLocal']).dt.day_name()
    
    # Count by day of week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['dayOfWeek'].value_counts().reindex(day_order, fill_value=0)
    
    print("\nActivities by Day of Week:")
    for day, count in day_counts.items():
        bar = "█" * int(count)
        print(f"  {day:<10}: {bar} ({count})")


def main():
    """Main execution function."""
    print("=" * 60)
    print("GARMIN DATA ANALYZER")
    print("=" * 60)
    
    # Load data
    df = load_activities()
    if df is None:
        return
    
    # Run analyses
    analyze_overall_stats(df)
    analyze_by_activity_type(df)
    analyze_trends(df)
    analyze_personal_records(df)
    analyze_weekly_patterns(df)
    
    print("\n" + "="*60)
    print("✓ Analysis complete!")
    print("\nNext: Run 'python visualize_data.py' to create charts")
    print("="*60)


if __name__ == "__main__":
    main()
