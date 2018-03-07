module.exports = {
    plugins: [
        require('autoprefixer')({
            cascade : false,
            browsers: [
                "> 1%",
                "last 2 versions",
            ],
       })
    ]
}