
(function() {

    var tpl = swig.compile($("#tpl_station_item").html());


    $('#search-box').on('keyup', function() {
        var term = $(this).val().toLowerCase();

        $('li.station').remove();

        if (term) {
            $.get('search', {
                q: term
            }).done(function(data){
                console.log(data.result)
                $.each(data.result, function(i, item) {
                    console.log(tpl(item))
                    $("#station-list ul").append(tpl(item));
                });
            });

        }

    });

    var player = new Player($('.controls'), $('#playing-info'));
    player.check_forever();

})();
