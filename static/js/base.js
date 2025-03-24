// * функции общие для всех страниц *

//
function emptyButton() {
    alert('Button does nothing :(');
}

// заполнить форму тестовыми данными
function testFill() {
        // итерация по всем полям ввода
        const inputs = document.querySelectorAll('input, textarea, date');;
        inputs.forEach(input => { try {
            // игнорить файловый инпут
            if (input.type === 'file') {
                return;
            }

            // если есть placeholder - вставить его
            if (input.placeholder) {
                input.value = input.placeholder;
            } else {
                switch (input.type) {
                    case 'url':
                        input.value = 'https://google.com'; break;
                    case 'date':
                        input.value = '2030-12-30'; break;
                    default:
                        input.value = 'test'; break;
                }
            }} catch(e) {alert(e)}
        });
    }

// очистить все поля ввода
function clearAll() {
    const inputs = document.querySelectorAll('input, textarea, date');;
    inputs.forEach(input => {
        input.value = '';
    });
}

