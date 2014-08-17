function new_show_setup() {
    template.show('new_show', $('#content'), null, function(){

        $('#form-new-show').submit(function(event){
            external = {};
            form = $(this).serializeObject();
            if (form['tvrage-id'] != '') {
                external['tvrage'] = form['tvrage-id'];
            }
            if (form['imdb-id'] != '') {
                external['imdb'] = form['imdb-id'];
            }
            if (form['thetvdb-id'] != '') {
                external['thetvdb'] = form['thetvdb-id'];
            }
            index = {
                'info': form.index_info,
                'episodes': form.index_episodes,
            }
            api.post(
                '/shows', 
                {
                    'external': external,
                    'index': index
                },
                {
                    error: function(error_data){
                        if (error_data.code === 4003) {
                            $('#new-show-'+error_data.extra.external_field+'-id').focus();
                        }
                        template.show(
                            'new_show_error', 
                            $('#form-error'), 
                            error_data
                        );
                    }
                }
            );
            return false;
        });
        
        $('#new-show-imdb-id').keyup(function(){
            if (/tt[0-9]+/i.test($(this).val())) {
                $('#save-button').removeAttr('disabled');
                $('#save-button-info').hide();
            } else {
                $('#save-button').attr('disabled', 'disabled');
                $('#save-button-info').show();
            }
        });
    });
}