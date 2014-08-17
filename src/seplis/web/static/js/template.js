var Template = function(){

};

Template.prototype.show = function(template, to, data) {
    to.html(
        _.template(template, data)
    );
}
