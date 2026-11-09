# FormSubmit setup, activation and real-delivery test

This is the **simplified, backend-free** contact-form delivery for Linkwave Technology.
The website (GitHub Pages) posts the enquiry directly to **FormSubmit** (free, no registration,
no e-mail password, no DNS/MX changes), which forwards it to **info@linkwave.tech**.

> Current status: **local implementation complete; real delivery UNVERIFIED.** The service
> must be activated by the owner (one-time confirmation e-mail) and a real message must be
> confirmed in the mailbox before the form can be considered working in production.

## What is verified (official FormSubmit documentation, checked 2026-11-09)

- Free, **no registration required**; point the form endpoint at the address and confirm the
  e-mail address. Source: <https://formsubmit.co/> and <https://formsubmit.co/help>.
- **AJAX** submissions are supported cross-origin:
  `https://formsubmit.co/ajax/your@email.com` with JSON + `Accept: application/json`.
  Source: <https://formsubmit.co/documentation>, <https://formsubmit.co/ajax-documentation>.
- **Activation:** until the form is activated, submissions are kept (30 days) and an
  activation e-mail is sent to the owner on each submission; after activation the submissions
  are delivered to the mailbox. Source: <https://formsubmit.co/help>.
- **Spam protection:** Google reCAPTCHA (default) and optional `_honey` honeypot; the service
  also runs its own spam filtering. Source: documentation/help.
- **No DNS/MX change** is part of the FormSubmit setup described in the docs (only e-mail
  confirmation).
- Docs state unlimited forms/submissions for an e-mail address; submission archive API is
  limited to 5 accesses/day; submissions retained 30 days. Source: documentation.

**Not verified here:** the exact JSON response schema of the AJAX endpoint (docs do not
document it; the frontend accepts `success:true`/`"true"`, `ok:true` or a "success" message),
reCAPTCHA behaviour with AJAX (this form passes `_captcha=false`), and the detailed legal
privacy/terms text (the official privacy policy is a PDF at
<https://formsubmit.co/privacy.pdf>; it could not be text-extracted in this environment).
The owner should review that policy before production use; no DNS/MX or account changes are
required by this repository.

## Activation and real-delivery test (owner, one-time)

1. Deploy the website through the approved release process **or** use an approved hosted
   preview (the form must be served over HTTP(S), not opened as a local HTML file).
2. Open the English contact page, fill a genuine short enquiry and click **Send**. This first
   submission triggers a **FormSubmit activation e-mail** to `info@linkwave.tech` (check inbox
   and spam/junk). The submission itself is retained by FormSubmit until activation.
3. Open the activation e-mail and click the confirmation/activation link.
4. Wait for confirmation, then submit a **second real test message** with a unique marker,
   e.g. subject `TEST-FORMSUBMIT-2026-11-09`, using the English form. Repeat once with the
   Arabic form.
5. Confirm in `info@linkwave.tech`:
   - both test messages arrive (check spam/junk too);
   - subject shows `Website enquiry: …`;
   - fields (name, e-mail, phone, subject, message) are readable;
   - **Reply-To** is the customer e-mail used in the test;
   - the page showed only “your message was accepted for delivery” (not a claimed receipt).
6. Record the evidence (screenshots of mailbox + form) and update the delivery status from
   **UNVERIFIED** to **VERIFIED** in the contact-form report/gate.

> Do **not** treat the local/mocked tests or a successful HTTP response as proof of mailbox
> delivery. Only step 5 confirms delivery.

## Configuration in this repository

- `js/site-config.js` → `formEndpoint: "https://formsubmit.co/ajax/info@linkwave.tech"`.
- Form includes hidden `_subject`, `_template=table`, `_captcha=false`, and a visually hidden
  `_honey` honeypot.
- CSP allows exactly `https://formsubmit.co` in `connect-src` (no wildcard, no other external
  script/style origins). The endpoint origin is injected at build time via
  `LINKWAVE_FORM_ORIGIN`; rebuilding after changing it:
  ```powershell
  $env:LINKWAVE_FORM_ORIGIN = "https://formsubmit.co"
  python tools/build_release.py --apply --manifest tools/build-manifest.json
  ```
- No SMTP credentials, API secrets, backend function, DNS or MX records exist in this flow.

## Spam / abuse notes

- `_honey` honeypot is checked client-side (never transmitted when filled) and by FormSubmit.
- FormSubmit applies its own spam filtering; reCAPTCHA is disabled (`_captcha=false`) because
  the AJAX flow does not embed the challenge widget. If spam becomes a problem, switch to the
  standard (non-AJAX) FormSubmit form submission so reCAPTCHA is enforced, or re-enable the
  reCAPTCHA flow after owner review.
- Client-side duplicate prevention + 30 s cooldown; FormSubmit rate-limits/spam-filters
  server-side.

## Rollback

1. Set `formEndpoint: null` in `js/site-config.js`, rebuild and deploy through the approved
   process → the form returns to the safe disabled state.
2. Optionally ask FormSubmit to deactivate the form by e-mail (their documented deactivation
   flow).
3. Code rollback: `git revert` the contact-form commits.
No credentials were created by this flow, so there are no secrets to rotate.
