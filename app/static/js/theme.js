'use strict';
(function () {
  const doc = document.documentElement;
  const body = document.body;
  const themeToggle = () => {
    try {
      const isDark = doc.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      updateToggleIcon(isDark);
    } catch (_) {}
  };
  function updateToggleIcon(isDark) {
    const moon = document.querySelector('#themeToggle [data-icon="moon"]');
    const sun = document.querySelector('#themeToggle [data-icon="sun"]');
    if (!moon || !sun) return;
    if (isDark) {
      moon.classList.add('d-none');
      sun.classList.remove('d-none');
    } else {
      sun.classList.add('d-none');
      moon.classList.remove('d-none');
    }
  }
  function initThemeFromStorage() {
    try {
      const stored = localStorage.getItem('theme');
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isDark = stored ? stored === 'dark' : prefersDark;
      if (isDark) doc.classList.add('dark'); else doc.classList.remove('dark');
      updateToggleIcon(isDark);
    } catch (_) {}
  }

  function hideLoader() { document.getElementById('globalLoader')?.classList.remove('show'); }

  function hookLinksForLoader() {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a');
      if (!a) return;
      const url = new URL(a.href, window.location.href);
      if (url.origin === window.location.origin && !a.hasAttribute('data-no-loader') && a.target !== '_blank') {
        showLoader();
      }
    }, true);
    window.addEventListener('pageshow', hideLoader);
  }

  function initAOS() {
    if (window.AOS) {
      window.AOS.init({ duration: 600, once: true, offset: 24, easing: 'ease-out-cubic' });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initThemeFromStorage();
    const btn = document.getElementById('themeToggle');
    if (btn) btn.addEventListener('click', themeToggle);
    hookLinksForLoader();
    initAOS();
  });
})();
