# Garmin Analyzer GUI Guide

## 🎉 New Features Added

### 1. ⚙️ Settings Dialog
Click the **Settings** button (top right) to configure:
- **Race Date** - Format: YYYY-MM-DD (e.g., 2026-06-15)
- **Race Type** - Choose: sprint, olympic, half_ironman, full_ironman
- **Race Priority** - A (main race), B (tune-up), C (training race)

This drives the periodization system and AI training plan recommendations.

### 2. 🤖 AI Coach Prompt
After clicking **Coach Brief**, a dialog will pop up with:
- Complete prompt ready to copy
- **📋 Copy to Clipboard** button - One click to copy everything
- **✅ Select All** button - Manually select all text
- The prompt includes all your training data formatted for Gemini/ChatGPT/Claude

**How to use:**
1. Click "Coach Brief" button
2. Wait for analysis to complete
3. Dialog pops up automatically
4. Click "Copy to Clipboard"
5. Open Gemini, ChatGPT, or Claude
6. Paste the prompt
7. Get your personalized 20-week training plan!

### 3. 🔍 Fullscreen Visualizations
- **Larger Window** - GUI now opens at 1400x900 (was 1200x800)
- **Fullscreen Button** - Click to view current chart in fullscreen
- **Press ESC or click** to exit fullscreen
- Perfect for analyzing details in charts

### 4. 🚀 Desktop Launcher
The app is now in your application menu!
- **Name:** Garmin Analyzer
- **Category:** Sports & Health
- **Search for:** "Garmin" in your app menu
- **Icon:** Heart rate monitor with activity waves

**To launch from menu:**
1. Open app menu (Super key)
2. Search "Garmin"
3. Click "Garmin Analyzer"

**Manual launch:** `python gui.py` from the Garmin-app directory

## 📊 Using the GUI

### Button Functions
1. **📥 Download** - Fetch latest data from Garmin Connect
2. **📊 Analyze** - Generate statistical analysis
3. **🏊🚴🏃 Triathlon** - TSS, ACWR, sport-specific metrics
4. **📋 Coach Brief** - Elite coaching brief + AI prompt dialog
5. **📈 Visualize** - Create 6 charts (auto-loads in right panel)
6. **⚡ Run All** - Complete pipeline (download → analyze → triathlon → coach → visualize)
7. **🗑️ Clear** - Clear output text

### Navigation
- **⬅ Previous / Next ➡** - Browse through visualization charts
- **🔄 Refresh** - Reload visualization list
- **🔍 Fullscreen** - View current chart fullscreen

## 🔧 Configuration Tips

### First Time Setup
1. Click **Settings** button
2. Set your race date (if you have one)
3. Choose race type and priority
4. Click **Save**

### Off-Season Training
- Leave race date blank
- System defaults to OFF_SEASON phase
- Focus: Base building, technique work

### Race Preparation
- Set race date 12-20 weeks out
- Priority A for goal race
- Run Coach Brief weekly to track progress

## 💡 AI Coach Workflow

**Weekly Routine:**
1. Download latest data (button 1)
2. Generate Coach Brief (button 4)
3. Copy AI prompt (auto-popup dialog)
4. Paste into Gemini/ChatGPT/Claude
5. Ask: "Based on this data, what should I focus on this week?"

**Monthly Planning:**
1. Update race date if changed (Settings)
2. Generate Coach Brief
3. Copy AI prompt
4. Ask: "Create a 4-week training block"

**Full Race Prep:**
1. Set race date 20 weeks out (Settings)
2. Generate Coach Brief
3. Copy AI prompt
4. Ask: "Create a complete 20-week periodized plan to my race"

## 🎯 What to Ask the AI

The prompt includes everything, so you can ask:

**Tactical (Weekly):**
- "What should I focus on this week?"
- "My ACWR is 1.3 - am I training too hard?"
- "Why is my aerobic decoupling so high?"

**Strategic (Long-term):**
- "Create a 20-week plan to my race"
- "When should I transition from base to build phase?"
- "How much volume should I add each week?"

**Sport-Specific:**
- "My swim SWOLF is 46 - how do I improve technique?"
- "How do I build bike efficiency?"
- "My run cadence is low - what drills help?"

## 🖥️ Desktop Entry

The app is installed at:
- **Desktop file:** `~/.local/share/applications/garmin-analyzer.desktop`
- **Icon:** `/home/fausto/Garmin-app/icon.png`
- **Executable:** `/home/fausto/Garmin-app/.venv/bin/python gui.py`

**To update icon:**
```bash
cd /home/fausto/Garmin-app
# Create new icon.png (256x256)
# Desktop entry automatically uses it
```

## 🐛 Troubleshooting

**Settings not saving?**
- Check `.env` file exists
- Run from terminal to see error messages

**AI prompt dialog not showing?**
- Check if `data/coaching_brief.json` was created
- Re-run Coach Brief

**Fullscreen not working?**
- Make sure visualizations exist
- Click Visualize button first

**App not in menu?**
- Desktop file: `~/.local/share/applications/garmin-analyzer.desktop`
- Try: `update-desktop-database ~/.local/share/applications`
