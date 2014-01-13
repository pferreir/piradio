var Player = (function() {
    function View($elem_controls, $elem_display) {
        this.$elem_controls = $elem_controls;
        this.$elem_display = $elem_display;
    }

    $.extend(View.prototype, {

        _controls: function(subsel) {
            return this.$elem_controls.find(subsel);
        },

        _display: function(subsel) {
            return this.$elem_display.find(subsel);
        },

        set_playing: function() {
            this._controls('.button').removeClass('active');
            this._controls('#play_button').addClass('active');
        },

        set_stopped: function() {
            this._controls('.button').removeClass('active');
            this._controls('#stop_button').addClass('active');
            this._display('#display').removeClass('flipped');
            $('li.station').removeClass("selected");
        },

        set_paused: function(state) {
            this._controls('.button').removeClass('active');
            this._controls('#pause_button').toggleClass('active', state);
            this._controls('#play_button').toggleClass('active', !state);

            this._display('.station').toggleClass('paused', state);
            this._display('.station .name').toggleClass('icon-pause', state);
        },

        set_station_info: function(data) {
            var $station = this._display('.station'),
                $nothing = this._display('.nothing');

            if (data.playing) {
                $station.find('.name').html(data.station.name);
                $station.find('.song').html(data.song);

                $('li.station').removeClass("selected");
                $('li.station[data-station-id="' + data.station.id + '"]').addClass("selected");

                if (data.station.has_logo) {
                    $station.find('.logo').attr('src', '/logo/' + data.station.id);
                } else {
                    $station.find('.logo').attr('src', '/static/img/radio.png');
                }

                this._display('#display').addClass('flipped');

                if (!data.paused) {
                    this.set_playing();
                }
            }

            this.set_paused(data.paused);

        }
    });


    function Controller(view) {
        this._setup();
        this.view = view;
        this.paused = false;
    }

    $.extend(Controller.prototype, {
        _setup: function() {
            var that = this;

            $('#station-list').on('click', '.station', function(){
                that._click_station($(this).closest('li').data('stationId'));
            });

            $('.controls').on('click', '#play_button:not(.active)', function(){
               that._click_play();
            });

            $('.controls').on('click', '#stop_button:not(.active)', function(){
               that._click_stop();
            });

            $('.controls').on('click', '#pause_button:not(.active)', function(){
                that._click_pause();
            });
        },

        toggle_paused: function() {
            var that = this;
            $.post('/pause/').done(
                function(result) {
                    that.view.set_paused(result.paused);
                });
        },

        _click_station: function(station_id) {
            var that = this;

            $.post('/play/' + station_id).done(
                function(result) {
                    that.view.set_playing();
                });
        },

        _click_play: function() {
            if (this.paused) {
                this.toggle_paused();
            }
        },

        _click_stop: function() {
            var that = this;
            $.post('/stop/').done(
                function() {
                    that.view.set_stopped();
                });
        },

        _click_pause: function() {
            this.toggle_paused();
        },

        check_playing: function() {
            var that = this;

            $.get('/playing.json').done(function(result) {
                that.paused = result.paused;
                that.view.set_station_info(result);
            });
        }
    });

    var _Player = function($controls, $info) {
        this.view = new View($controls, $info);
        this.controller = new Controller(this.view);
    };

    $.extend(_Player.prototype, {
        check_forever: function() {
            var that = this;
            this.controller.check_playing();

            setInterval(function() {
                that.controller.check_playing();
            }, 5000);
        }
    });

    return _Player;
})();

