/*
 * Announce "Copied to clipboard" to assistive technology.
 *
 * The theme's copy-code button announces nothing when it copies. This script
 * listens for clicks on that button (found by its aria-label) and writes a
 * short message into the polite live region in _includes/footer_custom.html.
 * The message is cleared after four seconds.
 *
 * Limits:
 * - The message is written when the button is clicked. The script does not
 *   check that the copy itself succeeded.
 * - If the live region is missing, the script does nothing.
 *
 * No dependencies. ES5 syntax, so the file needs no build step.
 */
(function () {
  'use strict';

  var BUTTON_SELECTOR = 'button[aria-label="Copy code to clipboard"]';
  var REGION_ID = 'rup-live-region';
  var MESSAGE = 'Copied to clipboard';
  var CLEAR_AFTER_MS = 4000;
  var clearTimer = null;

  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || typeof target.closest !== 'function') {
      return;
    }
    if (!target.closest(BUTTON_SELECTOR)) {
      return;
    }

    var region = document.getElementById(REGION_ID);
    if (!region) {
      return;
    }

    region.textContent = MESSAGE;
    if (clearTimer !== null) {
      window.clearTimeout(clearTimer);
    }
    clearTimer = window.setTimeout(function () {
      region.textContent = '';
      clearTimer = null;
    }, CLEAR_AFTER_MS);
  });
})();
