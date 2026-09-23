/**
 * METRI-REPORT App Initializer
 * Shared initialization script for all sub-pages.
 * Mirrors the Astro layout page-ready behaviour so CSS animations and
 * the c-header component render correctly.
 */
(function () {
  const html = document.documentElement;

  // 1. Set critical CSS layout variables that the Astro layout normally injects via JS
  function setCSSVars() {
    const root = document.documentElement.style;

    // Grid layout variables - match Cerebrium site defaults
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);

    let gridMargin, gridGutter;
    if (vw >= 2400) { gridMargin = '80px'; gridGutter = '32px'; }
    else if (vw >= 2000) { gridMargin = '72px'; gridGutter = '28px'; }
    else if (vw >= 1800) { gridMargin = '64px'; gridGutter = '24px'; }
    else if (vw >= 1600) { gridMargin = '56px'; gridGutter = '24px'; }
    else if (vw >= 1400) { gridMargin = '48px'; gridGutter = '20px'; }
    else if (vw >= 1200) { gridMargin = '40px'; gridGutter = '20px'; }
    else if (vw >= 1000) { gridMargin = '32px'; gridGutter = '16px'; }
    else if (vw >= 700) { gridMargin = '24px'; gridGutter = '16px'; }
    else if (vw >= 500) { gridMargin = '20px'; gridGutter = '12px'; }
    else { gridMargin = '16px'; gridGutter = '12px'; }

    root.setProperty('--grid-margin', gridMargin);
    root.setProperty('--grid-gutter', gridGutter);
    root.setProperty('--vw', vw + 'px');

    // Header height
    const headerEl = document.querySelector('[data-menu-header]');
    if (headerEl) {
      const h = headerEl.getBoundingClientRect().height || 72;
      root.setProperty('--header-height', h + 'px');
    } else {
      root.setProperty('--header-height', '72px');
    }

    // Announcement banner height (0 for sub-pages)
    root.setProperty('--announcement-banner-height', '0px');
  }

  // 2. Trigger page-ready animation states (mirrors Astro layout behaviour)
  function markReady() {
    setCSSVars();
    html.classList.remove('is-initial-loading');
    html.classList.add('is-ready');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markReady);
  } else {
    markReady();
  }

  // 3. Resize handler to keep CSS vars up to date
  window.addEventListener('resize', function () {
    setCSSVars();
  }, { passive: true });

  // 4. Scroll-based header transparency/hide
  window.addEventListener('DOMContentLoaded', function () {
    const header = document.querySelector('[data-menu-header]');
    if (!header) return;

    // Update header height after DOM is ready
    const h = header.getBoundingClientRect().height || 72;
    document.documentElement.style.setProperty('--header-height', h + 'px');

    let lastScroll = 0;
    window.addEventListener('scroll', function () {
      const y = window.scrollY;
      if (y > 10) {
        header.classList.add('is-scrolled');
      } else {
        header.classList.remove('is-scrolled');
      }
      lastScroll = y;
    }, { passive: true });
  });

  // 5. Animate elements into view (IntersectionObserver for anim- classes)
  window.addEventListener('DOMContentLoaded', function () {
    if (!('IntersectionObserver' in window)) return;
    const animElements = document.querySelectorAll('.anim-transform-opacity, .anim-scale, .animated-line');
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-inview');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    animElements.forEach(function (el) { observer.observe(el); });
  });

  // 6. Unified Mobile Menu Drawer Handler for Subpages
  function initMobileMenu() {
    const toggleButtons = document.querySelectorAll("[data-menu-mobile-toggle], .c-header_mobile_menu_toggle");
    const header = document.querySelector("[data-menu-header], header.c-header");
    const overlay = document.querySelector("[data-menu-overlay], .c-header_overlay");
    const mobileLinks = document.querySelectorAll(".c-header_mobile_menu_link, .c-header_mobile_menu_buttons a");

    function openMenu() {
      if (header) header.classList.add("is-menu-open");
      document.documentElement.classList.add("is-menu-open", "has-menu-mobile-open");
      toggleButtons.forEach(function(btn) {
        btn.setAttribute("aria-expanded", "true");
        const sc = btn.querySelector("c-scramble-text");
        if (sc) sc.textContent = "Close";
      });
      document.body.style.overflow = "hidden";
    }

    function closeMenu() {
      if (header) header.classList.remove("is-menu-open");
      document.documentElement.classList.remove("is-menu-open", "has-menu-mobile-open");
      toggleButtons.forEach(function(btn) {
        btn.setAttribute("aria-expanded", "false");
        const sc = btn.querySelector("c-scramble-text");
        if (sc) sc.textContent = "Menu";
      });
      document.body.style.overflow = "";
    }

    function toggleMenu(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      const isOpen = document.documentElement.classList.contains("is-menu-open") || 
                     document.documentElement.classList.contains("has-menu-mobile-open") ||
                     (header && header.classList.contains("is-menu-open"));
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    }

    toggleButtons.forEach(function(btn) {
      btn.addEventListener("click", toggleMenu);
    });

    if (overlay) {
      overlay.addEventListener("click", closeMenu);
    }

    mobileLinks.forEach(function(link) {
      link.addEventListener("click", function() {
        closeMenu();
      });
    });

    document.addEventListener("keydown", function(e) {
      if (e.key === "Escape") closeMenu();
    });
  }

  // 7. Inject & Render Active Metrologist Profile Pill across Navigation Headers
  function initUserSessionBadge() {
    function renderBadge() {
      let user = {
        name: 'Avinash Kumar',
        designation: 'Lead Test Engineer',
        role: 'TEST_ENGINEER',
        email: 'engineer@metrireport.local'
      };
      try {
        const stored = localStorage.getItem('metri_user');
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed && parsed.name) user = parsed;
        } else {
          localStorage.setItem('metri_user', JSON.stringify(user));
        }
      } catch (e) {}

      // Render Desktop Header Pill
      const navButtons = document.querySelectorAll('.c-header_nav_buttons');
      navButtons.forEach(container => {
        let existing = container.querySelector('.c-header_user_badge');
        if (!existing) {
          existing = document.createElement('div');
          existing.className = 'c-header_user_badge max-md:hidden';
          existing.style.cssText = `
            align-items: center;
            gap: 8px;
            background: rgba(16, 24, 39, 0.75);
            border: 1px solid rgba(56, 189, 248, 0.35);
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.12);
            backdrop-filter: blur(16px);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            color: #fff;
            margin-right: 12px;
            white-space: nowrap;
            user-select: none;
            cursor: pointer;
            transition: all 0.2s ease;
          `;
          existing.title = 'Active Session: ' + (user.name || 'Metrology Officer');
          existing.onmouseenter = () => { existing.style.borderColor = '#ff488b'; existing.style.boxShadow = '0 0 16px rgba(255, 72, 139, 0.3)'; };
          existing.onmouseleave = () => { existing.style.borderColor = 'rgba(56, 189, 248, 0.35)'; existing.style.boxShadow = '0 0 16px rgba(56, 189, 248, 0.12)'; };
          existing.addEventListener('click', () => {
            window.location.href = '/user-privileges-&-rbac';
          });
          container.insertBefore(existing, container.firstChild);
        }
        const nameToShow = user.displayName || (user.name ? user.name.split('(')[0].trim() : 'Avinash Kumar');
        const desigToShow = user.designation || 'Lead Test Engineer';
        existing.innerHTML = `
          <span style="width: 7px; height: 7px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; display: inline-block;"></span>
          <span style="font-weight: 700; color: #38bdf8; font-family: 'Outfit', sans-serif;">${nameToShow}</span>
          <span style="opacity: 0.8; font-size: 11px; color: #cbd5e1;">(${desigToShow})</span>
        `;
      });

      // Desktop user badge rendered above; mobile drawer badge removed to match localhost:3000 preview
    }

    renderBadge();
    window.addEventListener('metri_user_changed', renderBadge);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initMobileMenu();
      initUserSessionBadge();
    });
  } else {
    initMobileMenu();
    initUserSessionBadge();
  }
})();

