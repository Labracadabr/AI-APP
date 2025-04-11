document.addEventListener('DOMContentLoaded', function() {
  // DOM Elements
  const loginTabBtn = document.getElementById('loginTabBtn');
  const registerTabBtn = document.getElementById('registerTabBtn');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const loginFormElement = document.getElementById('loginFormElement');
  const registerFormElement = document.getElementById('registerFormElement');
  const loginError = document.getElementById('loginError');
  const registerError = document.getElementById('registerError');
  const loadingOverlay = document.getElementById('loadingOverlay');

  // Language Dictionaries
  const translations = {
    en: {
      'login': 'Login',
      'register': 'Register',
      'welcome-back': 'Welcome Back',
      'create-account': 'Create Account',
      'username': 'Username',
      'password': 'Password',
      'email': 'Email (optional)',
      'fullname': 'Full Name (optional)',
      'birth-year': 'Birth Year',
      'login-error': 'Invalid username or password',
      'register-error': 'Registration failed. Please check your information.'
    },
    ru: {
      'login': 'Вход',
      'register': 'Регистрация',
      'welcome-back': 'С возвращением',
      'create-account': 'Создать аккаунт',
      'username': 'Имя пользователя',
      'password': 'Пароль',
      'email': 'Email (необязательно)',
      'fullname': 'Полное имя (необязательно)',
      'birth-year': 'Год рождения',
      'login-error': 'Неверное имя пользователя или пароль',
      'register-error': 'Ошибка регистрации. Пожалуйста, проверьте данные.'
    }
  };

  let currentLanguage = 'en';

  // Tab switching
  function switchTab(tabType) {
    if (tabType === 'login') {
      loginTabBtn.classList.add('active');
      registerTabBtn.classList.remove('active');
      loginForm.classList.add('active');
      registerForm.classList.remove('active');
    } else {
      registerTabBtn.classList.add('active');
      loginTabBtn.classList.remove('active');
      registerForm.classList.add('active');
      loginForm.classList.remove('active');
    }
  }

  // Event listeners for tab buttons
  loginTabBtn.addEventListener('click', () => switchTab('login'));
  registerTabBtn.addEventListener('click', () => switchTab('register'));

  // Login form submission
  loginFormElement.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Hide previous errors
    loginError.classList.add('hidden');

    // Show loading overlay
    loadingOverlay.classList.remove('hidden');

    // Get form data
    const formData = new FormData();
    formData.append('username', document.getElementById('loginUsername').value);
    formData.append('password', document.getElementById('loginPassword').value);

    try {
      const response = await fetch('/token', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();

        // Store token in localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type);

        // Redirect to drawing app
        window.location.href = '/draw';
      } else {
        // Show error message
        loginError.textContent = translations[currentLanguage]['login-error'];
        loginError.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Login error:', error);
      loginError.textContent = error.message;
      loginError.classList.remove('hidden');
    } finally {
      loadingOverlay.classList.add('hidden');
    }
  });

  // Register form submission
  registerFormElement.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Hide previous errors
    registerError.classList.add('hidden');

    // Show loading overlay
    loadingOverlay.classList.remove('hidden');

    // Get form data
    const registerData = {
      username: document.getElementById('regUsername').value,
      password: document.getElementById('regPassword').value,
      birth_year: parseInt(document.getElementById('regBirthYear').value),
      email: document.getElementById('regEmail').value || null,
      fullname: document.getElementById('regFullname').value || null
    };

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(registerData)
      });

      if (response.ok) {
        // Auto-login after successful registration
        const formData = new FormData();
        formData.append('username', registerData.username);
        formData.append('password', registerData.password);

        const loginResponse = await fetch('/token', {
          method: 'POST',
          body: formData
        });

        if (loginResponse.ok) {
          const data = await loginResponse.json();

          // Store token in localStorage
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('token_type', data.token_type);

          // Redirect to drawing app
          window.location.href = '/';
        } else {
          // If auto-login fails, switch to login tab
          switchTab('login');
        }
      } else {
        const errorData = await response.json();
        registerError.textContent = errorData.error || translations[currentLanguage]['register-error'];
        registerError.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Registration error:', error);
      registerError.textContent = error.message;
      registerError.classList.remove('hidden');
    } finally {
      loadingOverlay.classList.add('hidden');
    }
  });

  // Set birth year range and default
  const birthYearInput = document.getElementById('regBirthYear');
  const currentYear = new Date().getFullYear();
  birthYearInput.min = currentYear - 100;
  birthYearInput.max = currentYear - 10;
  birthYearInput.value = currentYear - 25;

  // Check for language from localStorage or URL parameter
  function determineLanguage() {
    // Check URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');

    if (langParam && ['en', 'ru'].includes(langParam)) {
      return langParam;
    }

    // Check localStorage
    const storedLang = localStorage.getItem('language');
    if (storedLang && ['en', 'ru'].includes(storedLang)) {
      return storedLang;
    }

    // Default to English
    return 'en';
  }

  // Update language
  function updateLanguage() {
    document.documentElement.lang = currentLanguage;

    // Update all elements with language classes
    const langElements = document.querySelectorAll('[class*="lang-"]');
    langElements.forEach(element => {
      const langKeys = Array.from(element.classList)
        .filter(cls => cls.startsWith('lang-'))
        .map(cls => cls.replace('lang-', ''));

      if (langKeys.length > 0) {
        const key = langKeys[0];
        if (translations[currentLanguage][key]) {
          element.textContent = translations[currentLanguage][key];
        }
      }
    });

    // Store language preference
    localStorage.setItem('language', currentLanguage);
  }

  // Initialize
  currentLanguage = determineLanguage();
  updateLanguage();
});