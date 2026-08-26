# FM Media — Daily Substack Draft Pipeline

Every morning (11:00 UTC by default), this runs in GitHub Actions, writes a post
in the FM voice, and pushes it into your Substack as a **draft**. It never
publishes anything — you open the app, review, edit if needed, and tap publish
yourself, same as today.

## One-time setup (15 minutes)

### 1. Create a private GitHub repo
Push these files to it. **Must be private** — the workflow file itself is fine
to be public, but keep it private anyway since it's tied to your publication.

### 2. Get your Substack session cookie
This is the only slightly fiddly part, and you only do it once (cookies are
long-lived, but redo this if the pipeline ever starts failing with an auth error):

1. Log into Substack in your browser as normal.
2. Open DevTools (F12 or right-click → Inspect) → **Network** tab.
3. Refresh the page, click any request to `substack.com`.
4. In the request headers, find `Cookie:` and copy the *entire* value —
   it'll look like `substack.sid=abc123; substack.lli=1; ...`.
5. That whole string is your `SUBSTACK_COOKIES` secret.

### 3. Add repo secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Add all three:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from console.anthropic.com |
| `SUBSTACK_COOKIES` | The cookie string from step 2 |
| `SUBSTACK_PUBLICATION_URL` | e.g. `https://thefinalmindset.substack.com` |

### 4. Test it
Go to the **Actions** tab → "Daily Substack Draft" → **Run workflow** (this is
the `workflow_dispatch` trigger — lets you fire it on demand instead of waiting
for the schedule). Check the run's summary for the draft link, then check your
Substack dashboard's Drafts tab.

## Tuning the voice

Open `generate_and_draft.py` and edit `SYSTEM_PROMPT`. That's the entire lever —
tighten it, add example lines, ban phrases, whatever. No other code needs to
change for voice tuning.

## Adjusting the schedule

Edit the `cron` line in `.github/workflows/daily-draft.yml`. Cron is always UTC
regardless of where you are — e.g. `0 11 * * *` = 11:00 UTC daily. Use
[crontab.guru](https://crontab.guru) if you want a different time.

## What this deliberately does NOT do

- **Never auto-publishes.** `publish=False` is hard-coded in the script, not
  just a default — changing that requires editing the source, not a config flag.
- **No distribution/crossposting yet.** That's the next layer (Tier 1 from
  earlier): an RSS or email trigger off your *published* posts that fires
  IG/X/LinkedIn captions automatically. Separate build, bolts on top of this
  once you're happy with the draft quality.

## If it breaks

The cookie auth is unofficial (Substack has no public publish API) — if a
run fails with an auth error, it likely means the cookie expired or Substack
changed something server-side. Re-extract the cookie (step 2) and update the
secret. This is the one maintenance cost of this whole approach.
