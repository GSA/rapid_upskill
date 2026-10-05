/*
 * Light/dark switch.
 *
 * Adds a button at the top right of the side menu. With no saved choice the site follows the
 * device setting; a click saves an explicit "light" or "dark" in this browser (localStorage key
 * "nd-theme"). A small inline script in _includes/head_custom.html applies the saved choice
 * before the page paints, so this file only has to build and run the button.
 *
 * Limits:
 * - If the browser blocks storage, the button still works for the current page only.
 * - A preset without a "dark:" block loads no dark theme and this file is not included.
 *
 * No dependencies. ES5 syntax, so the file needs no build step.
 */
(function () {
  'use strict';

  var KEY = 'nd-theme';
  var root = document.documentElement;
  var query = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  var SUN = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" ' +
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">' +
    '<circle cx="12" cy="12" r="4"/>' +
    '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>' +
    '</svg>';
  var MOON = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" ' +
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

  function current() {
    return root.getAttribute('data-theme') || (query && query.matches ? 'dark' : 'light');
  }

  function build() {
    var host = document.querySelector('.site-nav') || document.querySelector('.site-header');
    if (!host) {
      return;
    }
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'nd-theme-toggle';

    function paint() {
      var dark = current() === 'dark';
      // The icon shows what a click switches to.
      button.innerHTML = dark ? SUN : MOON;
      button.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
      button.title = button.getAttribute('aria-label');
    }

    button.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try {
        localStorage.setItem(KEY, next);
      } catch (e) {
        // Not saved; the choice lasts for this page only.
      }
      paint();
    });
    if (query && query.addEventListener) {
      query.addEventListener('change', paint);
    }

    host.classList.add('nd-has-toggle');
    host.insertBefore(button, host.firstChild);
    paint();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
