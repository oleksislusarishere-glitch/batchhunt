# Filling application forms

Use a browser that can upload files (Claude in Chrome: `mcp__claude-in-chrome__*`). Prefer reading and verifying with JavaScript and page text over screenshots.

## Core technique (works even when the Chrome window is in the background)
Real keyboard typing and clicks often don't reach a background tab. Drive the page from JS:
1. **Upload the CV:** `find` the file input → `file_upload` with the PDF path. Never click file inputs (it opens a native picker).
2. **Text fields:** `el.focus(); document.execCommand('selectAll'); document.execCommand('delete'); document.execCommand('insertText', false, value); el.blur();`. `form_input` and setting `.value` often don't update React state; `execCommand` does.
3. **If a value "doesn't stick"** (form says it's missing): clear → blur → focus → insertText → blur, then resubmit.
4. **Buttons and radios:** `el.click()`. For Ashby Yes/No buttons check that `className` contains `_active_`.
5. **Comboboxes** (location, country, "how did you hear"): focus the `role=combobox` input → `insertText('Lisbon')`; in a **separate** call find the `[role=option]` and fire `mousedown` + `click`.
6. **Waiting:** use the browser tool's wait action, not `setTimeout` (background tabs throttle timers; long scripts time out).
7. **Submit** in its own call, wait ~8s, then read the page for success (`Success`, `Thank you`, `?success`, `/thanks`, `applied=ok`). On "Missing entry for required field: X", re-insert X (step 3) and resubmit.

## Per ATS
- **Ashby:** uploading a CV triggers "autofill from resume", which can wipe fields when it finishes. Wait ~20–30s after upload, then fill; re-insert anything it reports missing. Some boards label the resume field "Portfolio Upload".
- **Greenhouse (new UI):** text via execCommand works; react-select dropdowns usually need real clicks with the window in front. Ask the person to bring Chrome forward, or hand over. Invisible reCAPTCHA.
- **Lever / Lever EU:** plain inputs; set `<select>` via value + change event. May show an hCaptcha after submit: hand over.
- **Workable:** use the direct form `apply.workable.com/<account>/j/<shortcode>/apply/` (the jobs.workable.com modal can stay empty). Tick the Privacy Notice box or it fails with "There are some issues". Submit can sit on "Submitting…" for a minute (invisible reCAPTCHA) and then land on `?success`, so re-check before handing over. Numeric salary fields take digits only. Skip the optional EEO survey after success.
- **Recruitee:** fill the visible `...content` inputs, not hidden ones; the real submit button is often labelled "Send". Phone auto-formats: insert `+<country><number>` without spaces.
- **Teamtailor:** some roles require choosing an office location; that's a relocation decision, so ask the person. Decline non-essential cookies.
- **Breezy:** has a honeypot input (`hp_*`): leave it empty.
- **Rippling / Teamtailor:** resume parsing pre-fills fields; check and correct them.
- **Djinni / DOU / Contra / Dribbble / JOIN:** need the person's own login. If they're signed in, apply from their account; untick "save to profile" options so their profile doesn't change.
- **Avature, Workday, iCIMS:** account creation required: hand over.

## Hand over when
- account creation, login, password, captcha or email verification;
- the company forbids AI-written answers or asks for a video;
- a question needs a fact or story not in `profile.md` (Telegram handle, "what did you learn last week", a specific anecdote);
- a choice belongs to the person (office city / relocation, salary below floor, legal questions you're unsure about).
Write each to `TODO.md` with the link, what's already filled, and the exact action.
