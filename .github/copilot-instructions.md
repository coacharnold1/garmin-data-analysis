# Garmin Data Analysis App

## Project Overview
Python application to download and analyze Garmin Connect activity data.

## Tech Stack
- Python 3.8+
- garminconnect library for API access
- pandas for data analysis
- matplotlib for visualization
- python-dotenv for configuration

## Project Structure
- `download_data.py` - Main script to download Garmin data
- `analyze_data.py` - Analysis module for processing activities
- `visualize_data.py` - Visualization module for charts
- `data/` - Storage for downloaded activity data
- `.env` - Garmin credentials (not in version control)

## Development Guidelines
- Store credentials securely in .env file
- Save downloaded data as JSON/CSV for offline analysis
- Use pandas DataFrames for data processing
- Follow Python best practices (PEP 8)
