# Request and comment templates

Everything written to the tracker is clear, professional English for the MiraiMinds team, even when the client wrote in another language. Fill in only the sections you have, and leave out empty ones. Escape the client's text in HTML. Never include IDs other than reference numbers, and never @mention anyone.

The footer line is how the team, and later reports, can tell requests apart. Always include it exactly as shown, with today's date as `Tue 3 Nov 2026`.

## Titles

`<Where>: <what>`, 70 characters or fewer, and matching the description. For example:
- `Checkout: coupon code rejected on iPhone`
- `Orders: customers can track their order`
- `URGENT: payments failing for all customers`

## New feature / Addition

```html
<h3>Summary</h3>
<p>One or two sentences: what the client wants and why.</p>
<h3>Why</h3>
<p>The business goal, in the client's terms.</p>
<h3>Who uses it</h3>
<p>Customers / the client's staff / the client.</p>
<h3>How it should work</h3>
<ol><li>Step by step, as the client walked through it.</li></ol>
<h3>What you'll get</h3>
<ul><li>Each item can be checked with a yes or a no.</li></ul>
<h3>Not in this first version</h3>
<ul><li>What the client agreed to leave for later.</li></ul>
<h3>Situations discussed</h3>
<ul><li>If the customer cancels halfway: …</li></ul>
<h3>References</h3>
<ul><li>Apps, screenshots or links the client gave.</li></ul>
<h3>Builds on</h3>
<p>Additions only: SHOP-31. This was not part of that task's agreed list.</p>
<h3>Priority note</h3>
<p>Needed by Fri 20 Nov (client's wish, launch event). Client chose to put this ahead of SHOP-52, knowing it may be delayed.</p>
<h3>Related</h3>
<p>SHOP-44: client confirmed this request replaces its "optional coupon box" behaviour.</p>
<p><em>Agreed with {client name} on {date} via /task. Request type: {New feature | Addition}</em></p>
```

"What you'll get" and "Not in this first version" are the agreement. Use these exact headings, because later checks look for them.

## Change

Same as a new feature, plus this before *What you'll get*:

```html
<h3>Before / Now</h3>
<p><strong>Before:</strong> how it works today.</p>
<p><strong>Now:</strong> how it should work.</p>
```

Footer: `Request type: Change`

## Problem

```html
<h3>Summary</h3>
<p>What's wrong, in one sentence.</p>
<h3>What was agreed</h3>
<p>SHOP-31, agreed item: "A Track order button on every order".</p>
<p>(Or: "No agreed list found. Team: please check whether this was part of the original plan.")</p>
<h3>What happens</h3>
<p>…</p>
<h3>What should happen</h3>
<p>…</p>
<h3>Where</h3>
<p>Phone (iPhone), app, checkout page.</p>
<h3>Steps (what the client did just before)</h3>
<ol><li>…</li></ol>
<h3>How often / who is affected</h3>
<p>Every time; all customers on iPhone.</p>
<h3>Screenshots</h3>
<p>Attached.</p>
<p><em>Reported by {client name} on {date} via /task. Request type: Problem</em></p>
```

## Question

```html
<h3>Question</h3>
<p>…</p>
<h3>Why it matters</h3>
<p>What decision or work it's holding up.</p>
<p><em>Asked by {client name} on {date} via /task. Request type: Question</em></p>
```

## Comments

**Checked: all good**
```html
<p>✅ <strong>Checked by {client name}</strong> on {date}. Everything works as agreed.</p>
<ul><li>✔ A Track order button on every order</li><li>✔ …</li></ul>
```

**Checked: not working yet**
```html
<p><strong>Checked by {client name}</strong> on {date}. Not working yet:</p>
<ol><li><strong>{agreed item}</strong>: what happened: …; where: …; steps: …</li></ol>
<p>Working fine: {items}.</p>
```

**Also asked for** (on the task being checked)
```html
<p>{client name} also asked for: {short description}. Sent as a new request ({ref}) so it doesn't hold up this one.</p>
```

**More details**
```html
<p><strong>More details from {client name}</strong> ({date})</p>
<p>…</p>
```

**Answer for the team**
```html
<p><strong>Answer from {client name}</strong> to: "{the team's question, short}"</p>
<p>…</p>
```

**Change to the plan**
```html
<p><strong>Change to the plan</strong> ({client name}, {date})</p>
<p><strong>Before:</strong> …</p>
<p><strong>Now:</strong> …</p>
<p><strong>Why:</strong> …</p>
```

**Priority request**
```html
<p><strong>Priority request</strong> from {client name} ({date}): please treat this as {urgent | high | medium | low}. Reason: … The client knows this may delay: {refs}.</p>
```

**Put ahead** (on the task that may be delayed)
```html
<p>Note from {client name} ({date}): {new ref} was put ahead of this task. The client knows this one may come a little later.</p>
```

**Date request**
```html
<p><strong>Date request</strong> from {client name} ({date}): needed by {date} because … Please confirm if that's possible.</p>
```

**Request to stop**
```html
<p><strong>Request to stop</strong> from {client name} ({date}): please stop work on this. Reason: …</p>
```

**Update request**
```html
<p><strong>Update request</strong> from {client name} ({date}): could you share where this stands and when it's expected?</p>
```
