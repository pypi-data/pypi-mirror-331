/*
 * Copyright (c) 2023-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

const func = require('@jupyterlab/testutils/lib/jest-config');
const baseConfig = func(__dirname);

const esModules = [
  '@codemirror',
  '@datalayer',
  '@jupyterlab',
  '@jupyter',
  '@lumino',
  '@microsoft',
  'd3-color',
  'd3-format',
  'exenv-es6',
  'lib0',
  'lib0/websocket',
  'nanoid',
  'vscode\\-ws\\-jsonrpc',
  'y\\-protocols',
  'y\\-websocket',
  'y\\-webrtc',
  'yjs'
].join('|');

module.exports = {
  ...baseConfig,
  setupFiles: [...baseConfig.setupFiles, './jest-setup.cjs'],
  testRegex: '(/src/__tests__/.*(test|spec))\\.[jt]sx?$',
  transform: {
    '\\.[jt]sx?$': 'babel-jest',
    '\\.svg$': '@jupyterlab/testing/lib/jest-raw-loader.js'
  },
  transformIgnorePatterns: [`/node_modules/(?!${esModules}).+`]
};
