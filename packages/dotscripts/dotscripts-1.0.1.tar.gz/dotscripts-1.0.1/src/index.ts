import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  INotebookTracker
} from '@jupyterlab/notebook';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'dotscripts',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebooks: INotebookTracker) => {
    console.log('✅ JupyterLab extension dotscripts is activated.');

    const command = 'dotscripts:run-tagged-and-below';
    app.commands.addCommand(command, {
      label: 'Run Tagged Cell and All Below (No Scrolling)',
      execute: async (args: any) => {
        const tagName = args.tag || 'my-tag';
        //console.log(`🔍 Searching for cells tagged with: ${tagName}`);

        // ✅ 1. Find all scrollable containers
        const scrollContainers = document.querySelectorAll('.jp-WindowedPanel-outer');
        const activeCells = document.querySelectorAll('.jp-Cell.jp-CodeCell');

        const previousScrollPositions: Map<Element, number> = new Map();

        // ✅ 2. Disable scrolling (lock `scrollTop`)
        const disableScrolling = () => {
          scrollContainers.forEach(el => {
            previousScrollPositions.set(el, el.scrollTop);
            (el as HTMLElement).style.overflow = 'hidden';
            (el as HTMLElement).dataset.lockScroll = 'true'; // Mark as locked
            //console.log(`🛑 Locked scrolling for:`, el);
          });

          // Disable focus on code cells (prevents auto-scroll)
          activeCells.forEach(cell => {
            (cell as HTMLElement).setAttribute('tabindex', '-1');
            //console.log(`🛑 Disabled focus on:`, cell);
          });

          // Listen & block unwanted scroll events
          document.addEventListener('scroll', preventForcedScroll, true);
        };

        // ✅ 3. Restore scrolling
        const enableScrolling = () => {
          scrollContainers.forEach(el => {
            (el as HTMLElement).style.overflow = ''; // Restore scrolling
            el.scrollTop = previousScrollPositions.get(el) || 0; // Restore previous position
            (el as HTMLElement).dataset.lockScroll = 'false';
            //console.log(`🔓 Restored scrolling for:`, el);
          });

          // Re-enable focus on code cells
          activeCells.forEach(cell => {
            (cell as HTMLElement).setAttribute('tabindex', '0');
            //console.log(`🔓 Re-enabled focus on:`, cell);
          });

          document.removeEventListener('scroll', preventForcedScroll, true);
        };

        // ✅ 4. Prevent Jupyter from overriding our scroll lock
        const preventForcedScroll = (event: Event) => {
          const target = event.target as HTMLElement;
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
            const tags = cell.model.metadata?.tags as string[] | undefined;

            if (Array.isArray(tags) && tags.includes(tagName)) {
              notebook.activeCellIndex = index;
              //console.log(`🔍 Found tagged cell at index ${index}, running all below.`);
              await app.commands.execute('notebook:run-all-below');
              //console.log('✅ Execution complete.');
              return; // Stop after executing from the first matched tagged cell
            }
          }

          //console.warn('❌ No matching tagged cell found.');
        } catch (error) {
          //console.error('❌ Error during execution:', error);
        } finally {
          // ✅ Always restore scrolling, even if an error occurs
          enableScrolling();
        }
      }
    });

    //console.log('✅ Registered command:', command);
  }
};

// ✅ Export the extension
export default extension;
