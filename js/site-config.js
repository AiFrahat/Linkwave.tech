/* Public site configuration (no secrets may ever be placed here).
 * The contact recipient and public channels are rendered from these values.
 * Form submissions go to formEndpoint (an https serverless function) — set it only
 * after the owner has configured and verified the endpoint; the form stays disabled
 * while it is null. Keep mail credentials/API keys on the server, never in this file. */
window.LINKWAVE_CONFIG = {
  phone: null,                      // Additional phone if different from +20 127 666 8018
  email: 'info@linkwave.tech',      // Approved public contact mailbox
  address: null,                    // Verified office address
  whatsapp: '201276668018',         // International number without spaces
  formEndpoint: null,               // e.g. '/api/contact' or an https:// serverless URL
  formCooldownMs: 30000             // Client-side duplicate-submission cooldown
};
