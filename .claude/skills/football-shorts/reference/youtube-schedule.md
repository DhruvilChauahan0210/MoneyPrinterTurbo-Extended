# Scheduling Shorts in YouTube Studio

## CD's manual procedure (shown live on 1 Nov 2026). The fast scheduler reproduces exactly this.
Channel: **CD PHANTOM** (`UCfLjJwaxD7VhKwfSmTDQv3Q`). Use CD's real Chrome via the `chrome` MCP (chrome-devtools-mcp
`--autoConnect`). Work in an existing Studio tab, and use `list_pages` to find it. Never navigate CD's other tabs.

1. **Create → Upload videos**, then pick the file.
2. **Details:** Title and Description = the chat metadata blocks as-is. Playlist: none. Audience: **No, not made
   for kids**. Age restriction: **No**. Show more: **Altered content = YES**. Tags = the TAGS block. Licence:
   standard. Embedding on, notify subscribers on, remixing = video and audio, Category **Sport** (the channel
   default), comments On / Basic / Anyone / Top, like count shown.
3. **Video elements → Related video → Add/Edit →** pick the **first (latest) card**. CD: "select the latest one
   always". The picker only lists published videos. No subtitles.
4. **Initial check:** don't wait for it (CD: "we don't need to wait for the upload completes").
5. **Visibility → Schedule → "Schedule as public":** the Short's date, its slot time, time zone
   **(GMT+0530) Local Time** (the default) → **Schedule**. If "We're still checking your content" appears,
   click **Got it**. It still schedules.
6. Pinned comment: only possible after the Short goes live, so CD does it by hand.

## Fast scheduler (about 40s per Short)
```bash
mkdir -p upload_batch && cp ~/Desktop/<the Shorts>.mp4 upload_batch/       # must be inside the repo
python3 .claude/skills/football-shorts/scripts/make_meta.py spec.json upload_batch/meta.json
python3 .claude/skills/football-shorts/scripts/cors_server.py upload_batch 8799 &   # note the PID
```
Then in the Studio tab:
1. `evaluate_script { pageId, sourcePath: ".claude/skills/football-shorts/scripts/sched.js" }` returns `"installed"`.
2. `evaluate_script { function: "async () => { const out=[]; for (let i=0;i<7;i++){ const r=await window.__sched(i); out.push(i+': '+(r.ok?'OK':'?')+' '+(r.error||'')+' '+r.log.slice(-1)); if(r.error) break;} return out; }" }`
3. Repeat for the next index range (keep each call to 6–8 Shorts, or the MCP call may time out).
4. Verify: reload Content → Shorts, read `ytcp-video-row .tablecell-visibility` for the top N rows. All must say **Scheduled**.
5. `kill <server PID>`, then delete `upload_batch/` if CD wants it gone.

## Traps already hit
- `upload_file` can't send several files at once (Studio's input isn't `multiple`), so the scheduler feeds files through `fetch` → `DataTransfer` → `input.files`.
- `upload_file` / `sourcePath` only accept paths inside the workspace (repo), not `~/Desktop`.
- Port 8765 was already taken (returned 401). Use 8799.
- Typing into the date picker does **not** work. Click the `span.calendar-day` cell inside the right month block.
- After the date picker opens, the first visible `input` is the date box, not the time box. Set the date first, then the time.
- Confirmation text is either "Video scheduled" or "Video processing … will be set to public on …".
  Match on `will be set to public on`.
- A Short scheduled before its upload finished shows **Pending** in the list for a few minutes. That's normal.
