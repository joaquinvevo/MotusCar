const btn  = document.getElementById('configBtn');
const menu = document.getElementById('themeMenu');
const icon = btn?.querySelector('i');

function openMenu(){
  menu.hidden = false;
  menu.classList.add('open');
  btn.setAttribute('aria-expanded', 'true');
}
function closeMenu(){
  menu.classList.remove('open');
  btn.setAttribute('aria-expanded','false');
  setTimeout(() => { menu.hidden = true; }, 150);
}
function toggleMenu(){
  if (menu.hidden) openMenu(); else closeMenu();
}

// Cambia ícono con una pequeña animación, en función de si se abre o se cierra
function spinAndSwapIcon(opening){
  if (!icon) return;
  icon.classList.add('icon-spin'); // requiere .icon-spin { animation: spin-gear .25s ease; }
  if (opening) {
    icon.classList.remove('fa-gear');
    icon.classList.add('fa-gears');
  } else {
    icon.classList.add('fa-gear');
    icon.classList.remove('fa-gears');
  }
  icon.addEventListener('animationend', () => icon.classList.remove('icon-spin'), { once: true});
}

// 🔘 Click en el botón: abre/cierra + cambia el ícono
btn?.addEventListener('click', (e)=>{
  e.stopPropagation();
  const willOpen = menu.hidden;
  spinAndSwapIcon(willOpen);
  toggleMenu();
});

// 🔒 Cerrar con clic fuera
document.addEventListener('click', (e)=>{
  if (!menu.hidden && !menu.contains(e.target) && !btn.contains(e.target)) {
    spinAndSwapIcon(false);
    closeMenu();
  }
});

// ⎋ Cerrar con Escape
document.addEventListener('keydown', (e)=>{
  if (e.key === 'Escape' && !menu.hidden) {
    spinAndSwapIcon(false);
    closeMenu();
  }
});

/* ===== Tema ===== */
const THEME_KEY = 'theme-preference';

function applyTheme(theme){
  const root = document.documentElement;

  if (theme === 'system'){
    // Deja al sistema decidir
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches; // ← paréntesis arreglado
    root.setAttribute('data-theme', isDark ? 'dark' : 'light');
  } else {
    root.setAttribute('data-theme', theme);
  }

  // Marcar opción seleccionada
  document.querySelectorAll('.config-menu-item[role="menuitemradio"]').forEach(el=>{
    el.setAttribute('aria-checked', String(el.dataset.theme === theme));
  });
}

function saveTheme(theme){ localStorage.setItem(THEME_KEY, theme); }
function loadTheme(){ return localStorage.getItem(THEME_KEY) || 'system'; }

menu?.addEventListener('click', (e) => {
  const target = e.target.closest('.config-menu-item[role="menuitemradio"]');
  if (!target) return;
  const theme = target.dataset.theme;
  applyTheme(theme);
  saveTheme(theme);
  spinAndSwapIcon(false);
  closeMenu(); // ← antes faltaban los paréntesis
});

// Init
(function initTheme(){
  const saved = loadTheme();
  applyTheme(saved);
})();

// Si el usuario cambia el tema del SO en caliente y el modo es "system"
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', ()=>{
  if (loadTheme() === 'system') applyTheme('system');
});
