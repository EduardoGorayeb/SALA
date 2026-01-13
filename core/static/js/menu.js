
document.addEventListener('DOMContentLoaded', function() {
  console.log('Script carregado!');
  
  const menuHamburger = document.querySelector('.menu-hamburger');
  const navMobile = document.querySelector('.nav-mobile');
  const menuOverlay = document.querySelector('.menu-overlay');
  const closeMenu = document.querySelector('.close-menu');
  
  console.log('Elementos encontrados:', { menuHamburger, navMobile, menuOverlay, closeMenu });
  
  
  function toggleMobileMenu() {
    const isAberto = navMobile.classList.contains('menu-aberto');
    
    navMobile.classList.toggle('menu-aberto');
    menuOverlay.classList.toggle('menu-aberto');
    
    
    const spans = menuHamburger.querySelectorAll('span');
    if (!isAberto) {
      spans[0].style.transform = 'rotate(45deg) translate(6px, 6px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
    } else {
      spans[0].style.transform = 'none';
      spans[1].style.opacity = '1';
      spans[2].style.transform = 'none';
    }
  }
  
  function closeMobileMenu() {
    navMobile.classList.remove('menu-aberto');
    menuOverlay.classList.remove('menu-aberto');
    
    
    const spans = menuHamburger.querySelectorAll('span');
    spans[0].style.transform = 'none';
    spans[1].style.opacity = '1';
    spans[2].style.transform = 'none';
  }
  
  if (menuHamburger && navMobile && menuOverlay && closeMenu) {
    
    menuHamburger.addEventListener('click', function() {
      console.log('Menu hamburger clicado!');
      toggleMobileMenu();
    });
    
    
    closeMenu.addEventListener('click', function() {
      console.log('Botão fechar clicado!');
      closeMobileMenu();
    });
    
    
    menuOverlay.addEventListener('click', function() {
      console.log('Overlay clicado!');
      closeMobileMenu();
    });
    
    
    const mobileLinks = navMobile.querySelectorAll('a');
    mobileLinks.forEach(link => {
      link.addEventListener('click', function() {
        
        if (!this.classList.contains('mobile-login-btn') && 
            !this.classList.contains('mobile-register-btn') && 
            !this.classList.contains('mobile-logout-btn')) {
          closeMobileMenu();
        }
      });
    });
    
    
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && navMobile.classList.contains('menu-aberto')) {
        closeMobileMenu();
      }
    });
  }
  
  
  const desktopTheme = document.getElementById('theme');
  const mobileTheme = document.getElementById('mobile-theme');
  
  if (desktopTheme && mobileTheme) {
    
    mobileTheme.checked = desktopTheme.checked;
    
    
    desktopTheme.addEventListener('change', function() {
      mobileTheme.checked = this.checked;
    });
    
    
    mobileTheme.addEventListener('change', function() {
      desktopTheme.checked = this.checked;
      
      desktopTheme.dispatchEvent(new Event('change'));
    });
  }
  
  
  const mobileDecreaseFont = document.getElementById('mobile-decrease-font');
  const mobileIncreaseFont = document.getElementById('mobile-increase-font');
  
  if (mobileDecreaseFont && mobileIncreaseFont) {
    mobileDecreaseFont.addEventListener('click', function() {
      changeFontSize(-1);
    });
    
    mobileIncreaseFont.addEventListener('click', function() {
      changeFontSize(1);
    });
  }
  
  function changeFontSize(direction) {
    const currentSize = parseFloat(getComputedStyle(document.body).fontSize);
    const newSize = currentSize + (direction * 2);
    
    
    if (newSize >= 12 && newSize <= 24) {
      document.body.style.fontSize = newSize + 'px';
    }
  }
  
  
  const userBtn = document.getElementById('userBtn');
  const userDropdown = document.getElementById('userDropdown');

  if (userBtn && userDropdown) {
    // Initialize dropdown as hidden
    userBtn.setAttribute('aria-expanded', 'false');
    userDropdown.style.display = 'none';
    userDropdown.setAttribute('aria-hidden', 'true');

    userBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', !isExpanded);
      userDropdown.style.display = isExpanded ? 'none' : 'block';
      userDropdown.setAttribute('aria-hidden', String(isExpanded));
    });

    document.addEventListener('click', function() {
      userBtn.setAttribute('aria-expanded', 'false');
      userDropdown.style.display = 'none';
      userDropdown.setAttribute('aria-hidden', 'true');
    });


    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        userBtn.setAttribute('aria-expanded', 'false');
        userDropdown.style.display = 'none';
        userDropdown.setAttribute('aria-hidden', 'true');
      }
    });
  }
});