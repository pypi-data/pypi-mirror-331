"use strict";
(self["webpackChunkdotscripts"] = self["webpackChunkdotscripts"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);

const extension = {
    id: 'dotscripts',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    activate: (app, notebooks) => {
        console.log('JupyterLab extension dotscripts is activated');
        // Log available commands to verify registration
        console.log('Available Commands:', app.commands.listCommands());
        const command = 'dotscripts:run-tagged-and-below';
        app.commands.addCommand(command, {
            label: 'Run Tagged Cell and All Below',
            execute: (args) => {
                const tagName = args.tag || 'my-tag'; // Default tag if not specified
                console.log(`Executing cells from tag: ${tagName}`);
                const current = notebooks.currentWidget;
                if (!current) {
                    console.warn('No active notebook.');
                    return;
                }
                const notebook = current.content;
                let foundTaggedCell = false;
                notebook.widgets.forEach((cell, index) => {
                    const metadata = cell.model.metadata;
                    const tags = metadata.tags;
                    console.log(`Cell ${index} tags:`, tags);
                    if (tags?.includes(tagName)) {
                        console.log(`Found tagged cell at index ${index}`);
                        foundTaggedCell = true;
                    }
                    // If the tagged cell has been found, execute it and all below
                    if (foundTaggedCell) {
                        notebook.activeCellIndex = index;
                        app.commands.execute('notebook:run-all-below');
                    }
                });
                if (!foundTaggedCell) {
                    console.warn(`No cell found with tag: ${tagName}`);
                }
            }
        });
        console.log('Registered command:', command);
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extension);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.76267c81700bc9dcc91e.js.map