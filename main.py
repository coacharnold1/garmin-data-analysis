#!/usr/bin/env python3
"""
Main entry point for Garmin Data Analysis App
Orchestrates downloading, analyzing, and visualizing Garmin Connect data.
"""

import sys
import argparse
from pathlib import Path

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='Garmin Data Analysis App - Download, analyze, and visualize your Garmin Connect data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py all              # Run complete pipeline
  python main.py download         # Only download data
  python main.py analyze          # Only analyze data
  python main.py triathlon        # Triathlon-specific analysis
  python main.py coach            # Generate coaching brief
  python main.py visualize        # Only create visualizations
        """
    )
    
    parser.add_argument(
        'action',
        choices=['all', 'download', 'analyze', 'triathlon', 'coach', 'visualize'],
        help='Action to perform'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print(" " * 20 + "GARMIN DATA ANALYSIS APP")
    print("="*70)
    
    if args.action in ['all', 'download']:
        print("\n[1/4] DOWNLOADING DATA...")
        import download_data
        download_data.main()
        
        if args.action == 'download':
            return
    
    if args.action in ['all', 'analyze']:
        print("\n[2/4] ANALYZING DATA...")
        import analyze_data
        analyze_data.main()
        
        if args.action == 'analyze':
            return
    
    if args.action in ['all', 'triathlon']:
        print("\n[3/5] TRIATHLON TRAINING ANALYSIS...")
        import triathlon_analysis
        triathlon_analysis.main()
        
        if args.action == 'triathlon':
            return
    
    if args.action in ['all', 'coach']:
        print("\n[4/5] GENERATING COACHING BRIEF...")
        import coaching_brief
        coaching_brief.main()
        
        if args.action == 'coach':
            return
    
    if args.action in ['all', 'visualize']:
        print("\n[5/5] CREATING VISUALIZATIONS...")
        import visualize_data
        visualize_data.main()
    
    if args.action == 'all':
        print("\n" + "="*70)
        print("✓ COMPLETE PIPELINE FINISHED!")
        print("="*70)
        print("\nYour Garmin data has been:")
        print("  ✓ Downloaded from Garmin Connect")
        print("  ✓ Analyzed for statistics and trends")
        print("  ✓ Analyzed for triathlon training insights")
        print("  ✓ Generated elite coaching brief with recommendations")
        print("  ✓ Visualized with charts and graphs")
        print("\nCheck the 'data/' directory for all outputs.")


if __name__ == "__main__":
    main()
