const static = __dirname+'/src/seplis/web/static'

module.exports = {
    entry: {
        app: static+'/app',
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