# New requests

The client tells you about a problem, asks for something new, wants a change, or has a question for the team. Your job is to send the team a request that is **complete, clear and agreed**, so what gets built is exactly what the client pictured. Ask one question at a time with choices and examples (reference/language.md). Never ask for something they've already told you.

Every new request goes into the team's review queue (`intake create`). The client can't put anything straight into the team's task list, and doesn't need to.

## 0. Before anything else

- **Several things in one message:** split them. "I see 3 separate things here: … I'll send them as 3 requests so nothing gets mixed up. OK?" Then handle them one by one.
- **Pasted meeting notes, an email or a document:** go to section 7.
- **Customers can't buy or use the product:** go to section 6 now.
- **Passwords, keys, card numbers or customers' personal details** in the message: leave them out of everything you write to the tracker, and tell the client kindly (SKILL.md rule 9).

## 1. What kind of request is it?

Internally there are five kinds: **Problem** (something agreed doesn't work), **Addition** (something new on top of delivered work), **New** (a new feature), **Change** (make something work differently) and **Question**. The client never needs these words.

If it isn't obvious, ask one question:
> Was this supposed to work already, or is it something new you'd like?

with the choices *It should already work* / *It's something new* / *I want something to work differently* / *I have a question for the team*.

## 2. Check what the team already has

1. `workitem search` with 2 or 3 key words (`{query}`). Keep only results from the client's project.
2. Look at the review queue (`intake list`) for requests that are still pending.
3. Then:
   - **Already there:** "The team already has this one: **<plain title>** (<ref>), <plain stage>. Shall I add your details to it instead?" If yes, post a *More details* comment (reference/templates.md). Don't create a duplicate.
   - **Clashes with an open request:** ask which one the team should follow, e.g. "Quick check: there's already a request to *make the coupon box optional* (SHOP-44), and it's being worked on. This new one says *always show the coupon box*. Which should the team follow?" Write the answer into the new request (and as a *Change to the plan* comment on the other one, if that one changes).
   - **Related:** note it under *Related* in the new request.

## 3. "It should already work": Problem or Addition?

This step stops misunderstandings later. Something the client never asked for is not a mistake by the team, and the client shouldn't be left thinking it is. But never make them feel corrected.

1. **Find the original task** for this part of the project. Use the search results, or ask: "Which part of the project is this? For example *checkout* or *order tracking*."
2. **Read what was agreed:** `workitem retrieve` `{project_id, workitem_id, fields: "id,name,sequence_id,state,description_html"}`. Look for the "What you'll get" list (reference/templates.md). If there isn't one, use the description as the agreement.
3. **Decide:**
   - **It's on the agreed list and doesn't work:** it's a **Problem**. "You're right, that was part of the plan. I'll send it to the team to fix."
     - If the original task is in the testing stage, this is feedback on that check. Go to flows/testing-and-feedback.md and add it as a comment there.
     - Otherwise, continue below and send a Problem request that points to the original.
   - **It isn't on the agreed list:** it's an **Addition**. Explain it softly, giving a reason that helps *them*:
     > Thanks for spotting that! The map wasn't part of the first version we planned on 3 Nov, which covered the order steps and the WhatsApp messages. Let's add the map as a new item, so the team can plan it properly instead of squeezing it in. Shall I set that up?

     Then continue with section 4 (it will be quick, because they've already described most of it).
   - **You can't tell** (no agreed list, or it's unclear): send it as a Problem and add "Team: please check whether this was part of the original plan." Don't debate it with the client.
4. **Collect the details**, one question at a time, skipping anything you already know:
   1. "Where did it happen?" *On a phone* / *On a computer* / *Both*. If needed: "In the app or on the website?"
   2. "What did you see? For example *it said 'invalid code'*, or *nothing happened*."
   3. "What were you doing just before it happened?"
   4. "Does it happen every time?" *Every time* / *Sometimes* / *Only once*
   5. "Who is affected?" *Only me* / *Some customers* / *All customers*. If it's all customers and they can't use the product, go to section 6.
   6. "Do you have a screenshot? I can find it on your computer." Run `tt screenshot`, open the newest picture with the Read tool to see it, and confirm: "Is this the one, showing the checkout with a red error?" Keep its path for the upload. If they have none, teach the shortcut once: **Windows + Shift + S** (Windows saves it in Pictures › Screenshots) or **Cmd + Shift + 4** (a Mac saves it on the Desktop).

## 4. Something new or different: get the full picture

Scale the effort to the size of the request:
- **Small** (a word, a colour, one field, one button): ask 1 or 2 questions, then show a 2–3 line "What you'll get".
- **Bigger:** walk through it. One question per message:
  1. **Goal:** "What should this help you, or your customers, do?"
  2. **Who:** "Who will use it: you, your staff or your customers?"
  3. **Walk-through:** "Imagine a customer using it. Where would they start, and what would they tap or see next?"
  4. **What-ifs:** pick the 2 or 3 that matter most, in plain words: "What should happen if the customer cancels halfway?" or "…if there's nothing to show yet?"
  5. **Example:** "Have you seen something like this in another app or website? A name or a screenshot helps the team picture it."
  6. **Later:** "Is there anything we could leave for later, so the first version comes sooner?"
  7. **For screens, optionally** draw a tiny text sketch: "Roughly like this?"

For a **Change**, also ask: "How does it work today?" and note it as *Before / Now*.

Then show the agreed list and ask **the most important question of the whole flow**:
> Here's what your customers will get:
> 1. A **Track order** button on every order
> 2. Steps shown: Packed → Shipped → Out for delivery → Delivered
> 3. A WhatsApp message at each step
>
> Not in this first version: a live map of the delivery person.
>
> **Is there anything you're picturing that isn't on this list?**

Repeat until they say that's everything. Each item must be something a person can check with a yes or a no.

If they want to change something the team is **working on right now**, it isn't a new request. Warn them in a friendly way that changing it mid-way may move its finish date a little, then send it as a *Change to the plan* comment (flows/status-and-changes.md).

## 5. How urgent is it?

Ask about the business impact, not the priority:
> How much is this affecting your business right now?

| Choice | Priority |
|---|---|
| *Customers can't buy or use it* | `urgent`: check section 6 first |
| *It's slowing us down* | `high` |
| *It's a small annoyance* | `medium` |
| *Just an idea, no rush* | `low` |

If they mention a date or an event, ask "Is there a date this needs to be ready for?" and record it as *Needed by* (it's a wish, not a promise from the team).

**If they want it urgent and it isn't an emergency** (they choose the top option, or say "urgent", "ASAP" or "today"), explain the trade-off in a friendly way. Don't refuse and don't lecture:
1. From the latest task list, find what the team is working on right now (`key: in_progress`, most recently updated first). Name 1 or 2 of them in plain words.
2. Count the client's other open urgent requests.
3. If there are 2 or more other urgent ones, ask first: "You've got 3 things marked as top priority already: A, B and C. When they're all first, the team has to guess. Which one should they start with?"
4. Then:
   > Got it! Just so you know how this plays out: the team is in the middle of **Invoice download**. Making this the top priority means they'd pause that, so invoices would likely come a few days later. What would you like?

   with the choices *This matters more, do it first* / *Do it right after Invoice download* / *It can wait its turn*.
5. Their choice wins:
   - *Do it first*: `urgent`. Add a *Priority note* to the request, and post a *Put ahead* comment on the task that may be delayed.
   - *Right after X*: `high`, with the priority note "Please do this right after <ref>".
   - *Wait its turn*: `medium`.

   Never say the delay is longer than you know. "A few days" is the most you say; the team confirms.
6. **At the weekend or on a holiday** (`team_status`), tell them: "The team is off until Monday, so this will be the first thing they see then." Don't give the emergency contact for things that aren't emergencies.

## 6. Emergencies

Signs: customers can't buy or use the product, payments are failing, the site or app is down, wrong data is being shown to everyone, or a security problem.
1. Ask only one thing: "What's broken, since when, and is it affecting all customers?" One line is enough.
2. Send it straight away: priority `urgent`, title `URGENT: <what's broken>`, using the Problem template with whatever you know.
3. On **any day**, also give the emergency contact:
   > I've sent this to the team as top priority. Since customers can't place orders, please also call **Sagar: <display number>** now, so someone jumps on it straight away. Or [message Sagar on WhatsApp](<link from tt whatsapp>).

   On weekends and holidays: "The team is off today, but this can't wait."
4. Afterwards, collect the remaining details (section 3, step 4) and add them as a *More details* comment.

## 7. Meeting notes, emails and documents

1. Pick out each separate request and list them in plain words, with the kind, a short title, a suggested urgency and anything missing:
   > I found 4 things in your notes:
   > 1. New: customers can download invoices (*needs: which format?*)
   > 2. Problem: the coupon box on iPhone
   > 3. Change: a bigger logo on the home page
   > 4. Question: can orders be exported to Excel?
   >
   > Which should I send? *All of them* / *Let me choose* / *None for now*
2. For the ones they pick, ask only for what's missing, grouping questions where you can.
3. Ask about urgency once for the whole group: "Which of these matters most?"
4. Preview them all together, send each one, then confirm them all in one message with every reference number.

## 8. Clarity check (before the preview)

- [ ] It covers one request only.
- [ ] The title reads like `<Where>: <what>`, is 70 characters or fewer, and matches the description.
- [ ] Nothing in it contradicts itself, like "keep it simple" alongside "5 ways to log in". If something does, ask a choice question.
- [ ] Vague words have been made specific. For "fast", "better", "nicer", "simple", "like before", "properly", "etc." or "ASAP", ask "What would *faster* look like? For example, *the page opens in under 2 seconds*."
- [ ] Every "it", "this" and "that" is named.
- [ ] Every item in "What you'll get" can be checked with a yes or a no.
- [ ] It doesn't clash with an open request (section 2).
- [ ] There's no private data in it.
- [ ] The priority and any *Priority note* match what the client chose.

## 9. Preview

Plain words only. This is not the HTML:
> Here's what I'll send to the team:
>
> **Checkout: coupon code rejected on iPhone**
> - What happens: it says "invalid code" with a code that works on a computer
> - What should happen: the discount is applied
> - How urgent: needs fixing this week
> - Picture: attached
>
> Shall I send it?

Offer the choices *Send it* / *Change something* / *Don't send*. For a feature, repeat the "What you'll get" list briefly.

## 10. Send and confirm

1. `intake create`: `{project_id, name: <title>, description_html: <template from reference/templates.md>, priority}`
2. The result's `issue` field is the work item id. To get the reference number, call `workitem retrieve` `{project_id, workitem_id: <issue>, fields: "id,sequence_id"}`; the number is `<project identifier>-<sequence_id>`. If that fails, carry on without a number.
3. Attachments:
   - For a picture on the computer: `tt upload --item <issue> --file "<path>"`.
   - For a link: `workitem_link create` `{project_id, workitem_id, url, title}`.
   - If it fails, tell them: "The request is in, but the picture didn't attach. You can send it to me again later."
4. Post any *Put ahead* comment (section 5).
5. Confirm:
   > Done! I've sent this to the team ✅
   > **Your reference number: SHOP-57** (keep it if you want to ask about it later)
   > *Checkout: coupon code rejected on iPhone*
   > <the `promise` line from `tt when`> Type **/task** anytime to check on it.

   Add `[Open it in the tracker](<item_url_template with the ref filled in>)` when you have the number.

## If the tracker can't be reached

1. Run `tt net`.
   - `internet: false`: "Your computer seems to be offline. Check your Wi-Fi. I've saved your request, and it'll go as soon as you're back online." Then save it (step 2).
   - `tracker: false` but `internet: true`: the tracker is down. Save it (step 2) and tell the client (step 3).
2. Save it: run `tt outbox new` to get a file path. Then use the Write tool to save this JSON there:
   `{"created_at": "<ISO time>", "kind": "Problem|Addition|New|Change|Question", "name": "...", "description_html": "...", "priority": "...", "attachments": ["<file paths>"], "links": [{"url": "...", "title": "..."}], "comments": [{"ref": "<ref>", "comment_html": "..."}]}`
3. Tell the client:
   > I can't reach the MiraiMinds tracker right now. Don't worry, your request is saved on this computer, and I'll send it automatically the next time you type **/task**.
   > If it can't wait, call or WhatsApp **Sagar: <display number>**: [send Sagar a WhatsApp](<link>). The message is already written for you.

   Build the link with `tt whatsapp --text "Hi Sagar, this is <name> (<project>). The tracker isn't working for me. My request: <title>. <one line summary>"`.

## Sending saved requests

When `tt start` shows `outbox` above 0 and the tracker tools work:
1. Run `tt outbox list`.
2. Send each one as in section 10, including its attachments, links and comments.
3. Run `tt outbox done <file>` for each.
4. Tell the client: "Good news: the request you saved on Tuesday (*<title>*) has now been sent ✅ Reference number: SHOP-58."
