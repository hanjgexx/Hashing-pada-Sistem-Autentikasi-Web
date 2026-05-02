/* main.js — Client-side helper untuk form autentikasi */

/**
 * Toggle visibilitas password (tampilkan / sembunyikan)
 * @param {string} inputId - ID elemen input
 * @param {HTMLElement} btn  - Tombol toggle
 */
function toggleEye(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isHidden = input.type === 'password';
  input.type = isHidden ? 'text' : 'password';
  btn.innerHTML = isHidden
    ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
         <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
         <line x1="1" y1="1" x2="23" y2="23"/>
       </svg>`
    : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
         <circle cx="12" cy="12" r="3"/>
       </svg>`;
}

/**
 * Hitung dan tampilkan kekuatan password.
 * Kriteria: panjang, huruf besar, angka, karakter khusus.
 * @param {string} pwd - Password yang sedang diketik
 */
function updateStrength(pwd) {
  const fill  = document.getElementById('s-fill');
  const label = document.getElementById('s-text');
  if (!fill || !label) return;

  let score = 0;
  if (pwd.length >= 8)  score++;
  if (pwd.length >= 12) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;

  const levels = [
    { w: '0%',   color: 'transparent', text: '' },
    { w: '20%',  color: '#f05a5a',     text: 'Sangat lemah' },
    { w: '40%',  color: '#f0a84a',     text: 'Lemah' },
    { w: '60%',  color: '#f0a84a',     text: 'Sedang' },
    { w: '80%',  color: '#3ec87e',     text: 'Kuat' },
    { w: '100%', color: '#2aa865',     text: 'Sangat kuat ✓' },
  ];

  const lvl = levels[score] || levels[0];
  fill.style.width      = lvl.w;
  fill.style.background = lvl.color;
  label.textContent     = lvl.text;
  label.style.color     = lvl.color;
}

/* Auto-dismiss flash messages setelah 5 detik */
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });
});
