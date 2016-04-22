var webpack = require('webpack');

const static = __dirname+'/src/seplis/web/static'

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
        extensions: ['', '.js', '.jsx']
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
            }
        ]
    }
}