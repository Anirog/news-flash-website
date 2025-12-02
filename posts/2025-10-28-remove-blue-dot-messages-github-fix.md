---
title: Remove Blue Dot Messages GitHub Fix
date: 2025-10-28
slug: 2025-10-28-remove-blue-dot-messages-github-fix
tags: [tech, github]
image: https://ik.imagekit.io/1wh3oo1zp/Remove-Blue-Dot-Messages-GitHub-Fix_XtKuVGmWR
image_alt: Remove Blue Dot Messages GitHub Fix
---

When I went to GitHub.com, a nice little blue dot would appear next to the **Messages** icon whenever there was something new — a notification, a mention, or anything that needed my attention.

But for a while, that blue dot got stuck.  

Even after checking every notification and inbox tab, it just wouldn’t go away.  

After some searching, I found [this Stack Overflow thread](https://stackoverflow.com/questions/78140763/github-inbox-empty-but-still-showing-1-and-blue-dot), which linked to an official GitHub support reply that explained the cause:

> The issue you are experiencing is a known bug that often occurs when you receive notifications from accounts that have been suspended or marked as spammy. Our engineering team is aware of this issue and is actively working to address it.

The workaround they suggested finally fixed it — by marking all notifications as read using the GitHub Activity API.

Run this command in Terminal, replacing `$TOKEN` with your personal access token:

```bash
curl -X PUT -H "Authorization: token $TOKEN" https://api.github.com/notifications
```

After running that, the blue dot disappeared instantly.  

It was such a small thing, but weirdly satisfying.

---

### How to get a GitHub token with **notifications** scope

Here's the quick way:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Give it a name, set an expiry date, and check the **notifications** scope (plus anything else you actually need).
4. Click **Generate token** and copy it -- you'll only see it once.

That's it. Paste it into the command above and watch the blue dot vanish.