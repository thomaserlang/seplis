var webpack = require('webpack');
var static = __dirname+'/src/seplis/web/static'
var ExtractTextPlugin = require('extract-text-webpack-plugin');


module.exports = {
    entry: {
        app: static+'/app',
        vendor: [
            'jquery',
            'bootstrap/js/dropdown',
            'react',
            'react-dom',
        ]
    },  
    resolve: {
        extensions: ['', '.js', '.jsx', '.scss']
    },
    output: {
        path: static+'/dist',
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
                include: static,
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