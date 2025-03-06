/*
 * Copyright (c) 2023-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '@datalayer/jupyter-kernels:placeholder',
  description: 'Jupyter Kernels Placeholder.',
  autoStart: true,
  requires: [],
  activate: (app: JupyterFrontEnd) => {},
}

export default plugin;
