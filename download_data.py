#!/usr/bin/env python3
"""
Garmin Data Download Script
Downloads activity data from Garmin Connect and saves it locally.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectAuthenticationError
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()

# Configuration
GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')
DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
MAX_ACTIVITIES = int(os.getenv('MAX_ACTIVITIES', 100))


def authenticate_garmin():
    """Authenticate with Garmin Connect."""
    try:
        print("Authenticating with Garmin Connect...")
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()
        print("✓ Authentication successful")
        return client
    except GarminConnectAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPlease check your credentials in the .env file:")
        print("- GARMIN_EMAIL should be your Garmin Connect email")
        print("- GARMIN_PASSWORD should be your password")
        return None


def download_activities(client, limit=MAX_ACTIVITIES):
    """Download recent activities from Garmin Connect."""
    try:
        print(f"\nDownloading last {limit} activities...")
        activities = client.get_activities(0, limit)
        print(f"✓ Downloaded {len(activities)} activities")
        return activities
    except Exception as e:
        print(f"✗ Error downloading activities: {e}")
        return []


def download_activity_details(client, activity_id):
    """Download detailed data for a specific activity."""
    try:
        details = client.get_activity_evaluation(activity_id)
        return details
    except Exception as e:
        print(f"  Warning: Could not fetch details for activity {activity_id}: {e}")
        return None


def download_sleep_data(client, days=30):
    """Download sleep data for the last N days."""
    sleep_data = []
    print(f"\nDownloading sleep data for last {days} days...")
    
    try:
        today = datetime.now().date()
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            try:
                sleep_info = client.get_sleep_data(date_str)
                if sleep_info:
                    sleep_data.append(sleep_info)
                    if i < 3:  # Show first 3 days
                        print(f"  ✓ {date_str}: Found sleep data")
            except Exception as e:
                if i < 3:
                    print(f"  - {date_str}: No data ({str(e)[:50]})")
                continue
        
        print(f"✓ Downloaded sleep data for {len(sleep_data)} days")
        return sleep_data
    except Exception as e:
        print(f"✗ Error downloading sleep data: {e}")
        return []


def download_wellness_data(client, days=30):
    """Download comprehensive wellness data: HRV, stress, body battery, heart rates."""
    wellness_data = {
        'heart_rates': [],
        'hrv': [],
        'stress': [],
        'body_battery': []
    }
    
    print(f"\nDownloading wellness data for last {days} days...")
    
    try:
        today = datetime.now().date()
        
        # Get heart rates (includes resting HR!)
        try:
            print("  Fetching daily heart rates...")
            hr_data = client.get_heart_rates(today.isoformat())
            if hr_data:
                wellness_data['heart_rates'] = hr_data
                if 'restingHeartRate' in hr_data:
                    print(f"    ✓ Resting HR: {hr_data.get('restingHeartRate')} bpm")
        except Exception as e:
            print(f"    - Heart rates: {str(e)[:60]}")
        
        # Get HRV data
        try:
            print("  Fetching HRV data...")
            hrv_data = client.get_hrv_data(today.isoformat())
            if hrv_data:
                wellness_data['hrv'] = hrv_data
                print(f"    ✓ HRV data retrieved")
        except Exception as e:
            print(f"    - HRV: {str(e)[:60]}")
        
        # Get stress data
        try:
            print("  Fetching stress data...")
            stress_data = client.get_stress_data(today.isoformat())
            if stress_data:
                wellness_data['stress'] = stress_data
                print(f"    ✓ Stress data retrieved")
        except Exception as e:
            print(f"    - Stress: {str(e)[:60]}")
        
        # Get body battery
        try:
            print("  Fetching body battery...")
            bb_data = client.get_body_battery(today.isoformat())
            if bb_data:
                wellness_data['body_battery'] = bb_data
                print(f"    ✓ Body battery retrieved")
        except Exception as e:
            print(f"    - Body battery: {str(e)[:60]}")
        
        print(f"✓ Wellness data download complete")
        return wellness_data
        
    except Exception as e:
        print(f"✗ Error downloading wellness data: {e}")
        return wellness_data


def download_training_stats(client):
    """Download training status and stats (VO2 max, FTP, etc.)."""
    stats_data = {}
    
    print(f"\nDownloading training statistics...")
    
    try:
        # Get training status
        try:
            print("  Fetching training status...")
            training_status = client.get_training_status()
            if training_status:
                stats_data['training_status'] = training_status
                print(f"    ✓ Training status retrieved")
        except Exception as e:
            print(f"    - Training status: {str(e)[:60]}")
        
        # Get stats (VO2 max, FTP, etc.)
        try:
            print("  Fetching athlete stats...")
            stats = client.get_stats(datetime.now().isoformat()[:10])
            if stats:
                stats_data['stats'] = stats
                print(f"    ✓ Stats retrieved")
        except Exception as e:
            print(f"    - Stats: {str(e)[:60]}")
        
        # Get max metrics (VO2 max, FTP, lactate threshold)
        try:
            print("  Fetching max metrics (VO2, FTP, thresholds)...")
            max_metrics = client.get_max_metrics(datetime.now().isoformat()[:10])
            if max_metrics:
                stats_data['max_metrics'] = max_metrics
                # Display FTP if available
                if isinstance(max_metrics, dict):
                    for metric in max_metrics.get('metrics', []):
                        if 'cycling' in str(metric).lower() and 'ftp' in str(metric).lower():
                            print(f"    ✓ Cycling FTP found")
                        elif 'vo2' in str(metric).lower():
                            print(f"    ✓ VO2 max data found")
                print(f"    ✓ Max metrics retrieved")
        except Exception as e:
            print(f"    - Max metrics: {str(e)[:60]}")
        
        print(f"✓ Training stats download complete")
        return stats_data
        
    except Exception as e:
        print(f"✗ Error downloading training stats: {e}")
        return stats_data


def save_activities_json(activities, filename='activities.json'):
    """Save activities to JSON file."""
    filepath = DATA_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(activities, f, indent=2, default=str)
    print(f"✓ Saved raw data to {filepath}")


def save_activities_csv(activities, filename='activities.csv'):
    """Save activities to CSV file for easy analysis."""
    # Convert to DataFrame
    df = pd.DataFrame(activities)
    
    # Extract activity type name from dictionary
    if 'activityType' in df.columns:
        df['activityType'] = df['activityType'].apply(
            lambda x: x.get('typeKey', 'unknown') if isinstance(x, dict) else str(x)
        )
    
    # Select and rename key columns
    columns_to_keep = [
        'activityId', 'activityName', 'activityType', 'startTimeLocal',
        'distance', 'duration', 'averageSpeed', 'averageHR', 'maxHR',
        'calories', 'elevationGain', 'averageRunningCadenceInStepsPerMinute'
    ]
    
    # Filter columns that exist
    available_columns = [col for col in columns_to_keep if col in df.columns]
    df_filtered = df[available_columns].copy()
    
    # Convert date strings to datetime
    if 'startTimeLocal' in df_filtered.columns:
        df_filtered['startTimeLocal'] = pd.to_datetime(df_filtered['startTimeLocal'])
    
    # Convert distance from meters to kilometers
    if 'distance' in df_filtered.columns:
        df_filtered['distanceKm'] = df_filtered['distance'] / 1000
    
    # Convert duration from seconds to minutes
    if 'duration' in df_filtered.columns:
        df_filtered['durationMin'] = df_filtered['duration'] / 60
    
    # Calculate pace (min/km) for running activities
    if 'averageSpeed' in df_filtered.columns and df_filtered['averageSpeed'].notna().any():
        # averageSpeed is in m/s, convert to min/km
        df_filtered['paceMinPerKm'] = (1000 / df_filtered['averageSpeed']) / 60
    
    # Filter out outliers - unrealistic speeds from forgetting to stop device
    if 'averageSpeed' in df_filtered.columns and 'activityType' in df_filtered.columns:
        # For cycling activities: max realistic speed is 45 mph = 20.1 m/s
        cycling_types = ['cycling', 'road_biking', 'indoor_cycling', 'mountain_biking']
        cycling_mask = df_filtered['activityType'].isin(cycling_types)
        df_filtered.loc[cycling_mask & (df_filtered['averageSpeed'] > 20.1), 'averageSpeed'] = np.nan
        df_filtered.loc[cycling_mask & (df_filtered['averageSpeed'] > 20.1), 'paceMinPerKm'] = np.nan
        
        # For running activities: min realistic pace is 6:30 min/mile = 4:02 min/km
        running_types = ['running', 'treadmill_running', 'trail_running', 'track_running']
        running_mask = df_filtered['activityType'].isin(running_types)
        df_filtered.loc[running_mask & (df_filtered['paceMinPerKm'] < 4.03), 'averageSpeed'] = np.nan
        df_filtered.loc[running_mask & (df_filtered['paceMinPerKm'] < 4.03), 'paceMinPerKm'] = np.nan
    
    # Save to CSV
    filepath = DATA_DIR / filename
    df_filtered.to_csv(filepath, index=False)
    print(f"✓ Saved CSV data to {filepath}")
    
    return df_filtered


def print_summary(activities):
    """Print a summary of downloaded activities."""
    if not activities:
        return
    
    print("\n" + "="*60)
    print("ACTIVITY SUMMARY")
    print("="*60)
    
    df = pd.DataFrame(activities)
    
    # Extract activity type name from dictionary
    if 'activityType' in df.columns:
        df['activityType'] = df['activityType'].apply(
            lambda x: x.get('typeKey', 'unknown') if isinstance(x, dict) else str(x)
        )
    
    # Activity types
    if 'activityType' in df.columns:
        print("\nActivity Types:")
        type_counts = df['activityType'].value_counts()
        for activity_type, count in type_counts.items():
            print(f"  {activity_type}: {count}")
    
    # Total distance
    if 'distance' in df.columns:
        total_km = df['distance'].sum() / 1000
        print(f"\nTotal Distance: {total_km:.2f} km")
    
    # Total time
    if 'duration' in df.columns:
        total_hours = df['duration'].sum() / 3600
        print(f"Total Time: {total_hours:.2f} hours")
    
    # Date range
    if 'startTimeLocal' in df.columns:
        dates = pd.to_datetime(df['startTimeLocal'])
        print(f"\nDate Range: {dates.min()} to {dates.max()}")
    
    print("="*60)


def main():
    """Main execution function."""
    print("=" * 60)
    print("GARMIN DATA DOWNLOADER")
    print("=" * 60)
    
    # Check credentials
    if not GARMIN_EMAIL or not GARMIN_PASSWORD:
        print("\n✗ Error: Garmin credentials not found!")
        print("\nPlease create a .env file with:")
        print("  GARMIN_EMAIL=your.email@example.com")
        print("  GARMIN_PASSWORD=your_password")
        return
    
    # Create data directory
    DATA_DIR.mkdir(exist_ok=True)
    print(f"Data directory: {DATA_DIR.absolute()}")
    
    # Authenticate
    client = authenticate_garmin()
    if not client:
        return
    
    # Download activities
    activities = download_activities(client, MAX_ACTIVITIES)
    if not activities:
        print("✗ No activities downloaded")
        return
    
    # Download sleep data
    sleep_data = download_sleep_data(client, days=30)
    
    # Download wellness data (HRV, stress, body battery, resting HR)
    wellness_data = download_wellness_data(client, days=30)
    
    # Download training stats (VO2 max, FTP, training status)
    training_stats = download_training_stats(client)
    
    # Save data
    save_activities_json(activities)
    save_activities_csv(activities)
    
    # Save sleep data
    if sleep_data:
        sleep_file = DATA_DIR / 'sleep.json'
        with open(sleep_file, 'w') as f:
            json.dump(sleep_data, f, indent=2, default=str)
        print(f"✓ Saved sleep data to {sleep_file}")
    
    # Save wellness data
    if wellness_data and any(wellness_data.values()):
        wellness_file = DATA_DIR / 'wellness.json'
        with open(wellness_file, 'w') as f:
            json.dump(wellness_data, f, indent=2, default=str)
        print(f"✓ Saved wellness data to {wellness_file}")
    
    # Save training stats
    if training_stats:
        stats_file = DATA_DIR / 'training_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(training_stats, f, indent=2, default=str)
        print(f"✓ Saved training stats to {stats_file}")
    
    # Print summary
    print_summary(activities)
    
    print("\n✓ Download complete!")
    print(f"\nNext steps:")
    print(f"  1. Run 'python analyze_data.py' to analyze your data")
    print(f"  2. Run 'python visualize_data.py' to create visualizations")


if __name__ == "__main__":
    main()
