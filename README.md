# MiraiMinds `/task`

Your project helper inside Claude, connected to the MiraiMinds tracker.

Type `/task` and, in plain words, you can:

- see what's happening on your project: what's waiting for you, what's finished, what's being worked on
- tell the team about a problem, or ask for something new, and agree exactly what you'll get before it's sent
- check work that's ready, and send the team your feedback
- ask where a request is, change its priority or date, or get a short report

It knows the team's working days, keeps your requests safe if the tracker is ever down, and always sends the team clear, complete requests.

## Install

Open Claude: the **Code** tab of the Claude desktop app, the Claude panel in VS Code, or Claude in a terminal. Then type:

```
install skill <link to this page>
```

Claude sets everything up and guides you through it. It takes about 3 minutes and needs one restart of Claude. Your computer may ask for permission once or twice; click **Allow**.

After that, just type **/task** whenever you need something. For example:

- `/task`
- `/task the payment page shows an error`
- `/task I'd like customers to get an SMS when their order ships`

## Need help?

If setup doesn't work, the tracker is down, or something is urgent (customers can't use your product), contact **Sagar: +91 63537 64284** (call or WhatsApp).

## Privacy and safety

- `/task` works only with **your own project** in the MiraiMinds tracker.
- It can **add** requests and comments. It can't delete, move or reassign anything; the MiraiMinds team does that.
- Your connection key is saved only on your computer, in your user folder, and is never shown in the chat. You can switch it off anytime in the tracker under **Profile settings → Personal access tokens**.
- Private details such as passwords, card numbers or your customers' personal data are kept out of the tracker.

## What gets installed

| Where | What |
|---|---|
| `~/.claude/skills/task/` | The `/task` skill |
| `uv` (in `~/.local/bin`, only if missing) | A small tool that installs Python and the tracker connector, without admin rights |
| `plane-mcp-server` | The official open-source connector for the tracker (MIT licence) |
| `~/.claude.json` | The tracker connection (it contains no key) |
| `~/.claude/settings.json` | Safety rules for `/task`, and a longer start-up time for the tracker connection |
| `~/.miraiminds/task/` | Your connection key, your project choice, and any requests saved while the tracker was down |

Before changing `~/.claude.json` or `~/.claude/settings.json` for the first time, the installer keeps a backup next to them (`*.miraiminds-backup`).

To update, type `update /task` in Claude. To remove it, type `remove /task`.

---

## For Claude: installing, updating and removing

The user is probably **not technical**. Before each step, explain in one short, plain sentence what you're doing (no jargon), and tell them their computer may ask for permission and they should click **Allow**. This needs Claude Code (CLI, desktop app or VS Code extension) with shell access. Nothing needs admin rights.

### Install or update

1. **Download this repository** into a new, empty temporary folder, using the repository link the user gave you. For an update, use the `source` link in `~/.miraiminds/task/install.json`.
   - If `git` is available: `git clone --depth 1 <repo-url> "<temp folder>/miraiminds-task"`
   - Otherwise: download `<repo-url>/archive/refs/heads/main.zip` and extract it.
2. **Run the installer** from that folder, with a **10-minute timeout**:
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File "<folder>\install.ps1" -Source "<repo-url>"`
   - macOS / Linux: `bash "<folder>/install.sh" "<repo-url>"`

   It's safe to run again. The last thing it prints is a JSON summary.
3. **If it printed `"ok": true`:** read `~/.claude/skills/task/SKILL.md`, then `~/.claude/skills/task/flows/setup.md`.
   - For a new install, continue with the user from **"Step 1: Connect"**.
   - For an update (`already_connected: true`), ask for one restart (**"Step 3: Restart Claude"**).
4. **If it failed:** tell the user in plain words that one part didn't install, and give them the emergency contact from the output (`emergency`) to sort it out. Don't try workarounds that change system settings.

### Remove

Follow **"Removing"** in `~/.claude/skills/task/flows/setup.md`. In short: run `bash ~/.claude/skills/task/bin/tt uninstall`, then do what its `next` says.
