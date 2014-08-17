$('#signin-form').submit(function(event){
    event.preventDefault();
    api.post(
        '/signin', 
        $(this).serialize(), 
        {
            done: function(data){
                location.href = $('#next').val();
            }, 
            error: function(error_data){
                template.show(
                    multiline(function(){/*
                        <div class="alert alert-danger">
                            <strong><%=message %>.</strong>
                            <p>Forgot your password? Reset it <a href="#">here.</p>
                        </div>
                    */}),
                    $('#signin-error'),
                    error_data
                );
                if (error_data.code === 1000) {
                    $('#password').select();
                }
            }
        }
    );
});