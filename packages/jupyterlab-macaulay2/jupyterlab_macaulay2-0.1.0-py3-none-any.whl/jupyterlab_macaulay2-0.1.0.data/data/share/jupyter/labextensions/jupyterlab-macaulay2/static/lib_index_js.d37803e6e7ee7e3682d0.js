"use strict";
(self["webpackChunkjupyterlab_macaulay2"] = self["webpackChunkjupyterlab_macaulay2"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/codemirror */ "webpack/sharing/consume/default/@jupyterlab/codemirror");
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _codemirror_language__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @codemirror/language */ "webpack/sharing/consume/default/@codemirror/language");
/* harmony import */ var _codemirror_language__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_codemirror_language__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var codemirror_lang_macaulay2__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! codemirror-lang-macaulay2 */ "webpack/sharing/consume/default/codemirror-lang-macaulay2/codemirror-lang-macaulay2");
/* harmony import */ var codemirror_lang_macaulay2__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(codemirror_lang_macaulay2__WEBPACK_IMPORTED_MODULE_2__);



const plugin = {
    id: "jupyterlab-macaulay2:plugin",
    autoStart: true,
    description: "CodeMirror-based syntax highlighting for Macaulay2 code",
    requires: [_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__.IEditorLanguageRegistry],
    activate: async (app, registry) => {
        registry.addLanguage({
            name: "Macaulay2",
            mime: "text/x-macaulay2",
            support: new _codemirror_language__WEBPACK_IMPORTED_MODULE_1__.LanguageSupport((0,codemirror_lang_macaulay2__WEBPACK_IMPORTED_MODULE_2__.macaulay2)()),
            extensions: ["m2"],
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.d37803e6e7ee7e3682d0.js.map