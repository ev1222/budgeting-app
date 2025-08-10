# Google API Credentials Setup

This directory should contain your Google API credentials for accessing Google Sheets.

## Required Files

1. **credentials.json** - Download from Google Cloud Console
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create or select a project
   - Enable Google Sheets API
   - Create credentials (OAuth 2.0 Client ID)
   - Download the JSON file and rename it to `credentials.json`

2. **token.json** - Generated automatically on first run
   - This file is created when you first authenticate
   - Contains your access/refresh tokens
   - Should be kept secure and not committed to version control

## Security Note

These files are ignored by git (see .gitignore) and should never be committed to version control as they contain sensitive authentication information.