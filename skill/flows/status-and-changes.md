# Status, changes and reports

## A. "Where is …?"

1. **Find the task.**
   - With a reference number: `workitem retrieve_by_identifier` `{workitem_identifier: "SHOP-42"}`.
   - Otherwise: `workitem search` plus the latest task list.
   - If two or more could match, ask: "Do you mean the *order tracking* or the *order emails*?"
   - If it's still in the review queue, `intake list` / `intake retrieve` shows where it stands (`tt stages` → `intake_status`).
2. **Gather:** the stage (in plain words), when it was last updated, the last 1 or 2 team comments, and `target_date`, only if the team set one.
3. **Answer in 3 to 5 lines:**
   > **Order tracking** (SHOP-31): the team is working on it.
   > Last update yesterday: the WhatsApp messages are finished.
   > Planned for: Friday 13 Nov.

   - With no `target_date`: "The team hasn't set a date for this yet. Want me to ask them?"
   - If it's waiting on the client (a question, or ready to check): say so kindly, and offer to do it now.
   - If nothing has changed for 3 or more **working** days: "It's been quiet for 4 working days. Want me to ask the team for an update?" If yes, post an *Update request* comment. Count working days only, so a quiet weekend doesn't count.
4. Never guess why something is late. If they ask why, offer to ask the team.

## B. Changing something that's already been sent

The client can't edit or move tasks, so every change goes to the team as a comment. That includes requests still waiting in the review queue. After posting, tell the client: "Requested ✅ The team will confirm."

- **Higher priority:** have the same friendly trade-off conversation as in flows/new-request.md section 5. Then post a *Priority request* comment, plus a *Put ahead* comment on any task that may be delayed.
- **Lower priority:** post a *Priority request* comment.
- **A date it's needed by:** post a *Date request* comment. It's a wish, and the team confirms it.
- **Change what was agreed:** post a *Change to the plan* comment (*Before / Now / Why*). If the team is working on it right now, mention first, in a friendly way, that it may move the finish date a little.
- **Stop it:** check once ("Just to check: stop work on *order tracking*? Anything already built for it may be put aside."), then post a *Request to stop* comment.
- **"Delete it":** "I can't delete things, but I can ask the team to stop it. That way the history is kept in case you need it later." Then treat it as *Stop it*.
- **"Give it to someone else", "put it in this week's work" or "mark it done":** "That's the team's call. I'll pass on your wish with your reason." Then post a comment.

## C. Reports

For example: "what did we get in October?", "what's in progress?", "what's waiting on whom?"

1. Get the data:
   - `workitem list` `{project_id, order_by: "-updated_at", per_page: 50, fields: "id,name,sequence_id,state,priority,target_date,updated_at,completed_at"}`.
   - Follow the `next_cursor` for at most 3 pages, and stop as soon as `updated_at` is older than the start of the period.
   - "Delivered" means a finished stage with `completed_at` inside the period.
2. **Problems fixed vs. additions requested** (only if they ask about quality or "how many bugs"):
   - Read the descriptions of the period's tasks (at most 15 `workitem retrieve` calls) and count the `Request type:` line in their footers.
   - If there are too many to read, leave this line out and don't guess.
3. Write it plainly, so it's ready to paste into an email:
   > **Your project in October**
   >
   > **Finished (8):** Order tracking, Invoice download, Coupon fix on iPhone, …
   > **Being worked on (3):** Faster checkout, …
   > **Waiting for you (1):** Check the new login page
   > **Requests in October:** 2 problems fixed, 6 new additions
4. Offer: "Want me to make it shorter, or add more detail on any part?"
