const webpack = require("webpack")
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require("mini-css-extract-plugin")

module.exports = (env, argv) => {
    return {
        entry: {
            main: {
                import: './seplis/web/ui/index.tsx',
            },
        },
        devtool: "source-map",
        resolve: {
            extensions: [ '.tsx', '.ts', '.js' ],
            alias: {
                '@seplis': path.resolve(__dirname, 'seplis/web/ui/'),
            }
        },    
        module: {
            rules: [
                {
                    test: /\.tsx?$/,
                    use: 'ts-loader',
                    exclude: /node_modules/,
                }, 
                {
                    test: /\.css$/i,
                    use: [MiniCssExtractPlugin.loader, "css-loader"],
                },
                {
                    test: /\.less$/i,
                    use: [
                        "style-loader",
                        "css-loader",
                        {
                            loader: "less-loader",
                            options: {
                                lessOptions: {
                                    javascriptEnabled: true,
                                },
                            },
                        },
                    ],
                },
            ]
        },

        plugins: [
            new webpack.DefinePlugin({
                'buildMode': JSON.stringify(argv.mode),
            }),
            new MiniCssExtractPlugin({
            filename: "[name].[contenthash].css",
            chunkFilename: "[id].[contenthash].css",
            }),
            new HtmlWebpackPlugin({
            'filename': path.resolve(__dirname, 'seplis/web/templates/ui/react.html'),
            'template': './seplis/web/ui/index.html',
            'chunks': ['main'],
            'publicPath': '/static/ui',
            }),
        ],
        optimization: {
            splitChunks: {
                // include all types of chunks
                chunks: 'all',
            },
        },
        output: {
            filename: '[name].[contenthash].js',
            path: path.resolve(__dirname, 'seplis/web/static/ui'),
            clean: true,
        },
    }
}