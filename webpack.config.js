var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var path = require('path');
var autoprefixer = require('autoprefixer');

var staticPath = path.resolve(__dirname, 'src/seplis/web/static');
var nodeModulesPath = path.resolve(__dirname, 'node_modules');

module.exports = {
    devtool: "source-map",
    entry: {
        app: path.resolve(staticPath, 'app'),
        vendor: [
            'jquery',
            'bootstrap/js/dist/dropdown',
            'react',
            'react-dom',
            'react-router',
            'moment',
            'select2',
            'flat',
            'form-serialize',
        ]
    },
    resolve: {
        extensions: ['', '.js', '.jsx', '.scss', '.css'],
        
        root: [
            path.resolve(staticPath, 'app'),
        ]
    },
    output: {
        path: path.resolve(staticPath, 'dist'),
        filename: '[name].js',
        sourceMapFilename: '[file].map',
        libraryTarget: 'var',
        library: 'exports',
    },
    plugins: [
        new webpack.optimize.CommonsChunkPlugin({
            names: ['vendor']
        }),
        new ExtractTextPlugin("app.css"),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            "window.jQuery": "jquery"
        }),
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
                test: /\.(scss|css)/,
                loader: ExtractTextPlugin.extract('style', 'css?sourceMap!postcss!sass?includePaths[]='+nodeModulesPath),
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
}