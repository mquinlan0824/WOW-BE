# WeatherLink to WOW-BE Uploader - VS Code Virtual Environment Setup

This guide walks you through setting up and running the WOW-BE uploader in VS Code using a Python virtual environment.

## Prerequisites

- **VS Code** installed
- **Python 3.8+** installed on your Mac (check with `python3 --version`)
- **WeatherLink Live** connected to your Davis Vantage Vue
- Your credentials ready

## Step 1: Open the Project in VS Code

```bash
cd ~/Projects/Davis_PWS
code .
```

This opens the project folder in VS Code.

## Step 2: Create a Virtual Environment

In VS Code, open the **Terminal** (Ctrl+` or View → Terminal).

Create the virtual environment:

```bash
python3 -m venv davis_env
```

This creates a `davis_env/` folder with an isolated Python environment.

## Step 3: Activate the Virtual Environment

```bash
source davis_env/bin/activate
```

You should see `(davis_env)` at the start of your terminal prompt. This means the virtual environment is active.

## Step 4: Select the Virtual Environment in VS Code

1. Press **Cmd+Shift+P** (Command Palette)
2. Type "Python: Select Interpreter"
3. Choose the one that says `./davis_env/bin/python`

This tells VS Code to use your virtual environment.

## Step 5: Install Dependencies

With the virtual environment activated, run:

```bash
pip install -r requirements.txt
```

This installs `requests` and `python-dotenv` in your virtual environment.

## Step 6: Set Up Your Credentials

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and verify your credentials are correct:
   ```bash
   nano .env
   ```

   You should see:
   ```
   WEATHERLINK_API_KEY=your_api_key_here
   WEATHERLINK_API_SECRET=your_api_secret_here
   WEATHERLINK_STATION_ID=001D0AC026B4
   WOWBE_STATION_ID=your_wowbe_station_id
   WOWBE_AUTH_KEY=your_wowbe_auth_key
   ```

   Save with **Ctrl+O**, **Enter**, **Ctrl+X**

3. **IMPORTANT**: `.env` is in `.gitignore` so your credentials never get committed to git.

## Step 7: Test the Script

Run the script manually to test it works:

```bash
python weatherlink_to_wowbe.py
```

You should see output like:
```
2026-05-05 10:15:30,123 - INFO - Starting WeatherLink to WOW-BE uploader
2026-05-05 10:15:30,234 - INFO - Loaded credentials for WOW-BE station: your_wowbe_station_id
2026-05-05 10:15:30,345 - INFO - Fetching data from WeatherLink...
2026-05-05 10:15:31,456 - INFO - Formatting data for WOW-BE...
2026-05-05 10:15:31,567 - INFO - Sending data to WOW-BE...
2026-05-05 10:15:31,678 - INFO - Successfully sent data to WOW-BE
2026-05-05 10:15:31,789 - INFO - Upload cycle completed successfully
```

Check the log file:
```bash
tail -f ~/Library/Logs/WOW-BE/wowbe_uploader.log
```

## Step 8: Schedule It to Run Every 5 Minutes

You have two options:

### Option A: Run in Terminal (Simple Testing)

In VS Code terminal, run:
```bash
while true; do python weatherlink_to_wowbe.py; sleep 300; done
```

This runs the script every 5 minutes (300 seconds). Keep this terminal open.

### Option B: Use a Launch Configuration (Recommended)

Create a `.vscode/launch.json` file to run from VS Code:

1. In VS Code, go to **Run** → **Add Configuration**
2. Select **Python**
3. Replace the content with:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "WOW-BE Uploader",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/weatherlink_to_wowbe.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "PYTHONUNBUFFERED": "1"
            }
        }
    ]
}
```

Then press **F5** to run the script with debugging.

### Option C: Schedule with Mac's launchd (For 24/7 Operation)

If you want it to run automatically in the background 24/7:

1. Create a launch script:
   ```bash
   cat > ~/Projects/Davis_PWS/run_uploader.sh << 'EOF'
   #!/bin/bash
   cd ~/Projects/Davis_PWS
   source davis_env/bin/activate
   while true; do
       python weatherlink_to_wowbe.py
       sleep 300
   done
   EOF
   ```

2. Make it executable:
   ```bash
   chmod +x ~/Projects/Davis_PWS/run_uploader.sh
   ```

3. Create a launchd plist:
   ```bash
   cat > ~/Library/LaunchAgents/com.wowbe.uploader.venv.plist << 'EOF'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.wowbe.uploader</string>
       <key>ProgramArguments</key>
       <array>
           <string>/bin/bash</string>
           <string>/Users/michael-work/Projects/Davis_PWS/run_uploader.sh</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/Users/michael-work/Library/Logs/WOW-BE/wowbe_uploader.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/michael-work/Library/Logs/WOW-BE/wowbe_uploader_error.log</string>
   </dict>
   </plist>
   EOF
   ```

4. Load it:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.wowbe.uploader.venv.plist
   ```

## Verify Data on WOW-BE

1. Go to https://wow.meteo.be/
2. Log in with your account
3. Check your station dashboard
4. You should see recent observations

## Troubleshooting

### Virtual environment not activating
```bash
source venv/bin/activate
```

### Python can't find requests
Make sure you've run `pip install -r requirements.txt` while the venv is active.

### Can't find .env file
Make sure `.env` is in the same folder as the script (not in a subfolder).

### Deactivate virtual environment
```bash
deactivate
```

## Development Tips

- Edit `weatherlink_to_wowbe.py` directly in VS Code
- Use VS Code's debugger (F5) to step through code
- Check logs in VS Code terminal
- Make changes and re-run with F5

## Next Steps

Once you confirm it's working:
- Consider Option C to run it 24/7 on your Mac mini
- Or keep VS Code running with the script looping
