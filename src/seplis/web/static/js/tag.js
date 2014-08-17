$('.add-show-tag').submit(function(event){
    event.preventDefault();
    api.post(
        '/user-tags',
        $(this).serialize(),
        {
            done: function(data){
                alert(data);
            }
        } 
    )
});

$(document).on('submit', '.form-tag', function(event) {
    event.preventDefault();
    var _this = this;
    var relation_id = $(_this).find('.tag-relation-id').val();
    api.post(
        '/user-tags',
        $(this).serialize(),
        {
            done: function(data){
                api.get(
                    '/user-tags', 
                    $(_this).serialize(), 
                    {
                        done: function(data){
                            show_tags(
                                $('#tags-'+relation_id),
                                data,
                                relation_id
                            )
                        }
                    }
                );
                $(_this).find('input[name="name"]').val('');
                $(document).click();
            }
        }         
    );
});

$('.btn-add-tag').click(function(){
    var _this = this;
    setInterval(function(){
        $(_this).parent().find('.input-add-tag').focus();
    }, 10);
});

$('.btn-group').on('click', '.link-tag-delete', function(event){
    event.preventDefault();
    $(this).parent().find('.form-tag').submit();
});

function tag_generate_html(tag, relation_id) {  
    return _.template(  
        multiline(function(){/*
            <div class="btn-group">
                <button class="btn btn-success dropdown-toggle" data-toggle="dropdown">
                    <%-tag.name %>
                </button>
                <ul class="dropdown-menu">
                    <li>
                        <a href="/users/<%=current_user.id %>/tags/<%=tag.type %>?tag_id=<%=tag.id %>">
                            View all
                        </a>
                    </li>
                    <li class="divider"></li>
                    <li>
                        <a href="#" class="link-tag-delete">Delete</a>
                        <form class="form-tag">                        
                            <input type="hidden" class="tag-method" name="method" value="delete">
                            <input type="hidden" class="tag-relation-id" name="relation_id" value="<%=relation_id %>">
                            <input type="hidden" name="type" value="<%=tag.type %>">
                            <input type="hidden" name="tag_id" value="<%=tag.id %>">
                        </form>
                    </li>
                </ul>
            </div>
        */}),
        {
            tag: tag,
            relation_id: relation_id,
            current_user: current_user
        }
    );
}

function show_tags(obj, tags, relation_id) {
    obj.children('.btn-group').slice(1).remove();
    if (tags.length === 0) {
        obj.append(multiline(function(){/*
            <div class="btn-group">
                <button class="btn btn-default" disabled>You have not added any tags.</button>
            </div>
        */}));
        return
    }
    $.each(tags, function(index, tag){
        obj.append(
            tag_generate_html(tag, relation_id)
        )
    });
}