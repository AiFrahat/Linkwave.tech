/* Public site configuration.
 * The verified phone number is published statically in the page templates
 * (footer + contact page), so it works even without JavaScript.
 * Fill the remaining verified details when they are approved, then commit this file:
 * the contact sections and the enquiry form pick the values up automatically.
 * Keep secrets (mail credentials, API keys) on the server side, never here. */
window.LINKWAVE_CONFIG = {
  phone: null,          // Additional phone if different from the published +20 127 666 8018
  email: null,          // Example: "info@linkwave.tech"
  address: null,        // Verified office address
  whatsapp: null,       // International number without spaces: "201276668018"
  formEndpoint: null    // HTTPS endpoint that accepts POST JSON; null = local validation only
};
