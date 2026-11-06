# Setup, repair and updates

The client is not technical. Do every technical step yourself, and tell them only what they need to do, one small step at a time. Before the safety rules are active (the first install session), their computer may show permission boxes. Warn them once: "Your computer may ask for permission once or twice. Just click **Allow**."

## Step 0: Install (only if the helper is missing)

The normal install starts from the README of the MiraiMinds repository, when the client asks Claude to "install skill <link>". If you're here because `tt` doesn't exist:
1. Look for the link in `~/.miraiminds/task/install.json` (`source`). If there isn't one, ask: "Could you paste the link MiraiMinds sent you for setting me up?"
2. Follow the README's "For Claude: how to install this skill" steps.
3. If the installer prints `"ok": false`, go to **When setup fails**.

## Step 1: Connect

Say, in your own words:
> I'm almost ready to help with your project. I just need to connect to the MiraiMinds tracker. It takes about 2 minutes.

1. Run `tt open token`, which opens the key page in their browser. Then:
   > I've opened the tracker in your browser (log in if it asks). You'll see a page about **personal access tokens**.
   > 1. Click the button to add a new token
   > 2. Name it **Claude**, choose the longest expiry, and confirm
   > 3. Click **Copy** next to the key that appears
   >
   > Tell me when you've copied it.

   If the page doesn't open: "In the tracker, click your picture or name → **Profile settings** → **Personal access tokens**." If they still can't find it, go to **When setup fails**.
2. When they say it's copied:
   > A small box will pop up. It may be hiding behind this window. Paste your key into it with **Ctrl+V** (on a Mac, **Cmd+V**) and click **Connect**.

   Then run `tt connect` with a **10-minute timeout** (600000 ms), because it waits for them.
3. Read `reason` / `ok`:
   - `ok: true`: "Connected! Hi <first name> 👋" Then go to Step 2.
   - `cancelled`: "No problem. Tell me when you're ready and I'll open the box again."
   - `bad_key`: "That key didn't work. It may not have copied fully. Let's try once more: click **Copy** next to the key again, then tell me." On a second failure, go to **When setup fails**.
   - `no_internet`: "Your computer seems to be offline. Check your Wi-Fi, and tell me when it's back."
   - `tracker_unreachable` or `tracker_error`: use the tracker-down message in **When setup fails**.
   - `popup_unavailable`: "The pop-up box can't open on this computer, so please paste the key here instead. It's only used to connect you." Then run `tt connect --key "<key>"` and never repeat the key back.

## Step 2: Choose the project

From the `tt connect` result (or `tt project list`):
- One project: it's chosen automatically. Mention its name: "I can see your project **Shop App**."
- Several: ask which one they want to work on, with the project names as choices. Then run `tt project set "<name>"`.
- None: "Your account isn't added to a project yet." Go to **When setup fails**.

Then check the project:
- `intake_enabled: false`: new requests can't be received yet. Tell the client one small thing needs switching on by the team, and go to **When setup fails** (mention "new requests are switched off for <project>" in the message to Sagar).
- `has_testing_stage: false`: say nothing to the client. Remember there's no "ready for you to check" stage in this project.

## Step 3: Restart Claude

The tracker connection only starts when Claude starts. Use `surface` from `tt start`:
- `desktop`: "Last step: please **quit Claude completely** and open it again. On Windows, right-click the Claude icon near the clock and choose **Quit**; on a Mac, use the Claude menu → **Quit**. Then type **/task**."
- `vscode`: "Last step: please **close VS Code** and open it again, then type **/task** in the Claude panel."
- `terminal`: "Last step: type **/exit** and press Enter, then type **claude** and press Enter. Then type **/task**."
- `unknown`: ask "Where are you using me right now?" with the choices *The Claude app* / *VS Code* / *A terminal window*, then give the matching line.

If `tt connect` said `mcp_registered: false`, go to **When setup fails** instead.

## Step 4: Welcome tour (first `/task` after the restart)

1. Check the connection with one tracker call: `member me`. If it fails, go to **Repair**.
2. Say:
   > You're all set ✅ From now on, just type **/task** whenever you need something. For example:
   > - **/task** to see what's happening on your project
   > - **/task the payment page shows an error** to tell the team about a problem
   > - **/task I'd like customers to get an SMS when their order ships** to ask for something new
   >
   > You can write to me the way you'd message a colleague.
3. Then give a first-visit briefing (flows/briefing.md). It ends with `tt seen set`.

## Repair

The tracker tools aren't available, but the client is connected:
1. Run `tt repair`.
   - `changed: true`: the connection had gone missing and is now back. "The connection to the tracker didn't start this time. I've fixed it. Please restart Claude once more" (Step 3 wording), "then type **/task**."
   - `changed: false`: the connection is in place but didn't start, which can happen if the computer was slow. Ask for one restart (Step 3).
2. If the tools are still missing after that restart, go to **When setup fails**.

## Updating

If the client or MiraiMinds asks to update the skill: run the README install steps again with the `source` link from `~/.miraiminds/task/install.json`. The saved key and project are kept. Ask for a restart afterwards (Step 3).

## Removing

If the client asks to remove `/task`, check once ("Remove the project helper and its connection from this computer?"), then:
1. Run `tt uninstall`. It removes the tracker connection, the safety rules and the saved key.
2. Do what its `next` says: delete the skill folder and uninstall the connector.
3. Tell them: "Done, I've removed it. If you'd also like to switch off the key itself, you can delete it in the tracker under **Profile settings** → **Personal access tokens**."

## When setup fails

1. Run `tt doctor` to get a one-line `summary`.
2. Run `tt whatsapp --text "Hi Sagar, this is <client name> (<project, if known>). I'm setting up the MiraiMinds tracker in Claude and it isn't working. Details: <summary>"`
3. Tell the client:
   > This one needs a quick hand from the team. Please send Sagar a WhatsApp, I've written the message for you: [Send to Sagar on WhatsApp](<link>)
   > Or call **Sagar: <display number>**.

If the tracker itself can't be reached (`tt net` says `tracker: false` but `internet: true`):
> I can't reach the MiraiMinds tracker right now, so it may be down for a moment. Please let Sagar know: [Send to Sagar on WhatsApp](<link>) or call **Sagar: <display number>**. We can finish setting up as soon as it's back.
