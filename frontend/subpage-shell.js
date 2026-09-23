/**
 * Unified Subpage & Header Shell Script for Metri-Report
 * Handles scroll-direction based header hide/show and unified mobile menu toggling.
 */
(function () {
  'use strict';

  // Global ScrambleText Custom Element registration for hacker-tech navbar animations
  if (typeof window !== 'undefined' && !customElements.get('c-scramble-text')) {
    class ScrambleText extends HTMLElement {
      connectedCallback() {
        this.originalText = this.getAttribute('data-datocms-content-link-source') || this.textContent.trim();
        this.chars = '!<>-_\\/[]{}—=+*^?#________';
        
        const parent = this.closest('a, button');
        if (parent && !parent._scrambleBound) {
          parent._scrambleBound = true;
          parent.addEventListener('mouseenter', () => {
            parent.querySelectorAll('c-scramble-text').forEach(el => el.scrambleText && el.scrambleText());
          });
          parent.addEventListener('mouseleave', () => {
            parent.querySelectorAll('c-scramble-text').forEach(el => el.resetText && el.resetText());
          });
        }
      }
      scrambleText() {
        if (!this.originalText) {
          this.originalText = this.getAttribute('data-datocms-content-link-source') || this.textContent.trim();
        }
        if (!this.chars) this.chars = '!<>-_\\/[]{}—=+*^?#________';
        let iteration = 0;
        clearInterval(this.interval);
        this.interval = setInterval(() => {
          this.textContent = this.originalText
            .split('')
            .map((char, index) => {
              if (index < iteration) return this.originalText[index];
              return this.chars[Math.floor(Math.random() * this.chars.length)];
            })
            .join('');
          if (iteration >= this.originalText.length) clearInterval(this.interval);
          iteration += 1 / 2;
        }, 20);
      }
      resetText() {
        clearInterval(this.interval);
        if (this.originalText) this.textContent = this.originalText;
      }
    }
    customElements.define('c-scramble-text', ScrambleText);
    window.ScrambleText = ScrambleText;
  }

  function isMobileMenuOpen() {
    const header = document.querySelector('header.c-header, .c-header, [data-menu-header]');
    return (
      document.documentElement.classList.contains('has-menu-mobile-open') ||
      document.documentElement.classList.contains('is-menu-open') ||
      (header && header.classList.contains('is-menu-open'))
    );
  }

  function initHeaderScroll() {
    let lastScrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
    let ticking = false;
    const threshold = 6; // Minimum scroll delta

    function updateHeader() {
      const currentScrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
      const header = document.querySelector('header.c-header, .c-header, [data-menu-header]');

      // Do not hide if mobile menu is open
      if (isMobileMenuOpen()) {
        if (header) {
          header.classList.remove('is-header-hidden');
          header.classList.add('is-header-visible');
        }
        document.documentElement.classList.remove('has-header-hidden');
        document.documentElement.classList.add('has-header-visible');
        lastScrollY = currentScrollY;
        ticking = false;
        return;
      }

      if (currentScrollY <= 30) {
        // At or near top of the page -> Always visible
        if (header) {
          header.classList.remove('is-header-hidden');
          header.classList.add('is-header-visible');
        }
        document.documentElement.classList.remove('has-header-hidden');
        document.documentElement.classList.add('has-header-visible');
      } else if (Math.abs(currentScrollY - lastScrollY) >= threshold) {
        if (currentScrollY > lastScrollY) {
          // Scrolling DOWN -> Hide navbar and STAY HIDDEN when scroll stops
          if (header) {
            header.classList.add('is-header-hidden');
            header.classList.remove('is-header-visible');
          }
          document.documentElement.classList.add('has-header-hidden');
          document.documentElement.classList.remove('has-header-visible');
        } else {
          // Scrolling UP -> Show navbar and STAY VISIBLE when scroll stops
          if (header) {
            header.classList.remove('is-header-hidden');
            header.classList.add('is-header-visible');
          }
          document.documentElement.classList.remove('has-header-hidden');
          document.documentElement.classList.add('has-header-visible');
        }
        lastScrollY = currentScrollY;
      }

      ticking = false;
    }

    function onScroll() {
      if (!ticking) {
        window.requestAnimationFrame(updateHeader);
        ticking = true;
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    // Run initial check
    updateHeader();
  }

  // Global helper functions exposed for inline handlers or direct clicks
  window.toggleMetriMobileMenu = function (e) {
    if (e) {
      if (typeof e.preventDefault === 'function') e.preventDefault();
      if (typeof e.stopPropagation === 'function') e.stopPropagation();
    }

    const header = document.querySelector('header.c-header, .c-header, [data-menu-header]');
    const willBeOpen = !isMobileMenuOpen();

    document.documentElement.classList.toggle('has-menu-mobile-open', willBeOpen);
    document.documentElement.classList.toggle('is-menu-open', willBeOpen);
    document.body.classList.toggle('has-menu-mobile-open', willBeOpen);
    document.body.classList.toggle('is-menu-open', willBeOpen);

    if (header) {
      header.classList.toggle('is-menu-open', willBeOpen);
      header.classList.toggle('has-menu-mobile-open', willBeOpen);
      if (willBeOpen) {
        header.classList.remove('is-header-hidden');
        header.classList.add('is-header-visible');
      }
    }

    const toggles = document.querySelectorAll('[data-menu-mobile-toggle], .c-header_mobile_menu_toggle');
    toggles.forEach(t => t.setAttribute('aria-expanded', willBeOpen ? 'true' : 'false'));
  };

  window.closeMetriMobileMenu = function () {
    const header = document.querySelector('header.c-header, .c-header, [data-menu-header]');
    document.documentElement.classList.remove('has-menu-mobile-open', 'is-menu-open');
    document.body.classList.remove('has-menu-mobile-open', 'is-menu-open');
    if (header) {
      header.classList.remove('is-menu-open', 'has-menu-mobile-open');
    }
    const toggles = document.querySelectorAll('[data-menu-mobile-toggle], .c-header_mobile_menu_toggle');
    toggles.forEach(t => t.setAttribute('aria-expanded', 'false'));
  };

  // Bind close on overlay, link click, or outside click safely
  function initMobileMenuCloseListener() {
    document.addEventListener('click', function (e) {
      if (!isMobileMenuOpen()) return;

      // If toggle button was clicked, ignore (handled by onclick)
      if (
        e.target.closest('[data-menu-mobile-toggle]') ||
        e.target.closest('.c-header_mobile_menu_toggle')
      ) {
        return;
      }

      // If clicked on a mobile menu navigation link or action button, close drawer
      if (
        e.target.closest('.c-header_mobile_menu_link') ||
        e.target.closest('.c-header_mobile_menu_buttons a') ||
        e.target.closest('.c-header_overlay') ||
        e.target.closest('[data-menu-overlay]')
      ) {
        window.closeMetriMobileMenu();
        return;
      }

      // If clicked inside the menu white card (not a link), keep it open
      if (
        e.target.closest('.c-header_mobile_menu_inner') ||
        e.target.closest('[data-menu-mobile-inner]')
      ) {
        return;
      }

      // Outside click closes drawer
      window.closeMetriMobileMenu();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initHeaderScroll();
      initMobileMenuCloseListener();
    });
  } else {
    initHeaderScroll();
    initMobileMenuCloseListener();
  }
})();
