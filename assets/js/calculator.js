        const currentDisplay = document.getElementById('current-display');
        const historyDisplay = document.getElementById('history-display');
        const buttons = document.querySelectorAll('.calc-button');
        const fontSizeSlider = document.getElementById('fontSizeSlider');

        let currentInput = '0';
        let previousInput = '';
        let operator = '';
        let resultCalculated = false;
        let clearOnNextInput = false;
        let memory = 0;

        function updateDisplay() {
            currentDisplay.textContent = currentInput;
            historyDisplay.textContent = previousInput;
        }

        


        function calculate() {
            let expression = previousInput + currentInput;
            expression = expression.replace(/÷/g, '/').replace(/×/g, '*').replace(/,/g, '.');

            try {
                let result = eval(expression);
                if (!isFinite(result)) throw new Error("Division par zéro");
                
                result = parseFloat(result.toFixed(10)); 
                previousInput = expression.replace(/\./g, ',') + ' =';
                currentInput = result.toString().replace(/\./g, ',');
                resultCalculated = true;
                clearOnNextInput = true;
            } catch (error) {
                currentInput = 'Erreur';
                previousInput = '';
                resultCalculated = true;
                clearOnNextInput = true;
                console.error("Erreur de calcul:", error);
            }
        }

        buttons.forEach(button => {
            button.addEventListener('click', () => {
                const value = button.dataset.value;

                if (['MC', 'MR', 'M+', 'M-', 'MS'].includes(value)) {
                    switch (value) {
                        case 'MC': memory = 0; break;
                        case 'MR': currentInput = memory.toString().replace(/\./g, ','); resultCalculated = true; break;
                        case 'M+': memory += parseFloat(currentInput.replace(/,/g, '.')); break;
                        case 'M-': memory -= parseFloat(currentInput.replace(/,/g, '.')); break;
                        case 'MS': memory = parseFloat(currentInput.replace(/,/g, '.')); resultCalculated = true; break;
                    }
                    updateDisplay();
                    return;
                }

                if (value === 'C') {
                    currentInput = '0';
                    previousInput = '';
                    operator = '';
                    resultCalculated = false;
                    clearOnNextInput = false;
                } else if (value === 'CE') {
                    currentInput = '0';
                    clearOnNextInput = false;
                } else if (value === 'BACKSPACE') {
                    currentInput = currentInput.length > 1 ? currentInput.slice(0, -1) : '0';
                    resultCalculated = false;
                    clearOnNextInput = false;
                } else if (value === '=') {
                    if (previousInput && operator && !resultCalculated) calculate();
                } else if (['+', '-', '*', '/'].includes(value)) {
                    if (currentInput === 'Erreur') { currentInput = '0'; previousInput = ''; }
                    if (previousInput && operator && !resultCalculated) calculate();
                    previousInput = currentInput.replace(/,/g, '.') + value;
                    operator = value;
                    clearOnNextInput = true;
                    resultCalculated = false;
                } else if (value === '+/-') {
                    if (currentInput !== '0' && currentInput !== 'Erreur') currentInput = (parseFloat(currentInput.replace(/,/g, '.')) * -1).toString().replace(/\./g, ',');
                } else if (value === '%') {
                    if (currentInput !== 'Erreur') currentInput = (parseFloat(currentInput.replace(/,/g, '.')) / 100).toString().replace(/\./g, ',');
                    resultCalculated = true;
                    clearOnNextInput = true;
                } else if (value === '1/x') {
                    let num = parseFloat(currentInput.replace(/,/g, '.'));
                    if (num === 0) {
                        currentInput = 'Division par zéro'; previousInput = ''; resultCalculated = true; clearOnNextInput = true;
                    } else if (currentInput !== 'Erreur') {
                        currentInput = (1 / num).toString().replace(/\./g, ','); resultCalculated = true; clearOnNextInput = true;
                    }
                } else if (value === 'x^2') {
                    if (currentInput !== 'Erreur') currentInput = (Math.pow(parseFloat(currentInput.replace(/,/g, '.')), 2)).toString().replace(/\./g, ',');
                    resultCalculated = true;
                    clearOnNextInput = true;
                } else if (value === 'sqrt') {
                    let num = parseFloat(currentInput.replace(/,/g, '.'));
                    if (num < 0) {
                        currentInput = 'Entrée non valide'; previousInput = ''; resultCalculated = true; clearOnNextInput = true;
                    } else if (currentInput !== 'Erreur') {
                        currentInput = (Math.sqrt(num)).toString().replace(/\./g, ',');
                    }
                    resultCalculated = true;
                    clearOnNextInput = true;
                } else {
                    if (currentInput === '0' || resultCalculated || clearOnNextInput || currentInput === 'Erreur') {
                        currentInput = value;
                        clearOnNextInput = false;
                    } else {
                        if (value === ',' && currentInput.includes(',')) return;
                        currentInput += value;
                    }
                    resultCalculated = false;
                }
                updateDisplay();
            });
        });

        document.addEventListener('keydown', (event) => {
            const key = event.key;
            let buttonValue = '';

            if (key >= '0' && key <= '9') buttonValue = key;
            else if (key === ',' || key === '.') buttonValue = ',';
            else if (key === '+') buttonValue = '+';
            else if (key === '-') buttonValue = '-';
            else if (key === '*') buttonValue = '*';
            else if (key === '/') buttonValue = '/';
            else if (key === 'Enter') { buttonValue = '='; event.preventDefault(); }
            else if (key === 'Backspace') buttonValue = 'BACKSPACE';
            else if (key === 'Escape') buttonValue = 'C';

            if (buttonValue) {
                const targetButton = document.querySelector(`.calc-button[data-value="${buttonValue}"]`);
                if (targetButton) {
                    targetButton.click();
                } else {
                    if (buttonValue === '*') document.querySelector('.calc-button[data-value="*"]').click();
                    else if (buttonValue === '/') document.querySelector('.calc-button[data-value="/"]').click();
                }
            }
        });

        fontSizeSlider.addEventListener('input', (event) => {
            const fontSize = event.target.value;
            currentDisplay.style.fontSize = `${fontSize}px`;
        });

        updateDisplay();
