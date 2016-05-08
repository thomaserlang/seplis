var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var path = require('path');
var autoprefixer = require('autoprefixer');

var staticPath = path.resolve('./src/seplis/web/static');
var nodeModulesPath = path.resolve('./node_modules');

module.exports = {
    entry: {
        app: staticPath+'/app',
        vendor: [
            'jquery',
            'bootstrap/dist/js/umd/dropdown',
            'font-awesome/scss/font-awesome',
            'react',
            'react-dom',
            'moment',
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
                loader: ExtractTextPlugin.extract('style', 'css!postcss!sass?includePaths[]='+nodeModulesPath),
            },
            { test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: "url-loader?limit=10000&mimetype=application/font-woff" },
            { test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: "file-loader" }
        ]
    },    
    postcss: function () {
        return [autoprefixer({
            browsers: [
              "Android 2.3",
              "Android >= 4",
              "Chrome >= 20",
              "Firefox >= 24",
              "Explorer >= 8",
              "iOS >= 6",
              "Opera >= 12",
              "Safari >= 6"
            ]
        })];
    },
    devtool: 'source-map',
}