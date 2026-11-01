() => {
  // Installs window.__sched(i) in a YouTube Studio tab. Each call uploads + fills + schedules entry i of
  // http://127.0.0.1:PORT/meta.json exactly like CD's manual procedure (reference/youtube-schedule.md):
  // title, description, not made for kids, altered content YES, tags, related video = first (latest) card,
  // Schedule as public on date/time (IST), "Got it" on the still-checking notice, wait for confirmation.
  // Install: chrome MCP evaluate_script with sourcePath = this file. Then: await window.__sched(i).
  const PORT = 8799;
  const sleep = t => new Promise(r => setTimeout(r, t));
  const vis = e => e && e.offsetParent !== null;
  const until = async (fn, ms = 20000, step = 250) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { const v = fn(); if (v) return v; await sleep(step); } return null; };
  const typeInto = async (el, txt) => { el.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, txt); el.dispatchEvent(new Event('input', { bubbles: true })); await sleep(250); };
  const dlg = () => document.querySelector('ytcp-uploads-dialog');
  const heading = () => [...(dlg()?.querySelectorAll('h1') || [])].filter(vis).map(h => h.innerText.trim()).join('|');

  window.__sched = async (i) => {
    const log = [];
    const M = (await (await fetch(`http://127.0.0.1:${PORT}/meta.json`)).json())[i];
    log.push(M.file);

    // close any leftover "Video scheduled" / "Video processing" popup
    for (let k = 0; k < 3; k++) {
      const c = [...document.querySelectorAll('ytcp-button, button')].find(b => vis(b) && /^close$/i.test((b.innerText || '').trim()) && !b.closest('ytcp-uploads-dialog'));
      if (!c) break; c.click(); await sleep(700);
    }
    // open Create -> Upload videos
    if (!vis(document.querySelector('#select-files-button'))) {
      const cr = [...document.querySelectorAll('button, ytcp-button')].find(b => vis(b) && /^create$/i.test((b.innerText || b.getAttribute('aria-label') || '').trim()));
      cr.click(); await sleep(700);
      const it = [...document.querySelectorAll('tp-yt-paper-item')].find(e => vis(e) && /upload video/i.test(e.innerText));
      it.click();
      await until(() => vis(document.querySelector('#select-files-button')), 8000);
    }
    // feed the file (no native file chooser needed)
    const blob = await (await fetch(`http://127.0.0.1:${PORT}/` + encodeURIComponent(M.file))).blob();
    const dt = new DataTransfer(); dt.items.add(new File([blob], M.file, { type: 'video/mp4' }));
    const inp = document.querySelector('input[type=file]'); inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
    const title = await until(() => dlg()?.querySelector('#title-textarea #textbox'), 30000);
    if (!title) return { error: 'details did not open', log };
    await sleep(800);
    const d = dlg();

    // Details
    await typeInto(d.querySelector('#title-textarea #textbox'), M.title);
    await typeInto(d.querySelector('#description-textarea #textbox'), M.description);
    d.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]').click(); await sleep(250);
    const more = d.querySelector('#toggle-button'); if (more && /show more/i.test(more.innerText)) { more.click(); await sleep(1000); }
    const alt = await until(() => d.querySelector('tp-yt-paper-radio-button[name=VIDEO_HAS_ALTERED_CONTENT_YES]'), 5000); alt && alt.click(); await sleep(250);
    const tagIn = d.querySelector('#tags-container input, ytcp-free-text-chip-bar input');
    tagIn.focus(); tagIn.value = M.tags; tagIn.dispatchEvent(new Event('input', { bubbles: true })); await sleep(200);
    tagIn.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true })); await sleep(500);
    log.push('tags=' + [...d.querySelectorAll('ytcp-chip')].filter(c => c.innerText.trim()).length);

    // Video elements -> related video = first (latest) card
    for (let k = 0; k < 4 && !/video elements/i.test(heading()); k++) { d.querySelector('#next-button').click(); await sleep(1200); }
    const rvBtn = d.querySelector('#shorts-content-links-add-button');
    if (rvBtn) {
      rvBtn.click();
      const card = await until(() => [...document.querySelectorAll('ytcp-entity-card.card')].find(vis), 10000);
      if (card) { log.push('related=' + card.innerText.trim().slice(0, 30)); card.click(); await sleep(1000); }
    }

    // Visibility -> Schedule
    for (let k = 0; k < 4 && !/visibility/i.test(heading()); k++) { d.querySelector('#next-button').click(); await sleep(1200); }
    d.querySelector('#second-container-expand-button').click(); await sleep(1000);
    const sc = d.querySelector('#second-container');
    // date: open the picker and click the day cell inside the right month block (typing does NOT work)
    const trig = sc.querySelector('#datepicker-trigger');
    if (trig.innerText.trim() !== M.date) {
      trig.click(); await sleep(900);
      const [day, mon, yr] = M.date.split(' ');
      const hdr = [...document.querySelectorAll('ytcp-scrollable-calendar *')].find(e => vis(e) && e.childElementCount === 0 && e.innerText.trim().toUpperCase() === (mon + ' ' + yr).toUpperCase());
      const cells = [...document.querySelectorAll('ytcp-scrollable-calendar span.calendar-day')].filter(c => vis(c) && c.innerText.trim() === day && (!hdr || (hdr.compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING)));
      if (cells[0]) { cells[0].click(); await sleep(900); }
    }
    // time
    const ti = [...sc.querySelectorAll('input')].find(vis);
    ti.focus(); ti.select(); document.execCommand('insertText', false, M.time); ti.dispatchEvent(new Event('input', { bubbles: true })); await sleep(200);
    ti.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true })); ti.blur(); await sleep(500);
    const scText = sc.innerText.replace(/\n+/g, ' | ');
    log.push('schedule=' + trig.innerText.trim() + ' ' + ti.value);
    if (trig.innerText.trim() !== M.date || ti.value !== M.time) return { error: 'date/time mismatch', scText, log };
    if (!/GMT\+0530|Time zone/.test(scText)) return { error: 'timezone not IST?', scText, log };

    d.querySelector('#done-button').click(); await sleep(1500);
    const got = await until(() => [...document.querySelectorAll('ytcp-button, button')].find(x => vis(x) && /^got it$/i.test(x.innerText.trim())), 4000);
    if (got) { got.click(); log.push('still-checking notice: Got it'); }
    const ok = await until(() => [...document.querySelectorAll('ytcp-video-share-dialog, tp-yt-paper-dialog, ytcp-dialog')].filter(vis).map(e => e.innerText).find(t => /will be set to public on/i.test(t)), 25000);
    log.push(ok ? (ok.match(/public on [^\n]*?\d{1,2}:\d\d/) || [ok.slice(0, 80)])[0] : 'NO CONFIRMATION (check the Content list)');
    return { ok: !!ok, log };
  };
  return 'installed';
}
