# Streamer.bot Setup for arcade-jam

This guide walks through setting up the "Jam Roulette" channel point redemption in Streamer.bot.

## Prerequisites

- Streamer.bot installed and connected to Twitch
- OBS connected to Streamer.bot
- Pool of generated backing tracks in a local folder
- An audio source in OBS for playing the tracks

## Folder Structure

Set up your local folders:

```
C:\stream\jams\
├── ready\          # Tracks waiting to be played
│   ├── Neo_Soul_Groove_Take_1\
│   │   ├── READY_FOR_BASS.wav
│   │   └── metadata.yaml
│   ├── Boom_Bap_Classic_Take_2\
│   │   └── ...
│   └── ...
└── played\         # Used tracks (moved after playing)
```

## Step 1: Create the Channel Point Reward

1. Go to your Twitch Creator Dashboard
2. Navigate to **Viewer Rewards** → **Channel Points** → **Manage Rewards**
3. Click **Add New Custom Reward**
4. Configure:
   - **Name:** "Jam Roulette" (or your preferred name)
   - **Cost:** 500+ points (high enough to prevent spam)
   - **Require Viewer to Enter Text:** No
   - **Cooldown:** 180 seconds (3 minutes between redemptions)
   - **Limit:** 1 per stream (optional, depends on pool size)
5. Save the reward

## Step 2: Create the Streamer.bot Action

### Action: Jam Roulette

1. In Streamer.bot, go to **Actions**
2. Click **+** to create a new action
3. Name it: `Jam Roulette`

### Sub-Actions

Add these sub-actions in order:

#### 2.1: Pick Random Track (C# Code)

Add a **Execute C# Code** sub-action:

```csharp
using System;
using System.IO;
using System.Linq;

public class CPHInline
{
    public bool Execute()
    {
        string readyFolder = @"C:\stream\jams\ready";
        string playedFolder = @"C:\stream\jams\played";
        
        // Get all track folders
        var trackFolders = Directory.GetDirectories(readyFolder);
        
        if (trackFolders.Length == 0)
        {
            CPH.SetArgument("jamError", "No tracks remaining in pool!");
            CPH.SetArgument("jamFile", "");
            return true;
        }
        
        // Pick a random folder
        var random = new Random();
        int index = random.Next(trackFolders.Length);
        string selectedFolder = trackFolders[index];
        string folderName = Path.GetFileName(selectedFolder);
        
        // Find the READY_FOR_BASS.wav file
        string wavFile = Path.Combine(selectedFolder, "READY_FOR_BASS.wav");
        
        if (!File.Exists(wavFile))
        {
            CPH.SetArgument("jamError", "Track file not found!");
            CPH.SetArgument("jamFile", "");
            return true;
        }
        
        // Try to read metadata for display
        string vibeName = folderName.Replace("_", " ");
        string metadataFile = Path.Combine(selectedFolder, "metadata.yaml");
        if (File.Exists(metadataFile))
        {
            var lines = File.ReadAllLines(metadataFile);
            foreach (var line in lines)
            {
                if (line.StartsWith("name:"))
                {
                    vibeName = line.Substring(5).Trim().Trim('"');
                    break;
                }
            }
        }
        
        // Set variables for other sub-actions
        CPH.SetArgument("jamFile", wavFile);
        CPH.SetArgument("jamFolder", selectedFolder);
        CPH.SetArgument("jamVibe", vibeName);
        CPH.SetArgument("jamError", "");
        CPH.SetArgument("jamRemaining", (trackFolders.Length - 1).ToString());
        
        return true;
    }
}
```

#### 2.2: Check for Errors (If/Else)

Add an **If/Else** sub-action:
- **Variable:** `jamError`
- **Operator:** `Not Equals`
- **Value:** (empty)

If true (error exists):
- Add **Twitch Chat Message:** `@%user% Sorry, jam roulette is empty! No tracks remaining.`
- Add **Break** to stop the action

#### 2.3: Display Vibe on Screen (OBS)

Add a **OBS Set Source Text** sub-action:
- **Scene:** Your music scene
- **Source:** A text source for displaying the vibe (create one named "JamVibe")
- **Text:** `🎵 %jamVibe%`

#### 2.4: Announce in Chat

Add a **Twitch Chat Message** sub-action:
- **Message:** `🎰 JAM ROULETTE! %user% triggered: %jamVibe% — Let's go! (%jamRemaining% tracks remaining)`

#### 2.5: Play the Track

Add a **Play Sound** sub-action:
- **File Path:** `%jamFile%`
- **Audio Device:** Your OBS audio capture device or VB-Audio cable

Alternatively, use **OBS Set Source Settings** if you have a Media Source:
- **Scene:** Your music scene
- **Source:** A media source named "JamTrack"
- Set the file path to `%jamFile%`

#### 2.6: Wait for Track to Finish (Optional)

Add a **Delay** sub-action:
- **Delay:** 65000 ms (65 seconds, slightly longer than track)

#### 2.7: Move Track to Played Folder

Add another **Execute C# Code** sub-action:

```csharp
using System;
using System.IO;

public class CPHInline
{
    public bool Execute()
    {
        string sourceFolder = args["jamFolder"].ToString();
        string playedFolder = @"C:\stream\jams\played";
        
        if (string.IsNullOrEmpty(sourceFolder) || !Directory.Exists(sourceFolder))
            return true;
        
        string folderName = Path.GetFileName(sourceFolder);
        string destFolder = Path.Combine(playedFolder, folderName);
        
        try
        {
            Directory.Move(sourceFolder, destFolder);
        }
        catch (Exception ex)
        {
            CPH.LogError($"Failed to move jam folder: {ex.Message}");
        }
        
        return true;
    }
}
```

#### 2.8: Clear Display (Optional)

Add a **OBS Set Source Text** sub-action:
- **Source:** JamVibe
- **Text:** (empty, or your default text)

## Step 3: Create the Trigger

1. Go to the **Triggers** tab for this action
2. Click **+** to add a trigger
3. Select **Twitch** → **Channel Point Reward**
4. Choose your "Jam Roulette" reward

## Step 4: OBS Setup

### Create a Text Source for Vibe Display

1. In OBS, add a new **Text (GDI+)** source named `JamVibe`
2. Position it where you want the current vibe to display
3. Style it to match your overlay

### Create an Audio Source for Playback

Option A: **Media Source**
1. Add a new **Media Source** named `JamTrack`
2. Leave the file path empty (Streamer.bot will set it)
3. Enable "Close file when inactive"

Option B: **VB-Audio Cable**
1. Install VB-Audio Virtual Cable
2. Set Streamer.bot to play sounds through the cable
3. Add an Audio Input Capture in OBS for the cable

## Step 5: Test

1. Place at least one generated track folder in `C:\stream\jams\ready\`
2. Trigger the action manually in Streamer.bot
3. Verify:
   - Track plays
   - Vibe displays on screen
   - Track moves to played folder
   - Chat message appears

## Troubleshooting

**Track doesn't play:**
- Check file path in the Play Sound sub-action
- Verify audio device is correct
- Check Windows audio settings

**Text doesn't update:**
- Verify OBS is connected to Streamer.bot
- Check source name matches exactly

**Track doesn't move:**
- Check folder permissions
- Verify paths are correct in C# code

**"No tracks remaining" error:**
- Replenish your pool from the last RunPod generation
- Generate a new batch before your next music stream

## Tips

- Generate 12-24 tracks before a music stream
- Set a high point cost to manage redemption frequency
- Use the cooldown to ensure you have time to jam
- Keep the played folder so you can review what worked
- Curate your prompts.yaml based on what genres hit best
