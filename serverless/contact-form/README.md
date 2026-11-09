# Linkwave contact form — serverless endpoint (reference implementation)

Minimal, owner-hosted endpoint for the website enquiry form. It receives the JSON from
`js/linkwave.js`, applies server-side validation/anti-abuse checks and forwards the enquiry
by SMTP to **info@linkwave.tech**. It is the only piece that requires a hosting account:
GitHub Pages cannot run server code. No secrets are in the website or this folder.

> **Status: NOT DEPLOYED / delivery UNVERIFIED.** Deploying this function requires owner
> accounts, mailbox credentials and DNS/sender verification. Until the owner completes the
> steps below and a real message is confirmed in the mailbox, contact-form delivery must be
> treated as **UNVERIFIED** (the website form stays disabled while `formEndpoint` is `null`).

## Endpoint contract

`POST application/json`

```json
{ "name": "…", "email": "…", "phone": "…", "subject": "…", "message": "…",
  "_gotcha": "", "language": "en", "page": "/it_contact.html" }
```

| Result | Response |
|---|---|
| accepted for delivery | `200 {"ok":true,"accepted":true,"id":"…"}` |
| invalid | `400 {"ok":false,"errors":[{"field":"email","code":"badEmail"}]}` |
| rate-limited | `429 {"ok":false,"errors":[{"field":"","code":"rateLimited"}]}` |
| delivery failed | `502 {"ok":false}` |

The frontend only shows success when `ok === true`. That means **accepted by the sending
provider**, not a confirmed mailbox receipt.

## Security controls implemented

- Origin allowlist (`ALLOWED_ORIGINS`) with CORS; no wildcard.
- JSON-only `POST`; 16 KB body cap; method allowlist (`POST`/`OPTIONS` → 405 otherwise).
- Server-side validation: required fields, max lengths, email format, optional phone format.
- Control-character / CR-LF rejection for all header-bound fields (no header injection).
- Honeypot `_gotcha` rejected server-side.
- Best-effort per-instance IP rate limit (5 requests / 10 min). **Not distributed**; add the
  platform WAF/rate-limit or a durable store if stronger limits are required.
- Customer email used only as validated `Reply-To`; sender is the verified `MAIL_FROM`.
- Enquiry rendered as plain text + HTML-escaped HTML; no customer data written to logs.
- Fixed recipient `MAIL_TO` (no open relay); secrets only in environment variables.
- `Cache-Control: no-store`.

## Owner setup (required before the form can deliver mail)

1. **Mailbox:** confirm `info@linkwave.tech` is a working mailbox and obtain SMTP
   credentials from its mail provider (host, port, secure mode, username, password).
2. **Sender/DNS:** create/confirm a verified sender such as `website@linkwave.tech` and ask
   the DNS owner to publish the mail provider's **SPF, DKIM and DMARC** records for
   `linkwave.tech`. (No DNS change is made by this repository or this task.)
3. **Hosting:** create a free/paid serverless project (e.g. Vercel, Netlify) and deploy this
   `serverless/contact-form` folder (Node 18+, `npm install`, `api/contact.js` as the
   function). Alternatively port `api/contact.js` to another Node serverless platform.
4. **Environment variables** (set in the hosting dashboard, never commit):
   `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURE`, `SMTP_USER`, `SMTP_PASS`,
   `MAIL_TO=info@linkwave.tech`, `MAIL_FROM=<verified sender>`,
   `ALLOWED_ORIGINS=https://linkwave.tech,https://www.linkwave.tech`.
5. **Verify delivery:** send a real test enquiry from the deployed endpoint to
   `info@linkwave.tech`; confirm arrival (and check spam/junk), confirm `Reply-To` returns to
   the customer address, and confirm the form shows "accepted for delivery" only on
   `{ok:true}`.
6. **Connect the website:** set `formEndpoint` in `js/site-config.js` to the deployed URL,
   then rebuild with the endpoint origin allowed in CSP (build-time, exact origin only):

   ```powershell
   $env:LINKWAVE_FORM_ORIGIN = "https://<deployed-endpoint-origin>"
   python tools/build_release.py --apply --manifest tools/build-manifest.json
   ```

   (`LINKWAVE_FORM_ORIGIN` is appended to `connect-src`; no wildcard is added.)
7. Commit the rebuilt `js/site-config.js` + pages and deploy only through the approved
   release process.

## Managed alternative (UNVERIFIED in this environment)

A managed form endpoint (e.g. Formspree, Web3Forms) would remove the hosting/SMTP steps.
Their current free-tier limits, spam controls, data-retention terms and commercial-use
conditions **could not be verified from this offline environment**, so no provider is
claimed as verified or selected. If the owner verifies one:

- its JSON API must return `{ok:true}` on acceptance (the frontend contract);
- point `formEndpoint` at the form's endpoint URL and add its origin to CSP as above;
- destination email must be `info@linkwave.tech`; confirm provider e-mail verification;
- still verify real delivery before enabling in production.

## Rollback

- Immediate: set `formEndpoint: null` in `js/site-config.js`, rebuild, redeploy → form
  returns to disabled state; no server code involved.
- Serverless: delete/disable the deployed function; the website keeps working (form disabled).
- No customer data is stored by this endpoint, so there is no server-side data to purge.
