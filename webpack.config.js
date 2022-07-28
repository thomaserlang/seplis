const webpack = require('webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require("path");

module.exports = {
    
    entry: {
        main: {
            import: './src/seplis/web/ui/index.jsx',
        },
    },
    devtool: "source-map",
    resolve: {
        extensions: ['.js', '.jsx', '.scss', '.css'],
        modules: [
            './src/seplis/web/ui',
            'node_modules'
        ],
        alias: {
            seplis: path.resolve(__dirname, '/src/seplis/web/ui/'),
        }
    },    
    module: {
        rules: [
            {
                test: /\.(jsx|js)?$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                },
            },
            {
                test: /\.(css|scss)$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    { loader: 'css-loader', options: { url: false, sourceMap: true } },
                    { loader: 'sass-loader', options: { sourceMap: true } }
                ],
            }
        ]
    },

    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            Popper: ['popper.js', 'default'],
            Util: "exports-loader?Util!bootstrap/js/src/util",
            Dropdown: "exports-loader?Dropdown!bootstrap/js/src/dropdown",
        }),
        new MiniCssExtractPlugin({
          filename: "[name].[contenthash].css",
          chunkFilename: "[id].[contenthash].css",
        }),
        new HtmlWebpackPlugin({
          'filename': path.resolve(__dirname, 'src/seplis/web/templates/ui/react.html'),
          'template': './src/seplis/web/ui/index.html',
          'chunks': ['main'],
          'publicPath': '/static/ui',
        }),
    ],
    output: {
        filename: '[name].[contenthash].js',
        path: path.resolve(__dirname, 'src/seplis/web/static/ui'),
        clean: true,
    },
}