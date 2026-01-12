#!/usr/bin/env python3
"""
Garmin Data Visualization Script
Creates charts and graphs from Garmin activity data.
"""

import os
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuration
DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
ACTIVITIES_CSV = DATA_DIR / 'activities.csv'
OUTPUT_DIR = DATA_DIR / 'visualizations'

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


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
        df['dayOfWeek'] = df['startTimeLocal'].dt.day_name()
    
    print(f"✓ Loaded {len(df)} activities")
    return df


def plot_activity_timeline(df):
    """Plot activities over time."""
    if 'date' not in df.columns or 'distanceKm' not in df.columns:
        return
    
    print("Creating activity timeline...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Distance over time
    daily = df.groupby('date')['distanceKm'].sum().reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    
    ax1.plot(daily['date'], daily['distanceKm'], marker='o', linewidth=2, markersize=6)
    ax1.set_title('Daily Distance Over Time', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Distance (km)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Activity count over time
    activity_counts = df.groupby('date').size().reset_index(name='count')
    activity_counts['date'] = pd.to_datetime(activity_counts['date'])
    
    ax2.bar(activity_counts['date'], activity_counts['count'], alpha=0.7, color='steelblue')
    ax2.set_title('Number of Activities per Day', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Number of Activities', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    save_plot('activity_timeline.png')
    plt.close()


def plot_monthly_trends(df):
    """Plot monthly activity trends."""
    if 'month' not in df.columns:
        return
    
    print("Creating monthly trends chart...")
    
    monthly = df.groupby('month').agg({
        'activityId': 'count',
        'distanceKm': 'sum',
        'durationMin': 'sum'
    }).rename(columns={'activityId': 'count'})
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Activity count
    monthly['count'].plot(kind='bar', ax=axes[0], color='steelblue', alpha=0.7)
    axes[0].set_title('Activities per Month', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Month', fontsize=11)
    axes[0].set_ylabel('Number of Activities', fontsize=11)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Total distance
    monthly['distanceKm'].plot(kind='bar', ax=axes[1], color='green', alpha=0.7)
    axes[1].set_title('Total Distance per Month', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Month', fontsize=11)
    axes[1].set_ylabel('Distance (km)', fontsize=11)
    axes[1].tick_params(axis='x', rotation=45)
    
    # Total time
    (monthly['durationMin'] / 60).plot(kind='bar', ax=axes[2], color='orange', alpha=0.7)
    axes[2].set_title('Total Time per Month', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Month', fontsize=11)
    axes[2].set_ylabel('Time (hours)', fontsize=11)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_plot('monthly_trends.png')
    plt.close()


def plot_activity_types(df):
    """Plot activity type distribution."""
    if 'activityType' not in df.columns:
        return
    
    print("Creating activity type charts...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Count by activity type
    type_counts = df['activityType'].value_counts()
    colors = sns.color_palette("husl", len(type_counts))
    
    ax1.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax1.set_title('Activity Type Distribution (by count)', fontsize=14, fontweight='bold')
    
    # Distance by activity type
    if 'distanceKm' in df.columns:
        type_distance = df.groupby('activityType')['distanceKm'].sum().sort_values(ascending=False)
        type_distance.plot(kind='barh', ax=ax2, color=colors, alpha=0.7)
        ax2.set_title('Total Distance by Activity Type', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Distance (km)', fontsize=11)
        ax2.set_ylabel('Activity Type', fontsize=11)
    
    plt.tight_layout()
    save_plot('activity_types.png')
    plt.close()


def plot_heart_rate_analysis(df):
    """Plot heart rate statistics."""
    if 'averageHR' not in df.columns or not df['averageHR'].notna().any():
        print("Skipping heart rate analysis (no data available)")
        return
    
    print("Creating heart rate analysis...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Heart rate distribution
    df_hr = df[df['averageHR'].notna()]
    ax1.hist(df_hr['averageHR'], bins=20, color='red', alpha=0.7, edgecolor='black')
    ax1.axvline(df_hr['averageHR'].mean(), color='blue', linestyle='--', 
                linewidth=2, label=f"Average: {df_hr['averageHR'].mean():.0f} bpm")
    ax1.set_title('Average Heart Rate Distribution', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Heart Rate (bpm)', fontsize=11)
    ax1.set_ylabel('Number of Activities', fontsize=11)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Heart rate over time
    if 'date' in df.columns:
        hr_by_date = df_hr.groupby('date')['averageHR'].mean().reset_index()
        hr_by_date['date'] = pd.to_datetime(hr_by_date['date'])
        ax2.plot(hr_by_date['date'], hr_by_date['averageHR'], 
                marker='o', linewidth=2, markersize=5, color='red')
        ax2.set_title('Average Heart Rate Over Time', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11)
        ax2.set_ylabel('Average Heart Rate (bpm)', fontsize=11)
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_plot('heart_rate_analysis.png')
    plt.close()


def plot_pace_analysis(df):
    """Plot pace statistics for running activities."""
    if 'paceMinPerKm' not in df.columns or not df['paceMinPerKm'].notna().any():
        print("Skipping pace analysis (no data available)")
        return
    
    print("Creating pace analysis...")
    
    df_pace = df[df['paceMinPerKm'].notna()].copy()
    
    # Filter out unrealistic paces (< 3 min/km or > 15 min/km)
    df_pace = df_pace[(df_pace['paceMinPerKm'] >= 3) & (df_pace['paceMinPerKm'] <= 15)]
    
    if len(df_pace) == 0:
        print("No valid pace data available")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pace distribution
    ax1.hist(df_pace['paceMinPerKm'], bins=20, color='green', alpha=0.7, edgecolor='black')
    avg_pace = df_pace['paceMinPerKm'].mean()
    ax1.axvline(avg_pace, color='blue', linestyle='--', 
                linewidth=2, label=f"Average: {int(avg_pace)}:{int((avg_pace % 1) * 60):02d} min/km")
    ax1.set_title('Running Pace Distribution', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Pace (min/km)', fontsize=11)
    ax1.set_ylabel('Number of Activities', fontsize=11)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Pace over distance (scatter plot)
    if 'distanceKm' in df.columns:
        ax2.scatter(df_pace['distanceKm'], df_pace['paceMinPerKm'], 
                   alpha=0.6, s=50, color='green')
        ax2.set_title('Pace vs Distance', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Distance (km)', fontsize=11)
        ax2.set_ylabel('Pace (min/km)', fontsize=11)
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_plot('pace_analysis.png')
    plt.close()


def plot_weekly_pattern(df):
    """Plot weekly activity patterns."""
    if 'dayOfWeek' not in df.columns:
        return
    
    print("Creating weekly pattern chart...")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['dayOfWeek'].value_counts().reindex(day_order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['red' if day in ['Saturday', 'Sunday'] else 'steelblue' for day in day_order]
    day_counts.plot(kind='bar', ax=ax, color=colors, alpha=0.7, edgecolor='black')
    
    ax.set_title('Activity Distribution by Day of Week', fontsize=16, fontweight='bold')
    ax.set_xlabel('Day of Week', fontsize=12)
    ax.set_ylabel('Number of Activities', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    save_plot('weekly_pattern.png')
    plt.close()


def save_plot(filename):
    """Save the current plot to file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    filepath = OUTPUT_DIR / filename
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {filepath}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("GARMIN DATA VISUALIZER")
    print("=" * 60)
    
    # Load data
    df = load_activities()
    if df is None:
        return
    
    print("\nGenerating visualizations...")
    print("(Charts will be displayed and saved to data/visualizations/)\n")
    
    # Create visualizations
    plot_activity_timeline(df)
    plot_monthly_trends(df)
    plot_activity_types(df)
    plot_heart_rate_analysis(df)
    plot_pace_analysis(df)
    plot_weekly_pattern(df)
    
    print("\n" + "="*60)
    print("✓ Visualization complete!")
    print(f"\nCharts saved to: {OUTPUT_DIR.absolute()}")
    print("="*60)


if __name__ == "__main__":
    main()
