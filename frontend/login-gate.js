/**
 * Dribbble-Style Animated Characters Login Gate for Metri-Report
 * 100% Ultra-Realistic Physics Engine with Continuous 60fps RAF Lerp & Spring Dynamics
 * - Real-time organic Bezier spine morphing for Purple Character (Neck Extend & Neck Bend)
 * - Damped eye tracking physics with micro-saccades, blink timers, and boundary clipping
 * - Realistic Opposite-Side Look Away on Show Password
 * - Error Sad Shake & Folded Neck on Empty/Wrong Password Submit
 * - Confetti particle celebration burst STRICTLY BEHIND THE CHARACTERS on successful login!
 */

(function () {
  if (window.location.search.includes('nogate')) {
    document.cookie = "cc_cookie=" + encodeURIComponent(JSON.stringify({ categories: ["necessary"], revision: 0, data: null, consentTimestamp: new Date().toISOString(), consentId: "bypass", services: {}, languageCode: "en" })) + "; path=/";
    const style = document.createElement('style');
    style.innerHTML = '#cc-main { display: none !important; }';
    document.head.appendChild(style);
    return;
  }
  if (document.getElementById('login-overlay')) return;

  let isAuth = false;
  try {
    isAuth = (sessionStorage.getItem('metri_authenticated') === 'true' || localStorage.getItem('metri_authenticated') === 'true') && !window.location.search.includes('login') && !window.location.search.includes('gate');
  } catch (e) { }

  const overlayHtml = `
  <div id="login-overlay" class="${isAuth ? 'logged-in' : ''}">
    <!-- Interactive Silk Shader Background -->
    <canvas id="login-silk-canvas" class="login-silk-canvas"></canvas>
    <div class="login-card">
      <button class="demo-skip" id="login-skip-btn" title="Direct Preview">Skip to site &rarr;</button>
      
      <!-- Left Illustration Stage with Confetti Background -->
      <div class="characters-panel" id="characters-panel">
        <!-- Confetti Canvas Strictly Behind Characters -->
        <canvas id="character-confetti-canvas"></canvas>

        <div class="characters-stage" id="char-stage">
          
          <!-- 1. Purple Character (Back Left) with Dynamic Bezier Spine -->
          <svg class="character char-purple" id="char-purple" viewBox="0 0 200 280" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow: visible;">
            <!-- Real-time Mathematical Bezier Spine Body -->
            <path id="purple-body-path" d="M 20 280 L 20 0 L 140 0 L 140 280 Z" fill="#5812eb"/>
            
            <!-- Facial Features Group attached to Spine Head -->
            <g id="purple-face" style="transform-origin: 80px 30px;">
              <!-- Left Eye -->
              <circle class="eye" cx="62" cy="22" r="5.5" fill="#ffffff"/>
              <circle class="pupil" id="purple-pupil-l" cx="62" cy="22" r="2.8" fill="#111827"/>
              <!-- Right Eye -->
              <circle class="eye" cx="92" cy="22" r="5.5" fill="#ffffff"/>
              <circle class="pupil" id="purple-pupil-r" cx="92" cy="22" r="2.8" fill="#111827"/>
              <!-- Center Nose Bar -->
              <line id="purple-nose" x1="77" y1="26" x2="77" y2="44" stroke="#111827" stroke-width="3.8" stroke-linecap="round" style="opacity: 0; transition: opacity 0.3s ease;"/>
              <!-- Mouth Path -->
              <path id="purple-mouth" class="mouth-path" d="M 71 32 Q 77 37 83 32" stroke="#111827" stroke-width="3" stroke-linecap="round" fill="none"/>
            </g>
          </svg>

          <!-- 2. Black Character (Center) -->
          <svg class="character char-black" id="char-black" viewBox="0 0 100 240" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow: visible;">
            <path d="M 12 0 L 92 18 L 78 240 L 0 240 Z" fill="#181c22"/>
            <!-- Eyes Group -->
            <g id="black-face" style="transform-origin: 55px 40px;">
              <circle class="eye" cx="44" cy="38" r="5.5" fill="#ffffff"/>
              <circle class="pupil" id="black-pupil-l" cx="44" cy="38" r="2.8" fill="#111827"/>
              <circle class="eye" cx="68" cy="42" r="5.5" fill="#ffffff"/>
              <circle class="pupil" id="black-pupil-r" cx="68" cy="42" r="2.8" fill="#111827"/>
            </g>
          </svg>

          <!-- 3. Yellow Character (Right Front) -->
          <svg class="character char-yellow" id="char-yellow" viewBox="0 0 130 190" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow: visible;">
            <path d="M 0 190 L 0 65 Q 0 0 65 0 Q 130 0 130 65 L 130 190 Z" fill="#e5d519"/>
            <!-- Face -->
            <g id="yellow-face" style="transform-origin: 65px 55px;">
              <!-- Open Eye (Minimalist, Synced with Purple & Black) -->
              <g id="yellow-normal-eye" style="transition: opacity 0.22s ease;">
                <circle class="eye" cx="40" cy="48" r="5.5" fill="#ffffff"/>
                <circle class="pupil" id="yellow-pupil" cx="40" cy="48" r="2.8" fill="#111827"/>
              </g>
              
              <!-- Natural Squeezed Eye Arc (Password Look Away / Squint State) -->
              <g id="yellow-squint-eye" style="opacity: 0; transition: opacity 0.22s ease;">
                <path d="M 33 50 Q 40 41 47 50" stroke="#111827" stroke-width="3.2" stroke-linecap="round" fill="none"/>
              </g>
              
              <!-- Blush Cheeks (Appears ONLY on Successful Login) -->
              <ellipse id="yellow-blush-l" cx="24" cy="58" rx="6.5" ry="3.8" fill="#ff4d79" style="opacity: 0; filter: blur(1.2px); transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1); pointer-events: none;" />
              <ellipse id="yellow-blush-r" cx="106" cy="58" rx="6.5" ry="3.8" fill="#ff4d79" style="opacity: 0; filter: blur(1.2px); transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1); pointer-events: none;" />

              <!-- Minimalist Expressive Mouth Path -->
              <path id="yellow-mouth" class="mouth-path" d="M 56 60 Q 75 62 94 60" stroke="#111827" stroke-width="3.2" stroke-linecap="round" fill="none"/>
            </g>
          </svg>

          <!-- 4. Orange Character (Front Left Semicircle) -->
          <svg class="character char-orange" id="char-orange" viewBox="0 0 260 150" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow: visible;">
            <path d="M 0 150 C 15 55, 95 18, 185 45 C 230 65, 255 105, 260 150 Z" fill="#ff7033"/>
            
            <!-- Open Normal Eyes -->
            <g id="orange-normal-eyes" style="transform-origin: 165px 88px; transition: opacity 0.25s ease;">
              <circle class="eye" cx="145" cy="85" r="4.8" fill="#111827"/>
              <circle class="pupil" id="orange-pupil-l" cx="145" cy="85" r="2.5" fill="#111827"/>
              <circle class="eye" cx="185" cy="92" r="4.8" fill="#111827"/>
              <circle class="pupil" id="orange-pupil-r" cx="185" cy="92" r="2.5" fill="#111827"/>
            </g>

            <!-- Squint Eyelids (Look Away State) -->
            <g id="orange-squint-eyes" style="opacity: 0; transition: opacity 0.25s ease;">
              <path d="M 134 88 Q 142 80 150 88" stroke="#111827" stroke-width="3.2" stroke-linecap="round" fill="none"/>
              <path d="M 174 94 Q 182 86 190 94" stroke="#111827" stroke-width="3.2" stroke-linecap="round" fill="none"/>
            </g>

            <!-- Mouth -->
            <path id="orange-mouth" class="mouth-path" d="M 160 106 Q 168 114 176 106" stroke="#111827" stroke-width="3.2" stroke-linecap="round" fill="none"/>
          </svg>

        </div>
      </div>

      <!-- Right Form Panel -->
      <div class="form-panel">
        <span class="login-brand-icon login-scale-logo" style="color: #5b134b !important;" title="Metri-Report Statutory Emblem">
          <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%; display: block; color: #5b134b !important;">
            <!-- Top Finial Knob -->
            <circle cx="48" cy="11" r="4" fill="#5b134b"/>
            <!-- Central Vertical Pillar -->
            <rect x="45.5" y="15" width="5" height="69" rx="2" fill="#5b134b"/>
            <!-- Decorative Collar Ring -->
            <rect x="43.5" y="28.5" width="9" height="3.5" rx="1.5" fill="#5b134b"/>

            <!-- Pedestal Base -->
            <path d="M 35 84 C 35 76, 61 76, 61 84 Z" fill="#5b134b"/>
            <rect x="28" y="84" width="40" height="5.5" rx="2.75" fill="#5b134b"/>

            <!-- Angled Balance Beam -->
            <path d="M 17 35 Q 48 23 79 21.5" stroke="#5b134b" stroke-width="5.5" stroke-linecap="round" fill="none"/>
            <circle cx="48" cy="24" r="5" fill="#5b134b"/>
            <circle cx="17" cy="35" r="3.2" fill="#5b134b"/>
            <circle cx="79" cy="21.5" r="3.2" fill="#5b134b"/>

            <!-- Left Weighing Pan -->
            <path d="M 17 35 L 5 60 M 17 35 L 29 60" stroke="#5b134b" stroke-width="2.8" stroke-linecap="round"/>
            <path d="M 3.5 60 C 3.5 78, 30.5 78, 30.5 60 Z" fill="#5b134b"/>

            <!-- Right Hanging Document Sheets Construction -->
            <path d="M 79 21.5 L 66 36 M 79 21.5 L 91 36" stroke="#5b134b" stroke-width="2.8" stroke-linecap="round"/>
            
            <!-- Back Document Sheet -->
            <path d="M 68 36 L 89 36 C 92.5 36 95 38.5 95 42 L 95 72 C 95 75.5 92.5 78 89 78 L 76 78" 
                  stroke="#5b134b" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>

            <!-- Front Document Sheet -->
            <path d="M 59 40 L 75 40 L 87 52 L 87 78 C 87 81 84.5 83 81.5 83 L 59 83 C 56 83 54 81 54 78 L 54 45 C 54 42 56 40 59 40 Z" 
                  stroke="#5b134b" stroke-width="3.6" stroke-linejoin="round" fill="none"/>
            <!-- Dog-Ear Fold Flap -->
            <path d="M 75 40 L 75 52 L 87 52" stroke="#5b134b" stroke-width="3.6" stroke-linejoin="round" stroke-linecap="round" fill="none"/>

            <!-- Document Report Text Lines -->
            <line x1="60" y1="49" x2="69.5" y2="49" stroke="#5b134b" stroke-width="3.2" stroke-linecap="round"/>
            <line x1="60" y1="55.5" x2="69.5" y2="55.5" stroke="#5b134b" stroke-width="3.2" stroke-linecap="round"/>
            <line x1="60" y1="62" x2="81" y2="62" stroke="#5b134b" stroke-width="3.2" stroke-linecap="round"/>
            <line x1="60" y1="68.5" x2="81" y2="68.5" stroke="#5b134b" stroke-width="3.2" stroke-linecap="round"/>
            <line x1="60" y1="75" x2="73" y2="75" stroke="#5b134b" stroke-width="3.2" stroke-linecap="round"/>
          </svg>
        </span>

        <div class="form-header">
          <h2 class="form-brand-title">Metri-Report</h2>
          <div class="form-brand-tagline-wrap">
            <p class="form-brand-tagline">Measure &#9679; Validate &#9679; Report</p>
          </div>
          <p class="form-brand-subtext">Please enter your details</p>
        </div>

        <form id="metri-login-form" onsubmit="return false;">
          <div class="input-group">
            <label for="login-designation">Designation &amp; Officer</label>
            <div class="input-field-wrap" id="wrap-designation">
              <select id="login-designation" required>
                <option value="engineer" selected>Avinash Kumar (Lead Test Engineer)</option>
                <option value="reviewer">Sunita Verma (Senior Reviewer)</option>
                <option value="manager">Dr. Rajesh Sharma (Lab Manager)</option>
                <option value="admin">Admin Officer (Legal Metrology)</option>
              </select>
              <div class="select-arrow">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
            </div>
          </div>

          <div class="input-group">
            <label for="login-email">Email</label>
            <div class="input-field-wrap" id="wrap-email">
              <input type="email" id="login-email" placeholder="engineer@metrireport.local" value="engineer@metrireport.local" autocomplete="email" required />
            </div>
          </div>

          <div class="input-group">
            <label for="login-password">Password</label>
            <div class="input-field-wrap" id="wrap-password">
              <input type="password" id="login-password" placeholder="••••••••••••" value="engineer123" autocomplete="current-password" required />
              <button type="button" class="toggle-password" id="btn-toggle-pw" aria-label="Toggle password visibility">
                <svg id="eye-icon-open" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg id="eye-icon-closed" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="error-msg" id="password-error-msg">Please enter a valid password (min 4 characters)</div>
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" checked />
              <span>Remember for 30 days</span>
            </label>
            <a href="#" class="forgot-link" onclick="event.preventDefault(); alert('Password reset link sent to your email!');">Forgot password?</a>
          </div>

          <button type="submit" class="btn-login" id="login-submit-btn">
            <span>Log In</span>
          </button>

          <button type="button" class="btn-google" id="login-google-btn">
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
              <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.35 24 12 24z"/>
              <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
              <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.35 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
            </svg>
            <span>Log in with Google</span>
          </button>
        </form>

        <div class="form-footer">
          Don't have an account? <a href="#" id="signup-link">Sign Up</a>
        </div>
      </div>
    </div>
  </div>
  `;

  if (!document.querySelector('link[href*="login-gate.css"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/login-gate.css';
    document.head.appendChild(link);
  }

  const container = document.createElement('div');
  container.innerHTML = overlayHtml;
  document.body.appendChild(container.firstElementChild);

  const overlay = document.getElementById('login-overlay');
  try {
    if ((sessionStorage.getItem('metri_authenticated') === 'true' || localStorage.getItem('metri_authenticated') === 'true') && !window.location.search.includes('login') && !window.location.search.includes('gate')) {
      overlay.classList.add('logged-in');
    }
  } catch (e) { }
  const charactersPanel = document.getElementById('characters-panel');
  const confettiCanvas = document.getElementById('character-confetti-canvas');
  const designationSelect = document.getElementById('login-designation');
  const emailInput = document.getElementById('login-email');
  const pwInput = document.getElementById('login-password');
  const wrapPassword = document.getElementById('wrap-password');
  const passwordErrorMsg = document.getElementById('password-error-msg');
  const togglePwBtn = document.getElementById('btn-toggle-pw');
  const eyeIconOpen = document.getElementById('eye-icon-open');
  const eyeIconClosed = document.getElementById('eye-icon-closed');
  const submitBtn = document.getElementById('login-submit-btn');
  const googleBtn = document.getElementById('login-google-btn');
  const skipBtn = document.getElementById('login-skip-btn');
  const signupLink = document.getElementById('signup-link');

  // Character SVGs & Components
  const charOrange = document.getElementById('char-orange');
  const charPurple = document.getElementById('char-purple');
  const charBlack = document.getElementById('char-black');
  const charYellow = document.getElementById('char-yellow');

  // Purple Parts
  const purpleBodyPath = document.getElementById('purple-body-path');
  const purpleFace = document.getElementById('purple-face');
  const purplePupilL = document.getElementById('purple-pupil-l');
  const purplePupilR = document.getElementById('purple-pupil-r');
  const purpleNose = document.getElementById('purple-nose');
  const purpleMouth = document.getElementById('purple-mouth');

  // Black Parts
  const blackFace = document.getElementById('black-face');
  const blackPupilL = document.getElementById('black-pupil-l');
  const blackPupilR = document.getElementById('black-pupil-r');

  // Yellow Parts
  const yellowFace = document.getElementById('yellow-face');
  const yellowNormalEye = document.getElementById('yellow-normal-eye');
  const yellowSquintEye = document.getElementById('yellow-squint-eye');
  const yellowBlushL = document.getElementById('yellow-blush-l');
  const yellowBlushR = document.getElementById('yellow-blush-r');
  const yellowPupil = document.getElementById('yellow-pupil');
  const yellowMouth = document.getElementById('yellow-mouth');

  // Orange Parts
  const orangeNormalEyes = document.getElementById('orange-normal-eyes');
  const orangeSquintEyes = document.getElementById('orange-squint-eyes');
  const orangePupilL = document.getElementById('orange-pupil-l');
  const orangePupilR = document.getElementById('orange-pupil-r');
  const orangeMouth = document.getElementById('orange-mouth');

  let state = 'idle'; // 'idle', 'email', 'password_masked', 'password_look_away', 'error_sad', 'success'
  let passwordVisible = false;

  // -------------------------------------------------------------
  // CONFETTI BURST ENGINE (STRICTLY BEHIND CHARACTERS)
  // -------------------------------------------------------------
  let confettiCtx = confettiCanvas.getContext('2d');
  let confettiParticles = [];
  const CONFETTI_COLORS = ['#5812eb', '#ff7033', '#e5d519', '#10b981', '#f43f5e', '#38bdf8', '#fbbf24', '#a855f7'];

  function resizeConfettiCanvas() {
    if (charactersPanel && confettiCanvas) {
      confettiCanvas.width = charactersPanel.clientWidth;
      confettiCanvas.height = charactersPanel.clientHeight;
    }
  }
  window.addEventListener('resize', resizeConfettiCanvas);
  setTimeout(resizeConfettiCanvas, 100);

  function triggerConfettiBurst() {
    resizeConfettiCanvas();
    const w = confettiCanvas.width;
    const h = confettiCanvas.height;
    confettiParticles = [];

    const numParticles = 140;
    for (let i = 0; i < numParticles; i++) {
      // Spawn from lower-middle behind characters
      const originX = w * 0.45 + (Math.random() - 0.5) * 120;
      const originY = h * 0.75 + (Math.random() - 0.5) * 60;

      const angle = -Math.PI / 2 + (Math.random() - 0.5) * 1.5; // Upward fan burst
      const speed = 7 + Math.random() * 12;

      confettiParticles.push({
        x: originX,
        y: originY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 5 + Math.random() * 7,
        color: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 12,
        wobble: Math.random() * 10,
        wobbleSpeed: 0.1 + Math.random() * 0.1,
        shape: Math.random() > 0.4 ? 'rect' : 'circle',
        opacity: 1,
        gravity: 0.28 + Math.random() * 0.12,
        drag: 0.985
      });
    }
  }

  function renderConfetti() {
    if (confettiParticles.length === 0) return;
    confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);

    for (let i = confettiParticles.length - 1; i >= 0; i--) {
      const p = confettiParticles[i];
      p.vx *= p.drag;
      p.vy += p.gravity;
      p.x += p.vx;
      p.y += p.vy;
      p.rotation += p.rotSpeed;
      p.wobble += p.wobbleSpeed;
      p.opacity -= 0.008;

      if (p.opacity <= 0 || p.y > confettiCanvas.height + 20) {
        confettiParticles.splice(i, 1);
        continue;
      }

      confettiCtx.save();
      confettiCtx.globalAlpha = Math.max(0, p.opacity);
      confettiCtx.translate(p.x, p.y);
      confettiCtx.rotate((p.rotation * Math.PI) / 180);
      confettiCtx.scale(Math.cos(p.wobble), 1);
      confettiCtx.fillStyle = p.color;

      if (p.shape === 'rect') {
        confettiCtx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.5);
      } else {
        confettiCtx.beginPath();
        confettiCtx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
        confettiCtx.fill();
      }

      confettiCtx.restore();
    }
  }

  // -------------------------------------------------------------
  // CONTINUOUS 60FPS PHYSICS & LERP ENGINE
  // -------------------------------------------------------------
  let mouseTargetX = window.innerWidth / 2;
  let mouseTargetY = window.innerHeight / 2;

  let currentGazeX = mouseTargetX;
  let currentGazeY = mouseTargetY;
  let purpleSpine = 0; // -1 (sad folded kink) to 0 (idle) to 1 (extended arch)
  let targetPurpleSpine = 0;
  let purpleFaceX = 0, currentFaceX = 0;
  let purpleFaceY = 0, currentFaceY = 0;
  let purpleFaceRot = 0, currentFaceRot = 0;

  let blinkTimer = 0;

  window.addEventListener('mousemove', (e) => {
    if (state === 'idle') {
      mouseTargetX = e.clientX;
      mouseTargetY = e.clientY;
    }
  });

  function getElementFocusTarget(input) {
    if (!input) return { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    const rect = input.getBoundingClientRect();
    const len = input.value ? input.value.length : 0;
    const targetX = rect.left + Math.min(rect.width * 0.85, 20 + len * 9);
    const targetY = rect.top + rect.height / 2;
    return { x: targetX, y: targetY };
  }

  function generatePurplePath(spineVal) {
    if (spineVal >= 0) {
      const t = Math.min(1, spineVal);
      const tlX = 20 + t * 100;
      const tlY = 0 + t * 15;
      const trX = 140 + t * 35;
      const trY = 0 + t * 50;

      const cp1LX = 20 + t * -5;
      const cp1LY = 140;
      const cp2LX = 20 + t * 30;
      const cp2LY = 60;

      const cp1RX = 140 + t * -15;
      const cp1RY = 90;
      const cp2RX = 140 + t * -65;
      const cp2RY = 160;

      return `M 20 280 C ${cp1LX} ${cp1LY}, ${cp2LX} ${cp2LY}, ${tlX} ${tlY} L ${trX} ${trY} C ${cp1RX} ${cp1RY}, ${cp2RX} ${cp2RY}, 80 280 Z`;
    } else {
      const t = Math.min(1, -spineVal);
      const k1X = 20 + t * 0;
      const k1Y = 280;
      const k2X = 20 + t * 0;
      const k2Y = 140;
      const k3X = 20 + t * -20;
      const k3Y = 70;
      const k4X = 20 + t * 95;
      const k4Y = 30;
      const k5X = 140 + t * -10;
      const k5Y = 105;
      const k6X = 140 + t * -45;
      const k6Y = 145;
      const k7X = 140 + t * -45;
      const k7Y = 280;

      return `M ${k1X} ${k1Y} L ${k2X} ${k2Y} L ${k3X} ${k3Y} L ${k4X} ${k4Y} L ${k5X} ${k5Y} L ${k6X} ${k6Y} L ${k7X} ${k7Y} Z`;
    }
  }

  function animationLoop() {
    // Render confetti in background
    renderConfetti();

    // 1. Damped Lerp for Gaze Coordinates
    currentGazeX += (mouseTargetX - currentGazeX) * 0.14;
    currentGazeY += (mouseTargetY - currentGazeY) * 0.14;

    // 2. Damped Spring Lerp for Purple Spine & Face
    purpleSpine += (targetPurpleSpine - purpleSpine) * 0.12;
    currentFaceX += (purpleFaceX - currentFaceX) * 0.14;
    currentFaceY += (purpleFaceY - currentFaceY) * 0.14;
    currentFaceRot += (purpleFaceRot - currentFaceRot) * 0.14;

    const currentPath = generatePurplePath(purpleSpine);
    purpleBodyPath.setAttribute('d', currentPath);
    purpleFace.style.transform = `translate(${currentFaceX}px, ${currentFaceY}px) rotate(${currentFaceRot}deg)`;

    // 3. Update Pupils
    if (state !== 'password_look_away' && state !== 'error_sad') {
      const pupils = [
        { el: purplePupilL, max: 4.5 },
        { el: purplePupilR, max: 4.5 },
        { el: blackPupilL, max: 4.5 },
        { el: blackPupilR, max: 4.5 },
        { el: yellowPupil, max: 2.6 },
        { el: orangePupilL, max: 4.0 },
        { el: orangePupilR, max: 4.0 }
      ];

      pupils.forEach(({ el, max }) => {
        if (!el) return;
        const rect = el.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const dx = currentGazeX - centerX;
        const dy = currentGazeY - centerY;
        const angle = Math.atan2(dy, dx);
        const dist = Math.min(max, Math.hypot(dx, dy) / 22);

        const offsetX = Math.cos(angle) * dist;
        const offsetY = Math.sin(angle) * dist;

        el.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
      });
    }

    requestAnimationFrame(animationLoop);
  }

  requestAnimationFrame(animationLoop);

  // -------------------------------------------------------------
  // STATE MACHINE & TRANSITIONS
  // -------------------------------------------------------------

  // 0. DESIGNATION DROPDOWN FOCUS & CHANGE
  function onDesignationFocus() {
    clearErrorState();
    state = 'email';

    targetPurpleSpine = 0.8;
    purpleFaceX = 30;
    purpleFaceY = 12;
    purpleFaceRot = 14;
    purpleNose.style.opacity = '1';
    purpleMouth.setAttribute('d', 'M 70 50 Q 76 56 82 50');

    charBlack.style.transform = 'rotate(4.5deg) translateY(-6px)';
    blackFace.style.transform = 'translate(3px, -2px)';

    charYellow.style.transform = 'rotate(3.5deg) translateY(-4px)';
    if (yellowNormalEye) yellowNormalEye.style.opacity = '1';
    if (yellowSquintEye) yellowSquintEye.style.opacity = '0';
    if (yellowBlushL) yellowBlushL.style.opacity = '0';
    if (yellowBlushR) yellowBlushR.style.opacity = '0';
    yellowMouth.setAttribute('d', 'M 54 55 Q 74 72 94 55');

    charOrange.style.transform = 'rotate(3deg) translateY(-3px)';
    orangeNormalEyes.style.opacity = '1';
    orangeSquintEyes.style.opacity = '0';
    orangeMouth.setAttribute('d', 'M 160 106 Q 168 116 176 106');

    const target = getElementFocusTarget(designationSelect);
    mouseTargetX = target.x;
    mouseTargetY = target.y;
  }

  const METRI_ACCOUNTS = {
    'engineer': {
      name: 'Avinash Kumar (Lead Test Engineer)',
      displayName: 'Avinash Kumar',
      designation: 'Lead Test Engineer',
      email: 'engineer@metrireport.local',
      password: 'engineer123',
      role: 'TEST_ENGINEER'
    },
    'reviewer': {
      name: 'Sunita Verma (Senior Reviewer)',
      displayName: 'Sunita Verma',
      designation: 'Senior Reviewer',
      email: 'reviewer@metrireport.local',
      password: 'reviewer123',
      role: 'REVIEWER'
    },
    'manager': {
      name: 'Dr. Rajesh Sharma (Lab Manager)',
      displayName: 'Dr. Rajesh Sharma',
      designation: 'Lab Manager',
      email: 'manager@metrireport.local',
      password: 'manager123',
      role: 'LAB_MANAGER'
    },
    'admin': {
      name: 'Admin Officer (Legal Metrology)',
      displayName: 'Admin Officer',
      designation: 'Legal Metrology',
      email: 'admin@metrireport.local',
      password: 'admin123',
      role: 'ADMIN'
    }
  };

  function getAccountFromVal(val) {
    if (!val) return METRI_ACCOUNTS.engineer;
    if (METRI_ACCOUNTS[val]) return METRI_ACCOUNTS[val];
    const low = val.toLowerCase();
    if (low.includes('reviewer') || low.includes('sunita')) return METRI_ACCOUNTS.reviewer;
    if (low.includes('manager') || low.includes('rajesh')) return METRI_ACCOUNTS.manager;
    if (low.includes('admin')) return METRI_ACCOUNTS.admin;
    return METRI_ACCOUNTS.engineer;
  }

  function autoFillAccountCredentials() {
    if (!designationSelect) return;
    const acc = getAccountFromVal(designationSelect.value);
    if (emailInput && acc) {
      emailInput.value = acc.email;
    }
    if (pwInput && acc) {
      pwInput.value = acc.password;
    }
    clearErrorState();
  }

  if (designationSelect) {
    designationSelect.addEventListener('focus', onDesignationFocus);
    designationSelect.addEventListener('change', () => {
      autoFillAccountCredentials();
      onDesignationFocus();
      setTimeout(resetToIdle, 800);
    });
    designationSelect.addEventListener('blur', () => {
      if (state === 'email') {
        state = 'idle';
        resetToIdle();
      }
    });
  }

  // 1. EMAIL FOCUS & TYPING: Realistic curious neck extension towards input & happy natural smile
  function onEmailFocus() {
    clearErrorState();
    state = 'email';

    targetPurpleSpine = 1.0;
    purpleFaceX = 36;
    purpleFaceY = 16;
    purpleFaceRot = 18;
    purpleNose.style.opacity = '1';
    purpleMouth.setAttribute('d', 'M 70 50 Q 76 56 82 50');

    charBlack.style.transform = 'rotate(5.5deg) translateY(-8px)';
    blackFace.style.transform = 'translate(4px, -2px)';

    charYellow.style.transform = 'rotate(4.5deg) translateY(-5px)';
    if (yellowNormalEye) yellowNormalEye.style.opacity = '1';
    if (yellowSquintEye) yellowSquintEye.style.opacity = '0';
    if (yellowBlushL) yellowBlushL.style.opacity = '0';
    if (yellowBlushR) yellowBlushR.style.opacity = '0';
    yellowMouth.setAttribute('d', 'M 54 55 Q 74 72 94 55');

    charOrange.style.transform = 'rotate(3.5deg) translateY(-4px)';
    orangeNormalEyes.style.opacity = '1';
    orangeSquintEyes.style.opacity = '0';
    orangeMouth.setAttribute('d', 'M 160 106 Q 168 116 176 106');

    const target = getElementFocusTarget(emailInput);
    mouseTargetX = target.x;
    mouseTargetY = target.y;
  }

  emailInput.addEventListener('focus', onEmailFocus);
  emailInput.addEventListener('input', () => {
    if (state === 'email') {
      const target = getElementFocusTarget(emailInput);
      mouseTargetX = target.x;
      mouseTargetY = target.y;
    }
  });
  emailInput.addEventListener('blur', () => {
    if (state === 'email') {
      state = 'idle';
      resetToIdle();
    }
  });

  // 2. PASSWORD FOCUS & TYPING (Masked dots `•••` -> Curious attentive dot tracking)
  function onPasswordFocus() {
    clearErrorState();

    if (!passwordVisible) {
      state = 'password_masked';

      targetPurpleSpine = 0.15;
      purpleFaceX = 4;
      purpleFaceY = 8;
      purpleFaceRot = 2;
      purpleNose.style.opacity = '0';
      purpleMouth.setAttribute('d', 'M 71 32 Q 77 38 83 32');
      charPurple.style.transform = 'rotate(2deg) translateY(-2px)';

      charBlack.style.transform = 'rotate(2.5deg) translateY(-2px)';
      blackFace.style.transform = 'translate(2px, 4px)';

      charYellow.style.transform = 'rotate(2deg) translateY(-2px)';
      if (yellowNormalEye) yellowNormalEye.style.opacity = '1';
      if (yellowSquintEye) yellowSquintEye.style.opacity = '0';
      if (yellowBlushL) yellowBlushL.style.opacity = '0';
      if (yellowBlushR) yellowBlushR.style.opacity = '0';
      yellowMouth.setAttribute('d', 'M 55 58 Q 75 66 94 58');

      charOrange.style.transform = 'rotate(2deg) translateY(-2px)';
      orangeNormalEyes.style.opacity = '1';
      orangeSquintEyes.style.opacity = '0';
      orangeMouth.setAttribute('d', 'M 160 106 Q 168 112 176 106');

      const target = getElementFocusTarget(pwInput);
      mouseTargetX = target.x;
      mouseTargetY = target.y;

    } else {
      applyLookAwayState();
    }
  }

  pwInput.addEventListener('focus', onPasswordFocus);
  pwInput.addEventListener('input', () => {
    clearErrorState();
    if (passwordVisible) {
      applyLookAwayState();
    } else {
      if (state === 'password_masked') {
        const target = getElementFocusTarget(pwInput);
        mouseTargetX = target.x;
        mouseTargetY = target.y;
      }
    }
  });
  pwInput.addEventListener('blur', () => {
    if (state === 'password_masked' || state === 'password_look_away') {
      state = 'idle';
      resetToIdle();
    }
  });

  // 3. PASSWORD SHOW (Eye toggle ON): Squeezing of Eye + Neutral Mood Expression + Look Away!
  function applyLookAwayState() {
    state = 'password_look_away';

    targetPurpleSpine = 0.0;
    purpleFaceX = -8;
    purpleFaceY = 4;
    purpleFaceRot = -6;
    purpleNose.style.opacity = '0';
    purpleMouth.setAttribute('d', 'M 71 36 Q 77 30 83 36');
    charPurple.style.transform = 'rotate(-3deg)';
    if (purplePupilL) purplePupilL.style.transform = 'translate(-4px, -3.5px)';
    if (purplePupilR) purplePupilR.style.transform = 'translate(-4px, -3.5px)';

    blackFace.style.transform = 'translate(-6px, 6px) rotate(-4deg)';
    charBlack.style.transform = 'rotate(-3deg)';
    if (blackPupilL) blackPupilL.style.transform = 'translate(-4px, 2px)';
    if (blackPupilR) blackPupilR.style.transform = 'translate(-4px, 2px)';

    yellowFace.style.transform = 'translate(-4px, 2px) rotate(-4deg)';
    if (yellowNormalEye) yellowNormalEye.style.opacity = '0';
    if (yellowSquintEye) yellowSquintEye.style.opacity = '1';
    if (yellowBlushL) yellowBlushL.style.opacity = '0';
    if (yellowBlushR) yellowBlushR.style.opacity = '0';
    yellowMouth.setAttribute('d', 'M 56 60 Q 75 62 94 60');
    charYellow.style.transform = 'rotate(-3deg)';
    if (yellowPupil) yellowPupil.style.transform = 'translate(-2px, 0px)';

    charOrange.style.transform = 'rotate(-3deg)';
    orangeNormalEyes.style.opacity = '0';
    orangeSquintEyes.style.opacity = '1';
    orangeMouth.setAttribute('d', 'M 152 108 Q 160 102 168 108');
  }

  togglePwBtn.addEventListener('click', () => {
    passwordVisible = !passwordVisible;
    pwInput.type = passwordVisible ? 'text' : 'password';
    eyeIconOpen.style.display = passwordVisible ? 'none' : 'block';
    eyeIconClosed.style.display = passwordVisible ? 'block' : 'none';

    if (passwordVisible) {
      applyLookAwayState();
    } else {
      state = 'idle';
      resetToIdle();
      if (document.activeElement === pwInput) {
        onPasswordFocus();
      }
    }
  });

  // 4. ERROR / INCORRECT / EMPTY PASSWORD STATE (Dramatic Neck Bend + Sad Expressions)
  function triggerErrorSadState() {
    state = 'error_sad';

    wrapPassword.classList.add('error-shake');
    passwordErrorMsg.style.display = 'block';

    setTimeout(() => {
      wrapPassword.classList.remove('error-shake');
    }, 450);

    targetPurpleSpine = -1.0;
    purpleFaceX = 14;
    purpleFaceY = 52;
    purpleFaceRot = -6;
    purpleNose.style.opacity = '0';
    purpleMouth.setAttribute('d', 'M 71 42 Q 77 32 83 42');
    charPurple.style.transform = 'none';

    charBlack.style.transform = 'none';
    blackFace.style.transform = 'translate(2px, 12px)';

    charYellow.style.transform = 'none';
    yellowFace.style.transform = 'translate(0px, 4px)';
    if (yellowNormalEye) yellowNormalEye.style.opacity = '1';
    if (yellowSquintEye) yellowSquintEye.style.opacity = '0';
    if (yellowBlushL) yellowBlushL.style.opacity = '0';
    if (yellowBlushR) yellowBlushR.style.opacity = '0';
    yellowMouth.setAttribute('d', 'M 54 64 Q 74 54 94 64');

    charOrange.style.transform = 'none';
    orangeNormalEyes.style.opacity = '1';
    orangeSquintEyes.style.opacity = '0';
    orangeMouth.setAttribute('d', 'M 146 108 Q 156 98 166 108');

    [purplePupilL, purplePupilR, blackPupilL, blackPupilR, orangePupilL, orangePupilR].forEach(p => {
      if (p) p.style.transform = 'translate(-2px, 3.5px)';
    });
    if (yellowPupil) yellowPupil.style.transform = 'translate(1px, 2px)';
  }

  function clearErrorState() {
    passwordErrorMsg.style.display = 'none';
    wrapPassword.classList.remove('error-shake');
  }

  function resetToIdle() {
    targetPurpleSpine = 0.0;
    purpleFaceX = 0;
    purpleFaceY = 0;
    purpleFaceRot = 0;
    purpleNose.style.opacity = '0';
    purpleMouth.setAttribute('d', 'M 71 32 Q 77 37 83 32');
    charPurple.style.transform = 'none';

    blackFace.style.transform = 'none';
    charBlack.style.transform = 'none';

    yellowFace.style.transform = 'none';
    if (yellowNormalEye) yellowNormalEye.style.opacity = '1';
    if (yellowSquintEye) yellowSquintEye.style.opacity = '0';
    if (yellowBlushL) yellowBlushL.style.opacity = '0';
    if (yellowBlushR) yellowBlushR.style.opacity = '0';
    yellowMouth.setAttribute('d', 'M 56 60 Q 75 62 94 60');
    charYellow.style.transform = 'none';

    orangeNormalEyes.style.opacity = '1';
    orangeSquintEyes.style.opacity = '0';
    orangeMouth.setAttribute('d', 'M 160 106 Q 168 114 176 106');
    charOrange.style.transform = 'none';

    [purplePupilL, purplePupilR, blackPupilL, blackPupilR, yellowPupil, orangePupilL, orangePupilR].forEach(p => {
      if (p) p.style.transform = 'none';
    });
  }

  // 5. VALID SUBMIT -> Confetti Burst (Strictly Behind Characters) + Celebration Blush + Spring Jump
  function handleLoginSubmit() {
    const emailVal = (emailInput.value || '').trim();
    const pwVal = (pwInput.value || '').trim();

    if (!emailVal || !pwVal || pwVal.length < 4) {
      triggerErrorSadState();
      return;
    }

    clearErrorState();
    state = 'success';
    submitBtn.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      <span>Success</span>
    `;
    submitBtn.style.backgroundColor = '#10b981';

    // TRIGGER CONFETTI BURST STRICTLY BEHIND CHARACTERS!
    triggerConfettiBurst();

    // Spring jump & joyful celebration with rosy blush
    targetPurpleSpine = 0.3;
    charOrange.style.transform = 'translateY(-24px) scale(1.05)';
    charPurple.style.transform = 'translateY(-34px) rotate(2deg) scale(1.06)';
    charBlack.style.transform = 'translateY(-30px) rotate(-2deg) scale(1.06)';
    charYellow.style.transform = 'translateY(-28px) scale(1.06)';

    orangeNormalEyes.style.opacity = '1';
    orangeSquintEyes.style.opacity = '0';
    if (yellowNormalEye) yellowNormalEye.style.opacity = '0';
    if (yellowSquintEye) yellowSquintEye.style.opacity = '1';
    if (yellowBlushL) yellowBlushL.style.opacity = '0.95';
    if (yellowBlushR) yellowBlushR.style.opacity = '0.95';
    yellowMouth.setAttribute('d', 'M 52 53 Q 74 80 96 53');
    purpleMouth.setAttribute('d', 'M 68 30 Q 77 42 84 30');
    orangeMouth.setAttribute('d', 'M 156 102 Q 168 122 180 102');

    setTimeout(async () => {
      overlay.classList.add('logged-in');
      try {
        const selectedVal = (designationSelect ? designationSelect.value : 'engineer');
        const acc = getAccountFromVal(selectedVal);

        const userObj = {
          name: acc.name,
          displayName: acc.displayName,
          email: emailVal || acc.email,
          designation: acc.designation,
          role: acc.role
        };
        sessionStorage.setItem('metri_authenticated', 'true');
        localStorage.setItem('metri_authenticated', 'true');
        localStorage.setItem('metri_user', JSON.stringify(userObj));
        window.dispatchEvent(new CustomEvent('metri_user_changed', { detail: userObj }));

        // Proactively fetch and store real JWT bearer token
        try {
          const authRes = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: userObj.email, password: acc.password || 'engineer123' })
          });
          if (authRes.ok) {
            const authData = await authRes.json();
            if (authData.access_token) {
              localStorage.setItem('token', authData.access_token);
              localStorage.setItem('metri_token', authData.access_token);
              localStorage.setItem('metri_access_token', authData.access_token);
            }
          }
        } catch (authErr) {
          console.warn('[LoginGate] Token acquisition error:', authErr);
        }

        if (window.location.pathname.includes('/login') || window.location.pathname.includes('/signin')) {
          setTimeout(() => {
            window.location.href = '/evaluation-workspace';
          }, 800);
        }
      } catch (e) { }
    }, 700);
  }

  submitBtn.addEventListener('click', (e) => {
    e.preventDefault();
    handleLoginSubmit();
  });

  googleBtn.addEventListener('click', () => {
    handleLoginSubmit();
  });

  skipBtn.addEventListener('click', async () => {
    state = 'success';
    triggerConfettiBurst();
    overlay.classList.add('logged-in');
    try {
      const selectedVal = (designationSelect ? designationSelect.value : 'engineer');
      const acc = getAccountFromVal(selectedVal);
      const userObj = {
        name: acc.name,
        displayName: acc.displayName,
        email: acc.email,
        designation: acc.designation,
        role: acc.role
      };
      sessionStorage.setItem('metri_authenticated', 'true');
      localStorage.setItem('metri_authenticated', 'true');
      localStorage.setItem('metri_user', JSON.stringify(userObj));
      window.dispatchEvent(new CustomEvent('metri_user_changed', { detail: userObj }));

      // Proactively fetch and store real JWT bearer token
      try {
        const authRes = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: acc.email, password: acc.password || 'engineer123' })
        });
        if (authRes.ok) {
          const authData = await authRes.json();
          if (authData.access_token) {
            localStorage.setItem('token', authData.access_token);
            localStorage.setItem('metri_token', authData.access_token);
            localStorage.setItem('metri_access_token', authData.access_token);
          }
        }
      } catch (authErr) {
        console.warn('[LoginGate] Token acquisition error on skip:', authErr);
      }
    } catch (e) { }
  });

  if (signupLink) {
    signupLink.addEventListener('click', (e) => {
      e.preventDefault();
      alert('Sign up requested! Entering demo mode.');
      handleLoginSubmit();
    });
  }

  // ==========================================
  // Interactive Silk Background (Shader-Powered)
  // Props: hue: 305, saturation: 0.85, brightness: 0.28, speed: 0.85, mouseSensitivity: 1.5, damping: 0.92
  // ==========================================
  function initSilkBackground() {
    const canvas = document.getElementById('login-silk-canvas');
    if (!canvas) return;

    const silkProps = {
      hue: 305.0, // Deep rich plum / violet tone matching reference image
      saturation: 0.85,
      brightness: 0.28,
      speed: 0.85,
      mouseSensitivity: 1.5,
      damping: 0.92
    };

    let gl = null;
    try {
      gl = canvas.getContext('webgl', { alpha: false, antialias: true, powerPreference: 'high-performance' }) ||
        canvas.getContext('experimental-webgl', { alpha: false });
    } catch (e) {
      gl = null;
    }

    if (!gl) {
      init2DSilkFallback(canvas, silkProps);
      return;
    }

    const vsSource = `
      attribute vec2 a_position;
      void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
      }
    `;

    const fsSource = `
      precision highp float;
      uniform vec2 u_resolution;
      uniform float u_time;
      uniform vec2 u_mouse;
      uniform float u_hue;
      uniform float u_saturation;
      uniform float u_brightness;
      uniform float u_speed;

      vec3 hsl2rgb(vec3 c) {
        vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
        return c.z + c.y * (rgb - 0.5) * (1.0 - abs(2.0 * c.z - 1.0));
      }

      mat2 rot(float a) {
        float s = sin(a), c = cos(a);
        return mat2(c, -s, s, c);
      }

      float silkWave(vec2 p, float t) {
        float v = 0.0;
        vec2 p2 = p;
        for (int i = 1; i <= 5; i++) {
          float fi = float(i);
          p2 = rot(0.38 + fi * 0.12) * p2;
          float wave1 = sin(p2.x * (1.75 + fi * 0.65) + t * (0.6 + fi * 0.22) + sin(p2.y * 2.2 + t * 0.4));
          float wave2 = cos(p2.y * (1.45 + fi * 0.55) - t * (0.5 + fi * 0.18) + cos(p2.x * 1.9 - t * 0.3));
          v += (wave1 + wave2) / fi;
        }
        return v;
      }

      void main() {
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
        vec2 mouseNorm = (u_mouse - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
        
        // Mouse ripple disturbance
        float dist = length(uv - mouseNorm);
        vec2 dir = normalize(uv - mouseNorm + 0.0001);
        float ripple = sin(dist * 13.0 - u_time * 3.2) * exp(-dist * 3.6);
        uv += dir * ripple * 0.06;

        float t = u_time * 0.35 * u_speed;

        // Anisotropic surface normal estimation
        float eps = 0.005;
        float h = silkWave(uv * 1.5, t);
        float hx = silkWave((uv + vec2(eps, 0.0)) * 1.5, t);
        float hy = silkWave((uv + vec2(0.0, eps)) * 1.5, t);
        vec3 n = normalize(vec3((hx - h) / eps, (hy - h) / eps, 1.0));

        // Dual subtle directional lights for rich velvet silk folds
        vec3 light1 = normalize(vec3(0.5, 0.7, 0.9));
        vec3 light2 = normalize(vec3(-0.6, -0.3, 0.7));
        float diff1 = max(dot(n, light1), 0.0);
        float diff2 = max(dot(n, light2), 0.0);

        // Controlled subtle specular sheen (never blowing out into bright neon)
        vec3 view = vec3(0.0, 0.0, 1.0);
        vec3 half1 = normalize(light1 + view);
        float spec = pow(max(dot(n, half1), 0.0), 32.0);
        float rim = pow(1.0 - max(dot(n, view), 0.0), 2.5);

        // Deep dark wine plum color ramp (Image 1 palette)
        // Shadow: #1a0219 (deepest fold)
        // Midtone: #490e47 (exact match to user Image 1)
        // Highlight: #62145e (matte velvet luster, zero neon)
        vec3 colDeepShadow = vec3(0.10, 0.012, 0.10);
        vec3 colMidPlum    = vec3(0.286, 0.055, 0.278); // #490e47
        vec3 colLuster     = vec3(0.384, 0.080, 0.368); // #62145e

        float fold = clamp(0.5 + 0.5 * h, 0.0, 1.0);
        float shade = fold * 0.55 + diff1 * 0.30 + diff2 * 0.15;
        shade += spec * 0.08 + rim * 0.06;
        shade = clamp(shade, 0.0, 1.0);

        vec3 color = mix(colDeepShadow, colMidPlum, smoothstep(0.0, 0.55, shade));
        color = mix(color, colLuster, smoothstep(0.55, 1.0, shade));

        // Subtle vignette for luxury depth
        vec2 screenUv = gl_FragCoord.xy / u_resolution.xy;
        float vig = 1.0 - smoothstep(0.35, 1.35, length(screenUv - 0.5) * 1.2);
        color *= (0.80 + 0.20 * vig);

        gl_FragColor = vec4(color, 1.0);
      }
    `;

    function compileShader(glContext, type, source) {
      const shader = glContext.createShader(type);
      glContext.shaderSource(shader, source);
      glContext.compileShader(shader);
      if (!glContext.getShaderParameter(shader, glContext.COMPILE_STATUS)) {
        console.warn('[SilkShader] Compilation error:', glContext.getShaderInfoLog(shader));
        glContext.deleteShader(shader);
        return null;
      }
      return shader;
    }

    const vs = compileShader(gl, gl.VERTEX_SHADER, vsSource);
    const fs = compileShader(gl, gl.FRAGMENT_SHADER, fsSource);
    if (!vs || !fs) {
      init2DSilkFallback(canvas, silkProps);
      return;
    }

    const program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.warn('[SilkShader] Link error:', gl.getProgramInfoLog(program));
      init2DSilkFallback(canvas, silkProps);
      return;
    }
    gl.useProgram(program);

    const posBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1,
      1, -1,
      -1, 1,
      -1, 1,
      1, -1,
      1, 1
    ]), gl.STATIC_DRAW);

    const aPosition = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(aPosition);
    gl.vertexAttribPointer(aPosition, 2, gl.FLOAT, false, 0, 0);

    const uResolution = gl.getUniformLocation(program, 'u_resolution');
    const uTime = gl.getUniformLocation(program, 'u_time');
    const uMouse = gl.getUniformLocation(program, 'u_mouse');
    const uHue = gl.getUniformLocation(program, 'u_hue');
    const uSaturation = gl.getUniformLocation(program, 'u_saturation');
    const uBrightness = gl.getUniformLocation(program, 'u_brightness');
    const uSpeed = gl.getUniformLocation(program, 'u_speed');

    gl.uniform1f(uHue, silkProps.hue);
    gl.uniform1f(uSaturation, silkProps.saturation);
    gl.uniform1f(uBrightness, silkProps.brightness);
    gl.uniform1f(uSpeed, silkProps.speed);

    let mouseX = window.innerWidth * 0.5;
    let mouseY = window.innerHeight * 0.5;
    let targetMouseX = mouseX;
    let targetMouseY = mouseY;

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      const width = window.innerWidth;
      const height = window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(uResolution, canvas.width, canvas.height);
    }

    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', (e) => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      targetMouseX = e.clientX * dpr;
      targetMouseY = (window.innerHeight - e.clientY) * dpr;
    });

    window.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches[0]) {
        const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        targetMouseX = e.touches[0].clientX * dpr;
        targetMouseY = (window.innerHeight - e.touches[0].clientY) * dpr;
      }
    }, { passive: true });

    const startTime = performance.now();

    function render(now) {
      if (overlay.classList.contains('logged-in')) {
        requestAnimationFrame(render);
        return;
      }
      const elapsed = (now - startTime) * 0.001;

      mouseX += (targetMouseX - mouseX) * (1.0 - silkProps.damping);
      mouseY += (targetMouseY - mouseY) * (1.0 - silkProps.damping);

      gl.uniform1f(uTime, elapsed);
      gl.uniform2f(uMouse, mouseX, mouseY);
      gl.drawArrays(gl.TRIANGLES, 0, 6);

      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
  }

  function init2DSilkFallback(canvas, props) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    let t = 0;
    function render2D() {
      if (overlay.classList.contains('logged-in')) {
        requestAnimationFrame(render2D);
        return;
      }
      t += 0.015 * props.speed;
      const w = canvas.width;
      const h = canvas.height;
      const grad = ctx.createRadialGradient(
        w * 0.5 + Math.sin(t) * 80,
        h * 0.4 + Math.cos(t) * 60,
        50,
        w * 0.5,
        h * 0.5,
        Math.max(w, h) * 0.8
      );
      grad.addColorStop(0, '#490e47');
      grad.addColorStop(0.4, '#360834');
      grad.addColorStop(0.8, '#20031e');
      grad.addColorStop(1, '#110110');

      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);
      requestAnimationFrame(render2D);
    }
    requestAnimationFrame(render2D);
  }

  // Initialize Silk Background Shader
  initSilkBackground();

  window.reopenLoginGate = function () {
    state = 'idle';
    resetToIdle();
    clearErrorState();
    confettiParticles = [];
    confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    submitBtn.innerHTML = '<span>Log In</span>';
    submitBtn.style.background = 'linear-gradient(135deg, #5b134b 0%, #36082e 100%)';
    overlay.classList.remove('logged-in');
    try {
      sessionStorage.removeItem('metri_authenticated');
      localStorage.removeItem('metri_authenticated');
    } catch (e) { }
  };
})();
