var webpack = require('webpack');
var path = require('path');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var staticPath = path.resolve(__dirname, 'src/seplis/web/static');
var nodeModulesPath = path.resolve(__dirname, 'node_modules');

module.exports = {
    devtool: "source-map",
    entry: {
        app: path.resolve(staticPath, 'app'),
        vendor: [
            'jquery',
            'popper.js',
            'bootstrap/js/src/util',
            'bootstrap/js/src/dropdown',
            'react',
            'react-dom',
            'react-router',
            'fecha',
            'select2',
            'flat',
            'form-serialize',
        ],
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
        new webpack.optimize.CommonsChunkPlugin({
            names: ['vendor']
        }),
        new ExtractTextPlugin({
            'filename': 'app.css'
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
                loader: 'babel-loader',
                options: {
                    presets: [
                      'es2015',
                      'react',
                    ],
                },
            },
            {
                test: /\.(scss|css)/,
                use: ExtractTextPlugin.extract({
                    use: [
                        'css-loader?sourceMap',
                        'postcss-loader',
                        'sass-loader?includePaths[]='+nodeModulesPath,
                    ]
                }),
            },
            {
                test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            limit: 10000,
                            mimetype: 'application/font-woff',
                        }
                    }
                ]
            },
            { 
                test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/, 
                use: "file-loader",
            }
        ]
    },
}