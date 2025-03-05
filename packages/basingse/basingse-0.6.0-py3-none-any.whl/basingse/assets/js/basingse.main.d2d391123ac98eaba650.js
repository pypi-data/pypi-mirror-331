var Basingse;
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./src/frontend/scss/devbar.scss":
/*!***************************************!*\
  !*** ./src/frontend/scss/devbar.scss ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ }),

/***/ "./src/frontend/ts/theme.ts":
/*!**********************************!*\
  !*** ./src/frontend/ts/theme.ts ***!
  \**********************************/
/***/ (() => {


function getStoredTheme() {
    return localStorage.getItem("theme");
}
function setStoredTheme(theme) {
    localStorage.setItem("theme", theme);
}
function getPreferredTheme() {
    var storedTheme = getStoredTheme();
    if (storedTheme) {
        return storedTheme;
    }
    return getAutoTheme();
}
function getAutoTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
}
function setTheme(theme) {
    var root = document.documentElement;
    if (theme === "auto") {
        root.setAttribute("data-bs-theme", getAutoTheme());
    }
    else {
        root.setAttribute("data-bs-theme", theme);
    }
}
function showActiveTheme(theme, focus) {
    if (focus === void 0) { focus = false; }
    var themeSwitcher = document.querySelector("#color-theme-switcher");
    if (!themeSwitcher) {
        return;
    }
    var themeSwitcherText = document.querySelector("#color-theme-text");
    var activeThemeIcon = document.querySelector("#color-theme-icon use");
    var activeThemeButton = document.querySelector("[data-bs-theme-value=".concat(theme, "]"));
    var activeThemeButtonIcon = activeThemeButton === null || activeThemeButton === void 0 ? void 0 : activeThemeButton.querySelector("use");
    document
        .querySelectorAll("[data-bs-theme-value]")
        .forEach(function (button) {
        button.classList.remove("active");
        button.setAttribute("aria-pressed", "false");
    });
    activeThemeButton === null || activeThemeButton === void 0 ? void 0 : activeThemeButton.classList.add("active");
    activeThemeButton === null || activeThemeButton === void 0 ? void 0 : activeThemeButton.setAttribute("aria-pressed", "true");
    activeThemeIcon === null || activeThemeIcon === void 0 ? void 0 : activeThemeIcon.setAttribute("xlink:href", activeThemeButtonIcon === null || activeThemeButtonIcon === void 0 ? void 0 : activeThemeButtonIcon.getAttribute("xlink:href"));
    var themeSwitcherTextLabel = "Toggle theme (".concat(theme, ")");
    themeSwitcher.setAttribute("aria-label", themeSwitcherTextLabel);
    if (focus) {
        themeSwitcher.focus();
    }
}
window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", function () {
    var storedTheme = getStoredTheme();
    if (storedTheme !== "light" && storedTheme !== "dark") {
        showActiveTheme(getAutoTheme());
    }
});
setTheme(getPreferredTheme());
document.addEventListener("DOMContentLoaded", function () {
    showActiveTheme(getPreferredTheme());
    document
        .querySelectorAll("[data-bs-theme-value]")
        .forEach(function (button) {
        button.addEventListener("click", function () {
            var theme = button.getAttribute("data-bs-theme-value");
            setStoredTheme(theme);
            setTheme(theme);
            showActiveTheme(theme, true);
        });
    });
});


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
/*!*********************************!*\
  !*** ./src/frontend/ts/main.ts ***!
  \*********************************/
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _scss_devbar_scss__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../scss/devbar.scss */ "./src/frontend/scss/devbar.scss");
/* harmony import */ var _theme__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./theme */ "./src/frontend/ts/theme.ts");
/* harmony import */ var _theme__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_theme__WEBPACK_IMPORTED_MODULE_1__);



})();

(Basingse = typeof Basingse === "undefined" ? {} : Basingse).main = __webpack_exports__;
/******/ })()
;//# sourceMappingURL=/assets/js/basingse.main.js.map