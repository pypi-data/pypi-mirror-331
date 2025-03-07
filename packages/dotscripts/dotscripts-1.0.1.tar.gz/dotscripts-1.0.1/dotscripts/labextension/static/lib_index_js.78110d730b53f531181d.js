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
        console.log('✅ JupyterLab extension dotscripts is activated.');
        const command = 'dotscripts:run-tagged-and-below';
        app.commands.addCommand(command, {
            label: 'Run Tagged Cell and All Below (No Scrolling)',
            execute: async (args) => {
                const tagName = args.tag || 'my-tag';
                //console.log(`🔍 Searching for cells tagged with: ${tagName}`);
                // ✅ 1. Find all scrollable containers
                const scrollContainers = document.querySelectorAll('.jp-WindowedPanel-outer');
                const activeCells = document.querySelectorAll('.jp-Cell.jp-CodeCell');
                const previousScrollPositions = new Map();
                // ✅ 2. Disable scrolling (lock `scrollTop`)
                const disableScrolling = () => {
                    scrollContainers.forEach(el => {
                        previousScrollPositions.set(el, el.scrollTop);
                        el.style.overflow = 'hidden';
                        el.dataset.lockScroll = 'true'; // Mark as locked
                        //console.log(`🛑 Locked scrolling for:`, el);
                    });
                    // Disable focus on code cells (prevents auto-scroll)
                    activeCells.forEach(cell => {
                        cell.setAttribute('tabindex', '-1');
                        //console.log(`🛑 Disabled focus on:`, cell);
                    });
                    // Listen & block unwanted scroll events
                    document.addEventListener('scroll', preventForcedScroll, true);
                };
                // ✅ 3. Restore scrolling
                const enableScrolling = () => {
                    scrollContainers.forEach(el => {
                        el.style.overflow = ''; // Restore scrolling
                        el.scrollTop = previousScrollPositions.get(el) || 0; // Restore previous position
                        el.dataset.lockScroll = 'false';
                        //console.log(`🔓 Restored scrolling for:`, el);
                    });
                    // Re-enable focus on code cells
                    activeCells.forEach(cell => {
                        cell.setAttribute('tabindex', '0');
                        //console.log(`🔓 Re-enabled focus on:`, cell);
                    });
                    document.removeEventListener('scroll', preventForcedScroll, true);
                };
                // ✅ 4. Prevent Jupyter from overriding our scroll lock
                const preventForcedScroll = (event) => {
                    const target = event.target;
                    if (target.dataset.lockScroll === 'true') {
                        //console.log("🚫 Blocking forced scroll:", target);
                        target.scrollTop = previousScrollPositions.get(target) || 0; // Reset scroll
                        event.preventDefault();
                    }
                };
                // ✅ Apply scrolling lock BEFORE execution
                disableScrolling();
                await new Promise(resolve => setTimeout(resolve, 0)); // Ensure next frame starts with scroll disabled
                try {
                    // Find the active notebook
                    const current = notebooks.currentWidget;
                    if (!current) {
                        //console.warn('⚠️ No active notebook found.');
                        return;
                    }
                    const notebook = current.content;
                    for (let index = 0; index < notebook.widgets.length; index++) {
                        const cell = notebook.widgets[index];
                        const tags = cell.model.metadata?.tags;
                        if (Array.isArray(tags) && tags.includes(tagName)) {
                            notebook.activeCellIndex = index;
                            //console.log(`🔍 Found tagged cell at index ${index}, running all below.`);
                            await app.commands.execute('notebook:run-all-below');
                            //console.log('✅ Execution complete.');
                            return; // Stop after executing from the first matched tagged cell
                        }
                    }
                    //console.warn('❌ No matching tagged cell found.');
                }
                catch (error) {
                    //console.error('❌ Error during execution:', error);
                }
                finally {
                    // ✅ Always restore scrolling, even if an error occurs
                    enableScrolling();
                }
            }
        });
        //console.log('✅ Registered command:', command);
    }
};
// ✅ Export the extension
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extension);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.78110d730b53f531181d.js.map