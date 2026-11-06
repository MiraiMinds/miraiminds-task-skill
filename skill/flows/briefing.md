# Briefing: "what's happening on my project?"

Runs when the client types just `/task`, says hi, or asks for an update. The goal is a short, friendly update with **what needs the client** at the top. The client's input is what keeps the project moving.

## 1. Gather (about 10 tracker calls)

From `tt start` you already have `since`, `first_visit`, `when` and the client's `user.id`. Get the stage meanings with `tt stages`.

Then, stopping if the tracker fails (see "If the tracker can't be reached" in new-request.md):
1. `workitem list`: `{project_id, order_by: "-updated_at", per_page: 50, fields: "id,name,sequence_id,state,priority,target_date,updated_at,completed_at,created_by"}`
2. `intake list`: `{project_id, per_page: 30}` to get the client's requests and where they are in the team's review.
3. `cycle list`: `{project_id, status: "current"}`. Skip it quietly if it fails or is empty.
4. For up to 6 tasks updated since the last visit (testing-stage tasks first, then tasks being worked on), call `workitem_comment list` `{project_id, workitem_id}`. Look for **team comments newer than the last visit**, meaning comments whose author isn't the client's `user.id`. A team comment that asks the client something is a question waiting for them.

## 2. Sort into sections (skip empty ones)

1. **Needs your answer**: questions from the team that the client hasn't answered yet.
2. **Ready for you to check**: tasks in a stage with `key: testing`. Also mention any that have waited there more than 2 working days: "It's been waiting for you since Tuesday."
3. **Finished** (since the last visit): `key: finished`, with `completed_at` or `updated_at` after the last visit.
4. **Being worked on**: `key: in_progress`. Show at most 5, then "+3 more".
5. **Waiting for the team to review**: review-queue requests still pending. Also include any the team declined or marked as a duplicate since the last visit, with the team's reason in plain words.
6. **This round of work**: from the current cycle, e.g. "7 of 12 done, ends Friday". Only include it if the numbers are there.
7. **Running late**: tasks whose `target_date` has passed but which aren't finished. Say it gently, and offer to ask the team for an update (flows/status-and-changes.md → "Update request").

## 3. Write it

- Start with a greeting that fits the client's time (`client_now`): good morning, afternoon or evening. Use the `since` wording: "Here's what happened since Friday."
- **First visit:** instead of "since", give "Here's where your project stands." That means a count per plain stage plus the 3 most recent tasks.
- Rewrite technical task titles into plain words, keep the reference number in brackets, and don't change the meaning. For example, "Optimise PDP image lazy-loading" becomes "Product pages load faster (SHOP-11)". If you're unsure what a title means, keep it as it is.
- If the team is off right now (`team_status` is weekend, holiday or after hours), add one line, e.g. "The team is off for the weekend and back on Monday."
- End with "What would you like to do?" and 2 or 3 choices that fit what you found, such as *Answer the team's question*, *Check the order tracking*, or *Tell the team about something new*.
- Keep it to 15 lines or fewer. Give more detail only if they ask.

Example:
> Good morning! Here's what happened since Friday.
>
> **Needs your answer (1)**
> - The team asked about the new login page: should it also work with a Google account?
>
> **Ready for you to check (1)**
> - Order tracking for customers (SHOP-31)
>
> **Finished ✅** Coupon problem on iPhone, New banner on the home page
> **Being worked on:** Invoice download, Faster checkout
> **This round of work:** 7 of 12 done, ends Friday
>
> What would you like to do?

## 4. Finish

Run `tt seen set` so the next briefing starts from now.
