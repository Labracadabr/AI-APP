document.addEventListener('DOMContentLoaded', function() {
  // Configuration
  const items = ["cube", "face", "car", "mountain", "dog", "house", "tree", "book", "apple", "cat"];
  let currentLanguage = 'en';
  let currentItem = '';
  
  // DOM Elements
  const canvas = document.getElementById('drawingCanvas');
  const ctx = canvas.getContext('2d');
  const brushSizeSlider = document.getElementById('brushSize');
  const brushSizeDisplay = document.getElementById('brushSizeDisplay');
  const drawBtn = document.getElementById('drawBtn');
  const eraseBtn = document.getElementById('eraseBtn');
  const undoBtn = document.getElementById('undoBtn');
  const redoBtn = document.getElementById('redoBtn');
  const clearBtn = document.getElementById('clearBtn');
  const submitBtn = document.getElementById('submitBtn');
  const nextBtn = document.getElementById('nextBtn');
  const taskDisplay = document.getElementById('taskDisplay');
  const langToggle = document.getElementById('langToggle');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const responsePopup = document.getElementById('responsePopup');
  const popupMessage = document.getElementById('popupMessage');
  const popupClose = document.getElementById('popupClose');

  // Drawing State
  let isDrawing = false;
  let isErasing = false;
  let lastX = 0;
  let lastY = 0;
  let brushSize = 2;
  let drawingHistory = [];
  let redoHistory = [];
  let currentHistoryIndex = -1;

  // Language Dictionaries
  const translations = {
    en: {
      'draw-prompt': 'What you need to draw:',
      'profile': 'Profile',
      'extra': 'Settings',
      'draw': 'Draw',
      'erase': 'Erase',
      'undo': 'Undo',
      'redo': 'Redo',
      'clear': 'Clear',
      'brush-size': 'Brush size:',
      'submit': 'Submit',
      'next': 'Next',
      'loading': 'Processing...',
    },
    ru: {
      'draw-prompt': 'Что нужно нарисовать:',
      'profile': 'Профиль',
      'extra': 'Настройки',
      'draw': 'Рисовать',
      'erase': 'Стереть',
      'undo': 'Отменить',
      'redo': 'Вернуть',
      'clear': 'Очистить',
      'brush-size': 'Размер кисти:',
      'submit': 'Отправить',
      'next': 'Далее',
      'loading': 'Обработка...',
    }
  };

  // Initialize Canvas
  function initCanvas() {
    // Set canvas dimensions to match container size
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;

    // Set default styles
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.lineWidth = brushSize * 2; // Scale up brush size
    ctx.strokeStyle = '#000000';

    // Save initial canvas state
    saveCanvasState();
  }

  // Canvas Drawing Functions
  function startDrawing(e) {
    isDrawing = true;
    [lastX, lastY] = getPointerPosition(e);
  }

  function draw(e) {
    if (!isDrawing) return;

    // Prevent scrolling on touch devices
    if (e.type === 'touchmove') {
      e.preventDefault();
    }

    const [currentX, currentY] = getPointerPosition(e);

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(currentX, currentY);
    ctx.stroke();

    [lastX, lastY] = [currentX, currentY];
  }

  function stopDrawing() {
    if (isDrawing) {
      isDrawing = false;
      saveCanvasState();
    }
  }

  function getPointerPosition(e) {
    let x, y;
    const rect = canvas.getBoundingClientRect();

    // Handle both mouse and touch events
    if (e.type.includes('touch')) {
      x = e.touches[0].clientX - rect.left;
      y = e.touches[0].clientY - rect.top;
    } else {
      x = e.clientX - rect.left;
      y = e.clientY - rect.top;
    }

    return [x, y];
  }

  function saveCanvasState() {
    // Clear any redo history when a new action is performed
    if (currentHistoryIndex < drawingHistory.length - 1) {
      drawingHistory = drawingHistory.slice(0, currentHistoryIndex + 1);
    }

    drawingHistory.push(canvas.toDataURL());
    currentHistoryIndex = drawingHistory.length - 1;

    // Limit history size to prevent memory issues
    if (drawingHistory.length > 30) {
      drawingHistory.shift();
      currentHistoryIndex--;
    }

    // Update undo/redo button states
    updateUndoRedoButtons();
  }

  function undo() {
    if (currentHistoryIndex > 0) {
      currentHistoryIndex--;
      loadCanvasState(currentHistoryIndex);
      updateUndoRedoButtons();
    }
  }

  function redo() {
    if (currentHistoryIndex < drawingHistory.length - 1) {
      currentHistoryIndex++;
      loadCanvasState(currentHistoryIndex);
      updateUndoRedoButtons();
    }
  }

  function loadCanvasState(index) {
    const img = new Image();
    img.src = drawingHistory[index];
    img.onload = function() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
    };
  }

  function updateUndoRedoButtons() {
    // Disable undo button if at beginning of history
    if (undoBtn) {
      undoBtn.disabled = currentHistoryIndex <= 0;
    }

    // Disable redo button if at end of history
    if (redoBtn) {
      redoBtn.disabled = currentHistoryIndex >= drawingHistory.length - 1;
    }
  }

  function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    saveCanvasState();
  }

  function setDrawMode() {
    isErasing = false;
    ctx.globalCompositeOperation = 'source-over';
    ctx.strokeStyle = '#000000';
    updateToolButtons();
  }

  function setEraseMode() {
    isErasing = true;
    ctx.globalCompositeOperation = 'destination-out';
    ctx.strokeStyle = 'rgba(0,0,0,1)';
    updateToolButtons();
  }

  function updateToolButtons() {
    drawBtn.classList.toggle('active', !isErasing);
    eraseBtn.classList.toggle('active', isErasing);
  }

  function updateBrushSize() {
    brushSize = parseInt(brushSizeSlider.value);
    brushSizeDisplay.textContent = brushSize;
    ctx.lineWidth = brushSize * 2; // Scale up for better visibility
  }

  // Application Functions
  function getRandomItem() {
    const randomIndex = Math.floor(Math.random() * items.length);
    currentItem = items[randomIndex];
    taskDisplay.textContent = currentItem;
    return currentItem;
  }

  async function submitDrawing() {
    // Show loading overlay
    loadingOverlay.classList.remove('hidden');

  // Prepare data to submit
    try {

        // Convert canvas to Base64
        const dataUrl = canvas.toDataURL("image/png");
        const base64Image = dataUrl.split(",")[1];  // Remove "data:image/png;base64,"
        const data = {
            image: base64Image,
            item_name: currentItem
      };

      // Send to API
      const response = await fetch('/api/submit-drawing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      // Hide loading overlay
      loadingOverlay.classList.add('hidden');

      // Show result popup
      showResultPopup(result);

    } catch (error) {
      console.error('Error submitting drawing:', error);
      loadingOverlay.classList.add('hidden');

      // Show error popup
      showResultPopup({
        message: 'Failed to submit drawing. Please try again.',
        passed: false,
        error: error.message
      });
    }
  }

  function showResultPopup(result) {
    const popupContent = responsePopup.querySelector('.popup-content');

    if (result.error) {
      popupContent.classList.add('popup-error');
      popupMessage.textContent = result.error;
    } else {
      popupContent.classList.remove('popup-error');
      popupMessage.textContent = result.message;

      // Always show submit button
      submitBtn.classList.remove('hidden');

      // Show "Next" button if passed, but don't hide submit
      if (result.passed) {
        nextBtn.classList.remove('hidden');
      }
    }

    responsePopup.classList.remove('hidden');
  }

  function nextTask() {
    // Reset canvas
    clearCanvas();

    // Hide "Next" button but keep "Submit" button visible
    nextBtn.classList.add('hidden');

    // Get new task
    getRandomItem();

    // Hide popup
    responsePopup.classList.add('hidden');
  }

  // Language Functions
  function toggleLanguage() {
    currentLanguage = currentLanguage === 'en' ? 'ru' : 'en';
    updateLanguage();
  }

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
  }

  // Event Listeners
  function setupEventListeners() {
    // Drawing events
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);

    // Touch events
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw, { passive: false });
    canvas.addEventListener('touchend', stopDrawing);

    // Tool buttons
    drawBtn.addEventListener('click', setDrawMode);
    eraseBtn.addEventListener('click', setEraseMode);
    undoBtn.addEventListener('click', undo);
    redoBtn.addEventListener('click', redo);
    clearBtn.addEventListener('click', clearCanvas);

    // Brush size
    brushSizeSlider.addEventListener('input', updateBrushSize);

    // Submit and Next buttons
    submitBtn.addEventListener('click', submitDrawing);
    nextBtn.addEventListener('click', nextTask);

    // Language toggle
    langToggle.addEventListener('click', toggleLanguage);

    // Popup close
    popupClose.addEventListener('click', () => {
      responsePopup.classList.add('hidden');
    });

    // Window resize
    window.addEventListener('resize', initCanvas);
  }

  // Initialize App
  function init() {
    initCanvas();
    setupEventListeners();
    setDrawMode(); // Default to draw mode
    updateBrushSize(); // Set initial brush size
    getRandomItem(); // Get first task
    updateLanguage(); // Set initial language
    updateUndoRedoButtons(); // Initialize undo/redo button states
  }
  
  init();
});