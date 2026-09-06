<<<<<<< HEAD
/* ==========================================================
   Motuscar Theme Controller (login-focused)
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {
=======
// static/login/js/theme.js

// Sistema de temas
document.addEventListener("DOMContentLoaded", function() {
  console.log('✅ Script de temas cargado');

>>>>>>> feature/ventasylogin
  const root = document.documentElement;
  const configBtn = document.getElementById("configBtn");
  const themeMenu = document.getElementById("themeMenu");
  const themeButtons = document.querySelectorAll(".config-menu-item");
<<<<<<< HEAD

  /* ==========================================================
     1️⃣ Forzar modo oscuro por defecto en LOGIN
     ========================================================== */

  // 🔍 Detecta si estamos en una página de login (por URL o por clase del body)
  const isLoginPage =
    window.location.pathname.includes("login") ||
    document.body.classList.contains("auth-page");

  if (isLoginPage) {
    // 🖤 Forzar modo oscuro
    root.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
  } else {
    // Si NO estamos en login, aplica el tema guardado o el del sistema
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      root.setAttribute("data-theme", savedTheme);
    } else {
      // Detecta preferencia del sistema
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.setAttribute("data-theme", prefersDark ? "dark" : "light");
    }
  }

  /* ==========================================================
     2️⃣ Menú desplegable de configuración
     ========================================================== */
  if (configBtn && themeMenu) {
    configBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const expanded = configBtn.getAttribute("aria-expanded") === "true";
      configBtn.setAttribute("aria-expanded", !expanded);
      themeMenu.classList.toggle("show");
    });

    // Cerrar el menú si se hace click fuera
    document.addEventListener("click", (e) => {
      if (!themeMenu.contains(e.target) && e.target !== configBtn) {
        themeMenu.classList.remove("show");
        configBtn.setAttribute("aria-expanded", false);
      }
    });
  }

  /* ==========================================================
     3️⃣ Cambio de tema al pulsar en los botones
     ========================================================== */
  themeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const selectedTheme = btn.getAttribute("data-theme");

      if (selectedTheme === "system") {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        root.setAttribute("data-theme", prefersDark ? "dark" : "light");
        localStorage.removeItem("theme");
      } else {
        root.setAttribute("data-theme", selectedTheme);
        localStorage.setItem("theme", selectedTheme);
      }

      // Cierra el menú tras cambiar
      themeMenu.classList.remove("show");
      configBtn.setAttribute("aria-expanded", false);
    });
  }); 
});
=======
  const STORAGE_KEY = "motuscar-theme";

  console.log('Elementos encontrados:', {
    configBtn: !!configBtn,
    themeMenu: !!themeMenu,
    themeButtons: themeButtons.length
  });

  // DIAGNÓSTICO ESPECÍFICO DEL ENGRANAJE
  console.log('🔍 DIAGNÓSTICO DEL ENGRANAJE:');
  if (configBtn) {
    const gearIcon = configBtn.querySelector('.fa-gear');
    console.log('Ícono engranaje encontrado:', !!gearIcon);
    console.log('Clases del botón:', configBtn.className);
    console.log('Estilos computados del botón:', window.getComputedStyle(configBtn));
    
    if (gearIcon) {
      console.log('Estilos computados del ícono:', window.getComputedStyle(gearIcon));
      console.log('Color del ícono:', window.getComputedStyle(gearIcon).color);
      console.log('Opacidad del ícono:', window.getComputedStyle(gearIcon).opacity);
      console.log('Font-size del ícono:', window.getComputedStyle(gearIcon).fontSize);
    }
  }

  // Función para aplicar tema
  function applyTheme(theme) {
    console.log('Aplicando tema:', theme);
    if (theme === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      root.setAttribute("data-theme", prefersDark ? "dark" : "light");
    } else {
      root.setAttribute("data-theme", theme);
    }
    localStorage.setItem(STORAGE_KEY, theme);
    
    // Actualizar estado visual de los botones
    themeButtons.forEach(btn => {
      const isActive = btn.getAttribute("data-theme") === theme;
      btn.setAttribute("aria-checked", isActive);
    });
  }

  // Cargar tema inicial
  const savedTheme = localStorage.getItem(STORAGE_KEY) || "dark";
  console.log('Tema guardado:', savedTheme);
  applyTheme(savedTheme);

  // Configurar botón de tema
  if (configBtn && themeMenu) {
    console.log('✅ Configurando botón de tema');
    
    configBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      console.log('Botón de tema clickeado - posición:', {
        x: e.clientX,
        y: e.clientY
      });
      const isExpanded = configBtn.getAttribute("aria-expanded") === "true";
      configBtn.setAttribute("aria-expanded", !isExpanded);
      themeMenu.hidden = isExpanded;
    });

    // Cerrar menú al hacer clic fuera
    document.addEventListener("click", function() {
      themeMenu.hidden = true;
      configBtn.setAttribute("aria-expanded", "false");
    });

    // Prevenir que el clic en el menú lo cierre
    themeMenu.addEventListener("click", function(e) {
      e.stopPropagation();
    });

    // Configurar botones de tema
    themeButtons.forEach(function(btn) {
      btn.addEventListener("click", function() {
        const selectedTheme = this.getAttribute("data-theme");
        console.log('Tema seleccionado:', selectedTheme);
        applyTheme(selectedTheme);
        themeMenu.hidden = true;
        configBtn.setAttribute("aria-expanded", "false");
      });
    });
  } else {
    console.error('❌ No se encontraron elementos del selector de tema');
  }

  // Detectar cambios del sistema
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
    const savedTheme = localStorage.getItem(STORAGE_KEY);
    if (savedTheme === "system") {
      root.setAttribute("data-theme", e.matches ? "dark" : "light");
    }
  });
});

// Menú de usuario
document.addEventListener("DOMContentLoaded", function() {
  const userBtn = document.getElementById("userMenuBtn");
  const dropdown = document.getElementById("userDropdown");

  if (userBtn && dropdown) {
    userBtn.addEventListener("click", function(e) {
      e.stopPropagation();
      const expanded = userBtn.getAttribute("aria-expanded") === "true";
      userBtn.setAttribute("aria-expanded", !expanded);
      dropdown.hidden = expanded;
    });

    document.addEventListener("click", function() {
      dropdown.hidden = true;
      userBtn.setAttribute("aria-expanded", "false");
    });

    dropdown.addEventListener("click", function(e) {
      e.stopPropagation();
    });
  }
});
>>>>>>> feature/ventasylogin
