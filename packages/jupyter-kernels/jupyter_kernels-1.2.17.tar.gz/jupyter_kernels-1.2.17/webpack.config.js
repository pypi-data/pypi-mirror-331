/*
 * Copyright (c) 2023-2024 Datalayer, Inc.
 *
 * Datalayer License
 */

const path = require('path');
const webpack = require('webpack');
const miniSVGDataURI = require('mini-svg-data-uri');

const HtmlWebpackPlugin = require('html-webpack-plugin');

const IS_PRODUCTION = process.argv.indexOf('--mode=production') > -1;
const mode = IS_PRODUCTION ? 'production' : 'development';
const devtool = IS_PRODUCTION ? false : 'inline-cheap-source-map';
const minimize = IS_PRODUCTION ? true : false;
const publicPath = IS_PRODUCTION
  ? '/static/jupyter_kernels/'
  : 'http://localhost:3063/';

const commonOptions = {
  mode: mode,
  devServer: {
    port: 3063,
    open: [
      'http://localhost:3063'
    ],
    https: false,
    server: 'http',
    client: { overlay: false },
    historyApiFallback: true
  },
  watchOptions: {
    aggregateTimeout: 300,
    poll: 2000, // Seems to stabilise HMR file change detection
    ignored: '/node_modules/'
  },
  devtool,
  optimization: {
    minimize
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
    alias: {
      path: 'path-browserify',
      stream: 'stream-browserify'
    }
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: 'babel-loader',
        options: {
          plugins: ['@babel/plugin-proposal-class-properties'],
          presets: [
            [
              '@babel/preset-react',
              {
                runtime: 'automatic'
              }
            ],
            '@babel/preset-typescript'
          ],
          cacheDirectory: true
        },
        exclude: /node_modules/
      },
      {
        test: /\.m?js$/,
        resolve: {
          fullySpecified: false
        }
      },
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-react'],
          cacheDirectory: true
        }
      },
      {
        test: /\.css?$/i,
        use: ['style-loader', 'css-loader']
      },
      {
        // In .css files, svg is loaded as a data URI.
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.css$/,
        type: 'asset',
        generator: {
          dataUrl: content => miniSVGDataURI(content.toString())
        }
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.tsx$/,
        use: ['@svgr/webpack']
      },
      {
        // In .ts and .tsx files (both of which compile to .js), svg files
        // must be loaded as a raw string instead of data URIs.
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        issuer: /\.js$/,
        type: 'asset/source'
      },
      {
        test: /\.(png|jpg|jpeg|gif|ttf|woff|woff2|eot)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        type: 'asset/resource'
      },
    ]
  },
};

module.exports = [
  {
    ...commonOptions,
    entry: './src/KernelsApp',
    output: {
      publicPath,
      //    filename: '[name].[contenthash].jupyter-kernels.js',
      filename: '[name].jupyter-kernels.js'
    },
    plugins: [
      !IS_PRODUCTION
        ? new webpack.ProvidePlugin({
          process: 'process/browser'
        })
        : new webpack.ProvidePlugin({
          process: 'process/browser'
        }),
      new HtmlWebpackPlugin({
        template: './public/index.html'
      })
    ]
  },
]
