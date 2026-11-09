// Linkwave Technology — contact form serverless endpoint (reference implementation).
// Deploy only on an owner-approved serverless platform (Vercel/Netlify). Never commit
// secrets: all credentials come from environment variables.
//
// Contract (used by js/linkwave.js):
//   request : POST application/json { name, email, phone?, subject, message, _gotcha?, language?, page? }
//   success : 200 { ok: true, accepted: true, id }
//   invalid : 400 { ok: false, errors: [{ field, code }] }   codes: required|badEmail|badPhone|tooLong|invalid
//   limited : 429 { ok: false, errors: [{ field: '', code: 'rateLimited' }] }
//   failure : 502 { ok: false }                                (provider refused/failed)
//
// Security controls: origin allowlist, JSON-only POST, 16 KB payload cap, server-side
// validation and length limits, CR/LF + control-character rejection (no header injection),
// honeypot, best-effort IP rate limit, validated Reply-To, escaped email body, no PII logs.

import nodemailer from 'nodemailer';

const MAX_BYTES = 16 * 1024;
const LIMITS = { name: 100, email: 254, phone: 30, subject: 150, message: 3000 };
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const PHONE_RE = /^[+()0-9\s-]{7,30}$/;
const CONTROL_RE = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/;

// Best-effort per-instance rate limit. Configure the platform WAF / add a durable
// store (Redis/Upstash/KV) if stronger distributed limits are required.
const WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS = 5;
const hits = new Map();

function allowedOrigins() {
  return (process.env.ALLOWED_ORIGINS || 'https://linkwave.tech,https://www.linkwave.tech')
    .split(',').map((s) => s.trim()).filter(Boolean);
}

function clientIp(req) {
  const forwarded = req.headers['x-forwarded-for'];
  return (Array.isArray(forwarded) ? forwarded[0] : (forwarded || '').split(',')[0]).trim() || 'unknown';
}

function rateLimited(ip) {
  const now = Date.now();
  const current = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  current.push(now);
  hits.set(ip, current);
  if (hits.size > 5000) {
    for (const [key, value] of hits) {
      if (!value.some((t) => now - t < WINDOW_MS)) hits.delete(key);
    }
  }
  return current.length > MAX_REQUESTS;
}

function validate(payload) {
  const errors = [];
  for (const field of ['name', 'email', 'subject', 'message']) {
    const value = payload[field];
    if (typeof value !== 'string' || !value.trim()) errors.push({ field, code: 'required' });
  }
  for (const [field, limit] of Object.entries(LIMITS)) {
    const value = payload[field];
    if (value !== undefined && value !== null) {
      if (typeof value !== 'string') errors.push({ field, code: 'invalid' });
      else if (value.length > limit) errors.push({ field, code: 'tooLong' });
      else if (CONTROL_RE.test(value)) errors.push({ field, code: 'invalid' });
    }
  }
  const email = typeof payload.email === 'string' ? payload.email.trim() : '';
  if (email && !EMAIL_RE.test(email)) errors.push({ field: 'email', code: 'badEmail' });
  const phone = typeof payload.phone === 'string' ? payload.phone.trim() : '';
  if (phone && !PHONE_RE.test(phone)) errors.push({ field: 'phone', code: 'badPhone' });
  for (const field of ['name', 'email', 'subject', 'phone']) {
    const value = payload[field];
    if (typeof value === 'string' && /[\r\n]/.test(value)) errors.push({ field, code: 'invalid' });
  }
  return errors;
}

function escapeHtml(value) {
  return String(value === undefined || value === null ? '' : value)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function safeSingleLine(value, fallback) {
  const text = String(value || '').replace(/[\r\n\t]+/g, ' ').replace(/\s+/g, ' ').trim();
  return text || fallback;
}

function buildTransport() {
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 587),
    secure: String(process.env.SMTP_SECURE || 'false') === 'true',
    auth: process.env.SMTP_USER
      ? { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
      : undefined,
  });
}

export default async function handler(req, res) {
  const origin = req.headers.origin || '';
  const allowed = allowedOrigins();
  if (origin && !allowed.includes(origin)) {
    return res.status(403).json({ ok: false });
  }
  if (origin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
  }
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
    return res.status(204).end();
  }
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST, OPTIONS');
    return res.status(405).json({ ok: false });
  }
  const contentType = String(req.headers['content-type'] || '');
  if (!contentType.includes('application/json')) return res.status(415).json({ ok: false });
  const length = Number(req.headers['content-length'] || 0);
  if (length > MAX_BYTES) return res.status(413).json({ ok: false });

  let payload = req.body;
  if (Buffer.isBuffer(payload)) payload = payload.toString('utf-8');
  if (typeof payload === 'string') {
    try { payload = JSON.parse(payload); } catch (error) { return res.status(400).json({ ok: false }); }
  }
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return res.status(400).json({ ok: false });
  }

  if (rateLimited(clientIp(req))) {
    return res.status(429).json({ ok: false, errors: [{ field: '', code: 'rateLimited' }] });
  }
  if (typeof payload._gotcha === 'string' && payload._gotcha.trim()) {
    return res.status(400).json({ ok: false, errors: [{ field: '', code: 'honeypot' }] });
  }
  const errors = validate(payload);
  if (errors.length) return res.status(400).json({ ok: false, errors });

  const to = process.env.MAIL_TO || 'info@linkwave.tech';
  let from = process.env.MAIL_FROM || '';
  if (!from) return res.status(500).json({ ok: false });
  let subject = safeSingleLine(payload.subject, 'Website enquiry');
  if (subject.length > 150) subject = subject.slice(0, 150);
  const replyTo = payload.email.trim();
  const lines = [
    'New enquiry from the Linkwave Technology website',
    '',
    'Name:    ' + safeSingleLine(payload.name, ''),
    'Email:   ' + replyTo,
    'Phone:   ' + safeSingleLine(payload.phone, '—'),
    'Subject: ' + subject,
    'Page:    ' + safeSingleLine(payload.page, '—'),
    'Lang:    ' + (payload.language === 'ar' ? 'AR' : 'EN'),
    '',
    'Message:',
    String(payload.message || '').replace(/\r\n/g, '\n'),
  ];
  const html = '<h2>New website enquiry</h2><table cellpadding="6" border="0">'
    + '<tr><td><b>Name</b></td><td>' + escapeHtml(payload.name) + '</td></tr>'
    + '<tr><td><b>Email</b></td><td>' + escapeHtml(replyTo) + '</td></tr>'
    + '<tr><td><b>Phone</b></td><td>' + escapeHtml(safeSingleLine(payload.phone, '—')) + '</td></tr>'
    + '<tr><td><b>Subject</b></td><td>' + escapeHtml(subject) + '</td></tr>'
    + '<tr><td><b>Page</b></td><td>' + escapeHtml(safeSingleLine(payload.page, '—')) + '</td></tr>'
    + '</table><p><b>Message</b></p><pre style="white-space:pre-wrap;font-family:inherit">'
    + escapeHtml(String(payload.message || '')) + '</pre>';

  try {
    const transport = buildTransport();
    const info = await transport.sendMail({
      from,
      to,
      replyTo,
      subject: 'Website enquiry: ' + subject,
      text: lines.join('\n'),
      html,
    });
    if (!info || !info.accepted || !info.accepted.length) {
      return res.status(502).json({ ok: false });
    }
    return res.status(200).json({ ok: true, accepted: true, id: info.messageId || null });
  } catch (error) {
    // Never log message contents or customer data.
    console.error('contact-form delivery failed:', error && error.code ? error.code : 'unknown');
    return res.status(502).json({ ok: false });
  }
}
