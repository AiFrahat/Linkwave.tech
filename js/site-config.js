/* Public site configuration (no secrets may ever be placed here).
 * The contact recipient and public channels are rendered from these values.
 * The form uses FormSubmit (free, no registration, no email password, no DNS/MX
 * changes). The first submission triggers a one-time activation e-mail to the
 * owner; submissions are delivered only after that activation is confirmed. */
window.LINKWAVE_CONFIG = {
  phone: null,                      // Additional phone if different from +20 127 666 8018
  email: 'info@linkwave.tech',      // Approved public contact mailbox
  address: null,                    // Verified office address
  whatsapp: '201276668018',         // International number without spaces
  formEndpoint: 'https://formsubmit.co/ajax/info@linkwave.tech',
  formCooldownMs: 30000             // Client-side duplicate-submission cooldown
};
