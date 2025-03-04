import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  INotebookTracker
} from '@jupyterlab/notebook';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'dotscripts',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, notebooks: INotebookTracker) => {
    console.log('JupyterLab extension dotscripts is activated');

    // Log available commands to verify registration
    console.log('Available Commands:', app.commands.listCommands());

    const command = 'dotscripts:run-tagged-and-below';
    app.commands.addCommand(command, {
      label: 'Run Tagged Cell and All Below',
      execute: (args: any) => {
        const tagName = args.tag || 'my-tag'; // Default tag if not specified
        console.log(`Executing cells from tag: ${tagName}`);

        const current = notebooks.currentWidget;
        if (!current) {
          console.warn('No active notebook.');
          return;
        }
        
        const notebook = current.content;
        let foundTaggedCell = false;

        notebook.widgets.forEach((cell: any, index: number) => {
          const metadata = cell.model.metadata as any;
          const tags = metadata.tags as string[] | undefined;

          //console.log(`Cell ${index} tags:`, tags);

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

export default extension;
