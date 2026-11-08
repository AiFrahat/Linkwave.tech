/* Public site configuration.
 * Fill in the verified company details when they are approved, then commit this file:
 * the header/footer/contact sections and the enquiry form pick the values up automatically.
 * Keep secrets (mail credentials, API keys) on the server side, never here. */
window.LINKWAVE_CONFIG = {
  phone: null,          // Example: "+201234567890"
  email: null,          // Example: "info@linkwave.tech"
  address: null,        // Verified office address, in both languages if needed
  whatsapp: null,       // International number without spaces: "201234567890"
  formEndpoint: null    // HTTPS endpoint that accepts POST JSON; null = local validation only
};
