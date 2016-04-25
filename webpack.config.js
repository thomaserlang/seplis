var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var path = require('path');
var staticPath = path.resolve('./src/seplis/web/static');

module.exports = {
    entry: {
        app: staticPath+'/app',
        vendor: [
            'jquery',
            'bootstrap/js/dropdown',
            'react',
            'react-dom',
        ]
    },  
    resolve: {
        extensions: ['', '.js', '.jsx', '.scss'],
        root: [
            staticPath+'/app',
        ]
    },
    output: {
        path: staticPath+'/dist',
        filename: '[name].js',
        sourceMapFilename: '[name].js.map',
        libraryTarget: 'var',
        library: 'exports',
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin({
            names: ['vendor']
        }),
        new ExtractTextPlugin("[name].css"),
    ],
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loader: 'babel',
                include: staticPath,
                query: {
                    cacheDirectory: true,
                    presets: ['react', 'es2015']
                },
            },  
            {  
                test:   /\.scss/,
                loader: ExtractTextPlugin.extract('style', 'css', 'sass'),
            }
        ]
    },
    devtool: 'source-map',
}