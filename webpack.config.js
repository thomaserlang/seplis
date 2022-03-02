var webpack = require('webpack');
var path = require('path');
var MiniCssExtractPlugin = require("mini-css-extract-plugin");
var staticPath = path.resolve(__dirname, 'src/seplis/web/static');

module.exports = {
    devtool: "source-map",
    entry: {
        app: path.resolve(staticPath, 'app'),
    },
    resolve: {
        extensions: ['.js', '.jsx', '.scss', '.css'],        
        modules: [
            path.resolve(staticPath, 'app'),
            'node_modules'
        ],
        alias: {
            seplis: path.resolve(staticPath, 'app'),
        }
    },
    output: {
        path: path.resolve(staticPath, 'dist'),
        filename: '[name].js',
        sourceMapFilename: '[file].map',
        libraryTarget: 'var',
        library: 'exports',
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: "[name].css",
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            Popper: ['popper.js', 'default'],
            Util: "exports-loader?Util!bootstrap/js/src/util",
            Dropdown: "exports-loader?Dropdown!bootstrap/js/src/dropdown",
        }),
    ],
    module: {
        rules: [
            {
                test: /\.(jsx|js)?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
            },
            {
                test: /\.(scss|css)/,
                use: [
                    MiniCssExtractPlugin.loader,
                    { loader: 'css-loader', options: { url: false, sourceMap: true } },
                    { loader: 'sass-loader', options: { sourceMap: true } }
                ]
            }
        ]
    },
    optimization: {
        splitChunks: {
            cacheGroups: {
                vendor: {
                    test: /node_modules/, 
                    name: 'vendor',
                    chunks: 'all',
                    enforce: true
                }
            }
        }
    }
}