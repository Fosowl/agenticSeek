function findInputs(element, result = []) {
    // Find all <input> elements in the current DOM tree
    const inputs = element.querySelectorAll('input');
    inputs.forEach(input => {
        result.push({
            tagName: input.tagName,
            text: input.name || '',
            type: input.type || '',
            class: input.className || '',
            xpath: getXPath(input),
            displayed: isElementDisplayed(input)
        });
    });
    // Find all <select> elements (dropdowns / multi-choice)
    const selects = element.querySelectorAll('select');
    selects.forEach(select => {
        const options = Array.from(select.options).map(opt => ({
            value: opt.value,
            text: opt.textContent.trim(),
            selected: opt.selected
        }));
        result.push({
            tagName: select.tagName,
            text: select.name || '',
            type: 'select',
            class: select.className || '',
            xpath: getXPath(select),
            displayed: isElementDisplayed(select),
            multiple: select.multiple,
            options: options
        });
    });
    // Find all <textarea> elements
    const textareas = element.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        result.push({
            tagName: textarea.tagName,
            text: textarea.name || '',
            type: 'textarea',
            class: textarea.className || '',
            xpath: getXPath(textarea),
            displayed: isElementDisplayed(textarea)
        });
    });
    const allElements = element.querySelectorAll('*');
    allElements.forEach(el => {
        if (el.shadowRoot) {
            findInputs(el.shadowRoot, result);
        }
    });
    return result;
}
// function to get the XPath of an element
function getXPath(element) {
    if (!element) return '';
    if (element.id !== '') return '//*[@id="' + element.id + '"]';
    if (element === document.body) return '/html/body';

    let ix = 0;
    const siblings = element.parentNode ? element.parentNode.childNodes : [];
    for (let i = 0; i < siblings.length; i++) {
        const sibling = siblings[i];
        if (sibling === element) {
            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
        }
        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
            ix++;
        }
    }
    return '';
}
return findInputs(document.body);

function isElementDisplayed(element) {
    const style = window.getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
        return false;
    }
    return true;
}