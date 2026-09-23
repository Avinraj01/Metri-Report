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

  // 6. Unified Mobile Menu Drawer Handler
  function initMobileMenu() {
    const overlay = document.querySelector("[data-menu-overlay], .c-header_overlay");
    const mobileLinks = document.querySelectorAll(".c-header_mobile_menu_link, .c-header_mobile_menu_buttons a");

    window.toggleMetriMobileMenu = function (e) {
      if (e) {
        if (typeof e.preventDefault === 'function') e.preventDefault();
        if (typeof e.stopPropagation === 'function') e.stopPropagation();
      }
      const header = document.querySelector('header.c-header, .c-header, [data-menu-header]');
      const isOpen = document.documentElement.classList.contains('has-menu-mobile-open') ||
                     document.documentElement.classList.contains('is-menu-open') ||
                     (header && header.classList.contains('is-menu-open'));

      const willBeOpen = !isOpen;

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
      toggles.forEach(t => {
        t.setAttribute('aria-expanded', willBeOpen ? 'true' : 'false');
      });
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

    if (overlay) {
      overlay.addEventListener('click', window.closeMetriMobileMenu);
    }

    mobileLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        window.closeMetriMobileMenu();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') window.closeMetriMobileMenu();
    });
  }

  // 7. Inject & Render Active Metrologist Profile Avatar Icon & Dropdown next to Dashboard button
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

      const nameToShow = user.displayName || (user.name ? user.name.split('(')[0].trim() : 'Avinash Kumar');
      const desigToShow = user.designation || 'Lead Test Engineer';

      // Render Avatar Icon Button in Navigation Headers
      const navButtons = document.querySelectorAll('.c-header_nav_buttons');
      navButtons.forEach(container => {
        // Remove old wide badge if present
        const oldWideBadge = container.querySelector('.c-header_user_badge');
        if (oldWideBadge) oldWideBadge.remove();

        let wrap = container.querySelector('.c-header_user_profile_wrap');
        if (!wrap) {
          wrap = document.createElement('div');
          wrap.className = 'c-header_user_profile_wrap';
          wrap.style.cssText = `
            position: relative;
            display: inline-flex;
            align-items: center;
            margin-left: 8px;
            z-index: 100;
          `;

          wrap.innerHTML = `
            <button class="c-header_user_avatar_btn" type="button" aria-label="User Profile" title="${nameToShow} (${desigToShow})" style="
              width: 40px;
              height: 40px;
              border-radius: 50%;
              padding: 0;
              border: 2px solid #ff2d78;
              background: #ff2d78;
              cursor: pointer;
              position: relative;
              display: flex;
              align-items: center;
              justify-content: center;
              transition: all 0.25s ease;
              box-shadow: 0 0 14px rgba(255, 45, 120, 0.4);
              flex-shrink: 0;
            ">
              <svg viewBox="0 0 100 100" style="width: 100%; height: 100%; border-radius: 50%; display: block;">
                <circle cx="50" cy="50" r="50" fill="#ff2d78" />
                <circle cx="50" cy="38" r="16" fill="#ffffff" />
                <path d="M 23 84 A 28 28 0 0 1 77 84 Z" fill="#ffffff" />
              </svg>
              <span style="
                position: absolute;
                bottom: -1px;
                right: -1px;
                width: 11px;
                height: 11px;
                border-radius: 50%;
                background: #10b981;
                border: 2px solid #0d0417;
                box-shadow: 0 0 6px #10b981;
                display: block;
              "></span>
            </button>

            <!-- Interactive Profile Card Popup -->
            <div class="c-header_user_dropdown" style="
              display: none;
              position: absolute;
              top: calc(100% + 12px);
              right: 0;
              width: 290px;
              background: rgba(18, 10, 32, 0.97);
              backdrop-filter: blur(28px);
              -webkit-backdrop-filter: blur(28px);
              border: 1px solid rgba(255, 45, 120, 0.4);
              border-radius: 16px;
              box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.9), 0 0 30px rgba(255, 45, 120, 0.25);
              padding: 18px;
              z-index: 99999;
              text-align: left;
            ">
              <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0; border: 2px solid #ff2d78; overflow: hidden; box-shadow: 0 0 12px rgba(255, 45, 120, 0.5);">
                  <svg viewBox="0 0 100 100" style="width: 100%; height: 100%; display: block;">
                    <circle cx="50" cy="50" r="50" fill="#ff2d78" />
                    <circle cx="50" cy="38" r="16" fill="#ffffff" />
                    <path d="M 23 84 A 28 28 0 0 1 77 84 Z" fill="#ffffff" />
                  </svg>
                </div>
                <div style="min-width: 0; flex: 1;">
                  <div class="metri-user-pop-name" style="font-weight: 700; color: #ffffff; font-size: 14.5px; font-family: 'Outfit', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${nameToShow}</div>
                  <div class="metri-user-pop-desig" style="display: inline-block; background: rgba(255, 45, 120, 0.16); border: 1px solid rgba(255, 45, 120, 0.45); color: #ff659c; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 9999px; margin-top: 4px;">${desigToShow}</div>
                </div>
              </div>

              <div style="background: rgba(0,0,0,0.35); border-radius: 10px; padding: 10px 12px; margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.07); font-size: 12px;">
                <div style="color: #94a3b8; display: flex; justify-content: space-between; margin-bottom: 5px;">
                  <span>Email:</span>
                  <span class="metri-user-pop-email" style="color: #cbd5e1; font-family: monospace; font-size: 11px;">${user.email || 'officer@metrireport.local'}</span>
                </div>
                <div style="color: #94a3b8; display: flex; justify-content: space-between;">
                  <span>Authority:</span>
                  <span style="color: #10b981; font-weight: 600; font-size: 11px;">● OIML R-76 Verified</span>
                </div>
              </div>

              <div style="display: flex; flex-direction: column; gap: 8px;">
                <a href="/user-privileges-&-rbac" style="display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; background: rgba(255,255,255,0.05); color: #f1f5f9; font-size: 12.5px; text-decoration: none; font-weight: 500; transition: background 0.2s;">
                  <span style="font-size: 14px;">🛡️</span>
                  <span>User Privileges &amp; RBAC</span>
                </a>
                <button type="button" class="metri-btn-switch-account" style="display: flex; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 8px; background: rgba(255, 45, 120, 0.15); border: 1px solid rgba(255, 45, 120, 0.4); color: #ff659c; font-size: 12.5px; font-weight: 600; text-align: left; cursor: pointer; transition: all 0.2s;">
                  <span style="font-size: 14px;">🔄</span>
                  <span>Switch Officer / Re-Login</span>
                </button>
              </div>
            </div>
          `;

          const btn = wrap.querySelector('.c-header_user_avatar_btn');
          const dropdown = wrap.querySelector('.c-header_user_dropdown');
          const switchBtn = wrap.querySelector('.metri-btn-switch-account');

          btn.addEventListener('mouseenter', () => {
            btn.style.boxShadow = '0 0 20px rgba(255, 45, 120, 0.7)';
            btn.style.transform = 'scale(1.05)';
          });
          btn.addEventListener('mouseleave', () => {
            btn.style.boxShadow = '0 0 14px rgba(255, 45, 120, 0.4)';
            btn.style.transform = 'scale(1)';
          });

          btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = dropdown.style.display === 'block';
            document.querySelectorAll('.c-header_user_dropdown').forEach(d => d.style.display = 'none');
            dropdown.style.display = isOpen ? 'none' : 'block';
          });

          if (switchBtn) {
            switchBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              dropdown.style.display = 'none';
              if (window.reopenLoginGate) {
                window.reopenLoginGate();
              } else {
                localStorage.removeItem('token');
                localStorage.removeItem('metri_token');
                window.location.reload();
              }
            });
          }

          container.appendChild(wrap);
        } else {
          const btn = wrap.querySelector('.c-header_user_avatar_btn');
          if (btn) btn.title = `${nameToShow} (${desigToShow})`;
          const nameEl = wrap.querySelector('.metri-user-pop-name');
          if (nameEl) nameEl.textContent = nameToShow;
          const desigEl = wrap.querySelector('.metri-user-pop-desig');
          if (desigEl) desigEl.textContent = desigToShow;
          const emailEl = wrap.querySelector('.metri-user-pop-email');
          if (emailEl) emailEl.textContent = user.email || 'officer@metrireport.local';
        }
      });
    }

    // Global listener to close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.c-header_user_profile_wrap')) {
        document.querySelectorAll('.c-header_user_dropdown').forEach(d => d.style.display = 'none');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.c-header_user_dropdown').forEach(d => d.style.display = 'none');
      }
    });

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

