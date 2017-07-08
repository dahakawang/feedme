var HtmlWebpackPlugin = require('html-webpack-plugin');

const webpack = require('webpack');
const path = require('path');

module.exports = {
  entry: "./src/index.jsx",

  output: {
    path: path.resolve(__dirname,'debug'),
    filename: "[name].bundle.js"
  },

  module: {
    loaders: [
      {
        test: /.jsx?$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        query: {
          presets: ['es2015', 'react'],
          compact: false
        }
      }
    ]
  },

  plugins: [
    new HtmlWebpackPlugin({
      title: 'Feedme'
    })
  ],

  devtool: 'source-map',

  devServer: {
    contentBase: path.join(__dirname, "debug"),
    compress: true,
    port: 9000
  }

  ///////////  uncomment this for production ////////////////
  // plugins: [
  //   new webpack.optimize.UglifyJsPlugin({
  //     compress: {
  //       warnings: false
  //     }
  //   }),
  //   new webpack.DefinePlugin({
  //     'process.env': {'NODE_ENV': JSON.stringify('production')}
  //   })
  // ],////////////////////////////////////////////////////////
};

