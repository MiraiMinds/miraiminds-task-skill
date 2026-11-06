# Using the tracker

The tracker is a self-hosted **Plane Community Edition** at `tracker_url`. Its tools are named `mcp__miraiminds-tracker__<tool>`, and each takes an `action`. A safety hook allows only the actions below, and only on the client's own project. Anything else is refused, so don't try it.

Always pass `project_id` = `project.id` from `tt start` (the UUID, not the name). The helper's `tt stages` turns stage ids into plain meanings.

## What this edition can't do

- **No PQL / `pql` filters.** They fail on this edition. List tasks sorted by `-updated_at` and filter the results yourself.
- No work item types, epics, custom properties, templates, releases, customers, initiatives, workspace pages or project feature flags (they return 404).
- The MCP can't upload a file from the computer, only from a public URL. For local files, use `tt upload`.

## Allowed actions

| Tool | Actions |
|---|---|
| `member` | `me`, `list_project` |
| `project` | `retrieve` (the client's own project; to switch projects use `tt project list` / `tt project set`) |
| `workitem` | `list`, `retrieve`, `retrieve_by_identifier`, `search` |
| `intake` | `create`, `list`, `retrieve` |
| `workitem_comment` | `list`, `retrieve`, `create` |
| `workitem_link` | `list`, `create` |
| `workitem_attachment` | `list`, `read`, `download_url`, `upload_from_url` |
| `workitem_activity` | `list`, `retrieve` |
| `workitem_relation` | `list` |
| `state`, `label` | `list` |
| `cycle`, `module`, `milestone` | `list`, `retrieve`, `list_workitems` |
| `page` | `list`, `retrieve` (project pages only) |

## Recipes

**Latest tasks** (briefings, finding things, reports)
`workitem list` `{project_id, order_by: "-updated_at", per_page: 50, fields: "id,name,sequence_id,state,priority,target_date,updated_at,completed_at,created_by"}`
The reference number is `<project.identifier>-<sequence_id>`. For more, follow `next_cursor`, at most 3 pages.

**One task by reference number**
`workitem retrieve_by_identifier` `{workitem_identifier: "SHOP-42", fields: "id,name,sequence_id,state,priority,target_date,description_html"}`

**One task by id, with what was agreed**
`workitem retrieve` `{project_id, workitem_id, fields: "id,name,sequence_id,state,description_html"}`

**Search by words**
`workitem search` `{query: "coupon iphone"}`. This searches every project the client can open, so keep only results whose `project_id` is theirs.

**New request** (the only way to add work)
`intake create` `{project_id, name, description_html, priority}`. `priority` is one of `urgent`, `high`, `medium`, `low`, `none`. The result's `issue` field is the new work item's id; use it for comments, links and uploads.

**Requests waiting for review**
`intake list` `{project_id, per_page: 30}`. Each record's `status` is explained in `tt stages` → `intake_status` (-2 reviewing, -1 declined, 0 parked, 1 accepted, 2 duplicate). The work item id is the record's `issue` field.

**Comment**
`workitem_comment create` `{project_id, workitem_id, comment_html}`
- Use HTML, and escape the client's text (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`).
- No @mentions.
- Author check: a comment by the client has `created_by` (or `actor`) equal to `user.id` from `tt start`. Every other comment is from the team.

**Link**
`workitem_link create` `{project_id, workitem_id, url, title}`. The URL must start with `http://` or `https://`.

**Picture or file from the computer**
`tt upload --item <workitem_id> --file "<path>"`. The limit is 5 MB.

**Current round of work**
`cycle list` `{project_id, status: "current"}`. It's fine if this is empty.

**Stage meanings**
`tt stages` lists `key`: `not_started`, `planned`, `in_progress`, `testing` (ready for the client to check), `on_hold`, `finished`, `stopped`. Each also has a `plain` phrase for the client.

## Links for the client

`item_url_template` from `tt start`, with `{ref}` filled in, e.g. `https://tracker.miraiminds.co/workspace---miraiminds/browse/SHOP-42/`.

## When something fails

| Result | What it means / what to do |
|---|---|
| Connection error or timeout | Run `tt net`. Is the tracker down or their internet off? Use flows/new-request.md → "If the tracker can't be reached". |
| `403` / "permission" | The client's account can't do that. Tell them kindly that only the team can, and offer a comment instead. |
| `404` | It doesn't exist or isn't available on this edition. Try another way, or skip it quietly. |
| `429` / "rate" | Too many calls. Wait a moment, then make fewer calls. |
| Blocked by the safety hook | Follow the reason it gives (usually: use the right `project_id`, or send a comment instead). |
| The tools are missing | flows/setup.md → Repair |

Never show any of these to the client. Say it in plain words (reference/language.md).
