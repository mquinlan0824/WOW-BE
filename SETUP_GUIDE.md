# WeatherLink to WOW-BE Uploader - Setup Guide

This Python script automatically uploads your weather data from WeatherLink to the WOW-BE platform every 5 minutes, 24/7.

## Prerequisites

- **Mac mini** (or any Mac)
- **Python 3** installed (check with `python3 --version`)
- **WeatherLink Live** connected to your Davis Vantage Vue
- **WeatherLink Pro subscription** (you already have this)
- **WOW-BE account** with registered station (you already have this)

## Step 1: Get Your Credentials

### WeatherLink API Credentials

You need your WeatherLink API credentials. From your earlier screenshot, you have:

1. Log into your WeatherLink account
2. Go to **Account Information** (Settings)
3. Look for **API Token v1** and **API Key v2** section
4. You need:
   - **API Key v2**: `bvzmlbyg4pxaydig0yap8a4kdtptw42n` (from your screenshot)
   - **API Secret**: `alge5t4bhaviskirm2kesqwyxoadjhv` (from your screenshot)
   - **Station ID**: Find this in WeatherLink (usually a 6-digit number)

### WOW-BE Credentials

From your registration, you have:
- **Station ID**: `45720f67`
- **Authentication Key**: `082468`

## Step 2: Install Python Dependencies

Open Terminal and run:

```bash
pip3 install requests --break-system-packages
```

## Step 3: Configure the Launcher

Edit the `com.wowbe.uploader.plist` file:

```bash
nano ~/Projects/Davis_PWS/com.wowbe.uploader.plist
```

Replace these placeholders with your actual credentials:
- `YOUR_WEATHERLINK_API_KEY_HERE` → Your API Key v2
- `YOUR_WEATHERLINK_API_SECRET_HERE` → Your API Secret
- `YOUR_WEATHERLINK_STATION_ID_HERE` → Your WeatherLink Station ID

The file already has your WOW-BE credentials filled in.

Save with **Ctrl+O**, **Enter**, **Ctrl+X**

## Step 4: Make the Script Executable

```bash
chmod +x ~/Projects/Davis_PWS/weatherlink_to_wowbe.py
```

## Step 5: Install the Launcher

Copy the plist file to the Mac launchd directory:

```bash
cp ~/Projects/Davis_PWS/com.wowbe.uploader.plist ~/Library/LaunchAgents/
```

## Step 6: Load and Start the Service

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.wowbe.uploader.plist

# Verify it's running
launchctl list | grep wowbe
```

You should see output like:
```
-    0    com.wowbe.uploader
```

## Step 7: Test It's Working

Check the log file:

```bash
tail -f ~/Library/Logs/WOW-BE/wowbe_uploader.log
```

You should see entries like:
```
2026-05-05 10:15:30,123 - INFO - Starting WeatherLink to WOW-BE uploader
2026-05-05 10:15:30,234 - INFO - Loaded credentials for WOW-BE station: 45720f67
2026-05-05 10:15:30,345 - INFO - Fetching data from WeatherLink...
2026-05-05 10:15:31,456 - INFO - Formatting data for WOW-BE...
2026-05-05 10:15:31,567 - INFO - Sending data to WOW-BE...
2026-05-05 10:15:31,678 - INFO - Successfully sent data to WOW-BE
2026-05-05 10:15:31,789 - INFO - Upload cycle completed successfully
```

## Step 8: Verify Data on WOW-BE

1. Go to https://wow.meteo.be/
2. Log in with your account
3. Check your station dashboard
4. You should see recent observations appearing

## Troubleshooting

### Service not running
```bash
launchctl list | grep wowbe
```

If not listed, reload it:
```bash
launchctl unload ~/Library/LaunchAgents/com.wowbe.uploader.plist
launchctl load ~/Library/LaunchAgents/com.wowbe.uploader.plist
```

### Check error log
```bash
tail -f ~/Library/Logs/WOW-BE/wowbe_uploader_error.log
```

### Missing credentials error
Make sure all environment variables in the plist file are filled in correctly.

### WeatherLink API errors
- Verify your API credentials are correct
- Check your WeatherLink Station ID (not your email or account name)

### Manual test
Run the script directly:
```bash
python3 ~/Projects/Davis_PWS/weatherlink_to_wowbe.py
```

## Stopping the Service

```bash
launchctl unload ~/Library/LaunchAgents/com.wowbe.uploader.plist
```

## Restarting on Mac Restart

The plist has `RunAtLoad` set to `true`, so the service will automatically restart when your Mac boots.

## Getting Help

- WOW-BE documentation: https://wow.meteo.be/docs/api/
- WeatherLink API docs: Check your WeatherLink account settings
- Logs location: `~/Library/Logs/WOW-BE/`
