(function() {
    var publish_api_url = '/publish';
    var text_api_base_url = '/edit/text/';
    var image_api_base_url = '/edit/image/';
    var container_api_base_url = '/edit/container/';
    var mapbox_api_base_url = '/edit/mapbox/geojson';
    var texts = $('*[data-text-identifier]');
    var images = $('*[data-image-identifier]');
    var containers = $('*[data-container-identifier]');


    var submit_text_input = function(text_node) {
        var identifier = text_node.data('text-identifier');
        var input_node = text_node.find('textarea');

        $.post(
            text_api_base_url + identifier, {
            'content': input_node.val()
        }).done(function(data) {
            var identifier = data.identifier;
            var content = data.content;

            text_node.empty();
            text_node.append(content);
        });
    }


    var render_text_input = function(text_node, original_content) {
        var width = text_node.width();
        var height = text_node.height();
        text_node.empty();
        text_node.append('<textarea type="text">');

        var input_node = text_node.find('textarea');
        input_node.val(original_content);
        input_node.focus();
        input_node.width(width);
        input_node.height(height);

        input_node.on('click', function(event) {
            return false;
        });

        input_node.on('keyup', function(event) {
            // Cancel input
            if (event.keyCode == 27) {
                text_node.empty();
                text_node.append(original_content);
            // Submit input
            } else if (event.keyCode == 13) {
                submit_text_input(text_node);
            }
        });
    }


    // Clicking text blurbs kicks off editing behavior
    texts.on('click', function(event) {
        var text_node = $(this);
        var identifier = $(this).data('text-identifier');

        $.get(
            text_api_base_url + identifier,
            function(data) {
                var original_content = data.content;
                render_text_input(text_node, original_content);
            }
        );
    });


    images.on('click', function(event) {
        var image_element = $(this);
        var identifier = image_element.data('image-identifier');
        var image_api_url = image_api_base_url + identifier;
        var input_element = '<input id="fileupload" type="file" name="files[]" data-url="' + image_api_url + '" multiple>';

        $('#fileupload').remove();
        image_element.after(input_element);

        $('#fileupload').fileupload({
            dataType: 'json',
            done: function (e, data) {
                var image_src_segments = image_element.attr('src').split('/');
                var image_src_base_segments = image_src_segments.splice(0, 2);
                var new_image_src = image_src_base_segments.join('/') + '/' + data.result.filename;
                image_element.attr('src', new_image_src);
            }
        });
    });


    var render_container_buttons = function(edit_container) {
        containers.append('<button type="button" data-action="+">+</button><button type="button" data-action="-">-</button>');

        var container_buttons = containers.find('button');
        container_buttons.on('click', edit_container);
    }

    var edit_container = function(event) {
        var self = this;
        var visible_figures = $(this).parent().siblings('figure:visible');
        var mode = $(this).data('action');
        var identifier = $(this).parent().data('container-identifier');

        $.post(
            container_api_base_url + identifier, {
            'mode': mode
        }).done(function(data) {
            var identifier = data.identifier;
            var mode = data.mode;

            if (mode == '-') {
                if (visible_figures.length == 1) {
                    return;
                }

                $(self).parent().siblings('figure:visible').last().hide();
            } else if (mode == '+') {
                if (visible_figures.length == 6) {
                    return;
                }

                $(self).parent().siblings('figure:hidden').first().show();
            }

            resize_containers();
        });
    }

    var resize_containers = function() {
       $('article figure').parent().each(function(index, article) {
           var figures = $(article).find('figure');
           var visible_figures = $(article).find('figure:visible');

            if (visible_figures.length == 1) {
                figures.removeClass();
                figures.addClass('item 12u')
            } else if (visible_figures.length > 1 && visible_figures.length <= 4) {
                figures.removeClass();
                figures.addClass('item 6u');
            } else if (visible_figures.length > 4) {
                figures.removeClass();
                figures.addClass('item 4u');
            }
       });
    }

    render_container_buttons(edit_container);
    resize_containers();

    var render_mapbox_editor = function() {
        var container = $('#jsoneditor');
        container.text(JSON.stringify(map.markerLayer.getGeoJSON(), null, 2));
        container.on('blur', function() {
            var data = JSON.parse(container.val());

            $.post(
                mapbox_api_base_url, {
                'geojson': container.val()
            }).done(function(data) {
                var geojson = JSON.parse(data.geojson);
                map.markerLayer.setGeoJSON(geojson);
            });
        });
    }

    render_mapbox_editor();

    // Auto-hide any flash messages after 3 seconds
    setTimeout(function() {
        $('.flash-messages').fadeOut(function() {
            $('.flash-messages').remove();
        });
    }, 2000);


    // Publish / Reset buttons
    $('#edit-reset').on('click', function(event) {
        var reset_confirm = window.confirm('Throw away your changes?');

        if (reset_confirm == true) {
            var current_url = window.location.href;
            window.location.href = current_url + '/reset';
        }
    });

    $('#edit-publish').on('click', function(event) {
        var publish_confirm = window.confirm('Go live?');

        if (publish_confirm == true) {
            window.location.href = '/publish';
        }
    });
})();
