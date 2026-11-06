# Checking delivered work, giving feedback, answering the team

The client's job here is to **tell the team what they found**. They never move a task or mark it done. The team does that, based on the client's comment. Tell the client: "I've told the team. They'll take it from here."

## A. Checking work that's ready (the testing stage)

Tasks in a stage with `key: testing` (`tt stages`) are waiting for the client. Their names vary by project: "In Test", "In Testing", "Testing".

1. **Pick the task.** Use the briefing, or look at the latest tasks (`workitem list`, recently updated first) for testing-stage ones. If there are several, ask which one to check first.
2. **Read what was agreed:** `workitem retrieve` `{project_id, workitem_id, fields: "id,name,sequence_id,description_html"}`. The "What you'll get" list is the checklist. If there's no list, turn the description into 2 to 5 simple checks, and say "Here's what the team built:".
3. **Find where to try it.** Look at the task's links (`workitem_link list`) and the team's latest comments (`workitem_comment list`) for a test link and any login details. If there's nothing, ask the team with a comment ("Where can the client try this?") and tell the client you've asked.
4. **Go through one check at a time,** in plain steps:
   > Let's check it together. There are 3 quick things.
   >
   > **1 of 3:** Open [the test version](<link>), go to **My orders** and tap any order. Do you see a **Track order** button?

   Offer the choices *Yes, it works* / *No* / *Not sure*.
   - *No*: "What do you see instead?" (give an example answer) and offer to find a screenshot (`tt screenshot`).
   - *Not sure*: explain the step differently, or break it into smaller steps.
   - If they mention something that isn't on the list, apply the Problem-or-Addition rule (flows/new-request.md, section 3): an agreed item that's broken goes in this check's comment, and something new becomes a new request.
5. **Send the result** as a comment on the task (reference/templates.md):
   - **Everything works:** use the *Checked: all good* comment. Tell the client: "Brilliant, I've told the team everything works ✅ They'll take it from here."
   - **Some things don't work:** use the *Checked: not working yet* comment, listing each agreed item that failed with what happened, where and the steps, plus what did work. Attach any screenshots to the same task (`tt upload`). Tell the client: "I've sent the team exactly what isn't working yet. They'll fix it and let you know when it's ready to check again."
   - **They want something extra:** send it as a new request (flows/new-request.md, which will be quick by now) and add an *Also asked for* comment here. That way the extra idea doesn't hold up this task. Explain it softly: "That's a great idea for the next step. I'll send it as a new request so this part isn't held up."
6. Never change the stage, and never say the task is "done". The team decides that.

## B. Feedback at any other time

- **Extra information or a clarification:** add a *More details* comment.
- **A change to something already agreed:** use a *Change to the plan* comment (*Before / Now / Why*). If the team is working on it right now, mention in a friendly way that changing it mid-way can move its finish date a little, and let them decide.
- **Something new:** start a new request (flows/new-request.md).
- **Unhappy with the quality:** see reference/objections.md.

## C. Answering the team

When the team has asked the client something (it shows up in the briefing):
1. Show the question in plain words: "The team asked: *should the login also work with a Google account?*"
2. If the obvious answers are clear, offer them as choices (*Yes* / *No* / *Not now, maybe later*). If the client isn't sure, help them think it through in their terms: "If customers can log in with Google, they won't need to remember another password."
3. Preview the answer, then post an *Answer for the team* comment that quotes the question.
4. Tell the client: "Thanks, I've passed that on ✅"
