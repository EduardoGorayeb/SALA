const themeToggle = document.querySelector('.theme__toggle');
const html = document.documentElement;
const body = document.body;
const savedTheme = localStorage.getItem('theme');
const savedFontSize = localStorage.getItem('fontSize') || '16';

function updateLogo() {
  const logo = document.querySelector('.logo-imagem');
  if (logo) {
    if (html.classList.contains('dark-mode')) {
      logo.src = '/static/img/micro.png';
      logo.style.width = '60px';
      logo.style.height = '72px';
    } else {
      logo.src = '/static/img/micro2.png';
      logo.style.width = '50px';
      logo.style.height = '60px';
    }
  }
}

function updateFontSize() {
  const fontSize = parseInt(savedFontSize);
  html.style.fontSize = fontSize + 'px';
}

function increaseFontSize() {
  let currentSize = parseInt(localStorage.getItem('fontSize') || '16');
  if (currentSize < 24) {
    currentSize += 2;
    localStorage.setItem('fontSize', currentSize);
    html.style.fontSize = currentSize + 'px';
  }
}

function decreaseFontSize() {
  let currentSize = parseInt(localStorage.getItem('fontSize') || '16');
  if (currentSize > 12) {
    currentSize -= 2;
    localStorage.setItem('fontSize', currentSize);
    html.style.fontSize = currentSize + 'px';
  }
}

if (themeToggle) {
  if (savedTheme === 'dark') {
    html.classList.add('dark-mode');
    themeToggle.checked = true;
  } else {
    html.classList.remove('dark-mode');
    themeToggle.checked = false;
  }
  updateLogo();
  updateFontSize();

  themeToggle.addEventListener('change', () => {
    if (themeToggle.checked) {
      html.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    } else {
      html.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    }
    updateLogo();
  });
}


const increaseBtn = document.getElementById('increase-font');
const decreaseBtn = document.getElementById('decrease-font');

if (increaseBtn) {
  increaseBtn.addEventListener('click', increaseFontSize);
}

if (decreaseBtn) {
  decreaseBtn.addEventListener('click', decreaseFontSize);
}
