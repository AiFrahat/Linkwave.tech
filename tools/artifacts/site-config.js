/* Public site configuration (no secrets may ever be placed here).
 * RELEASE 2026-11-09: contact-form submission is temporarily DISABLED for production.
 * The FormSubmit implementation is preserved; activation requires setting formEndpoint
 * and restoring the CSP form origin (see tools/FORMSUBMIT-SETUP.md). */
window.LINKWAVE_CONFIG = {
  phone: null,                      // Additional phone if different from +20 127 666 8018
  email: 'info@linkwave.tech',      // Approved public contact mailbox
  address: null,                    // Verified office address
  whatsapp: '201276668018',         // International number without spaces
  formEndpoint: null,               // DISABLED for release; null = no submission possible
  formEndpointPending: 'https://formsubmit.co/ajax/info@linkwave.tech',
  formCooldownMs: 30000             // Client-side duplicate-submission cooldown
};
