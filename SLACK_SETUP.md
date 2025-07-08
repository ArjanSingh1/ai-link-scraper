# Slack Setup Guide

## 🚨 Current Issue
You're getting an `invalid_auth` error because you have an **App token** (`xapp-`) instead of a **Bot User OAuth Token** (`xoxb-`).

## ✅ How to Fix This

### Step 1: Get the Correct Bot Token

1. **Go to your Slack App**: https://api.slack.com/apps
2. **Select your existing app** (or create a new one if needed)
3. **Navigate to "OAuth & Permissions"** in the left sidebar
4. **Look for "Bot User OAuth Token"** (NOT "User OAuth Token")
   - This should start with `xoxb-`
   - Copy this token to your `.env` file

### Step 2: Verify Bot Permissions

Make sure your bot has these scopes in "OAuth & Permissions" → "Bot Token Scopes":
- ✅ `channels:history` - Read messages from public channels
- ✅ `channels:read` - View basic information about public channels
- ✅ `users:read` - Get user information for display names (required for PDF generation)

### Step 3: Install/Reinstall the App

1. **Click "Install to Workspace"** (or "Reinstall to Workspace" if already installed)
2. **Authorize the permissions**
3. **Copy the new "Bot User OAuth Token"**

### Step 4: Update Your .env File

Replace your current token in `.env`:
```bash
# Replace this (App token - wrong type)
SLACK_BOT_TOKEN=xapp-1-A095AUU1JGG-...

# With this (Bot token - correct type)
SLACK_BOT_TOKEN=xoxb-1234567890-1234567890-abc123def456...
```

### Step 5: Verify Channel ID

Your channel ID `C04FLMADLRM` looks correct. To double-check:
1. **Open Slack in a web browser**
2. **Navigate to your target channel**
3. **Check the URL**: `slack.com/...channels/C04FLMADLRM`
4. **The part after `/channels/` is your channel ID**

### Step 6: Test the Connection

Run this to test your setup:
```bash
python test_setup.py
```

## 🔍 Token Types Explained

| Token Type | Starts With | Use Case | What You Need |
|------------|-------------|----------|---------------|
| **Bot User OAuth Token** | `xoxb-` | Bot interactions | ✅ **This one** |
| App-Level Token | `xapp-` | Socket Mode | ❌ Not needed |
| User OAuth Token | `xoxp-` | Acting as user | ❌ Not needed |

## 🛠️ Common Issues

### "Channel not found" error
- ✅ Make sure the bot is **added to the channel**
- ✅ Use `/invite @YourBotName` in the Slack channel

### "Missing scope" error
- ✅ Add `channels:history` and `channels:read` scopes
- ✅ Reinstall the app after adding scopes

### "Invalid auth" error
- ✅ Use Bot User OAuth Token (`xoxb-`) not App token (`xapp-`)
- ✅ Make sure token is copied correctly (no extra spaces)

## 🎯 Quick Checklist

- [ ] Using Bot User OAuth Token (starts with `xoxb-`)
- [ ] Bot has `channels:history` and `channels:read` scopes  
- [ ] App is installed to workspace
- [ ] Bot is added to target channel
- [ ] Channel ID is correct
- [ ] No typos in `.env` file

## 💡 Need Help?

If you're still having issues:
1. **Double-check your token type** - it must start with `xoxb-`
2. **Try creating a fresh Slack app** if the current one has issues
3. **Verify the bot is in the channel** by typing `/invite @YourBotName`
4. **Check Slack's API logs** in your app dashboard for detailed errors
