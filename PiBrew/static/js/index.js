/*
 * application.js
 * Copyright (C) 2016 Rafal Gumienny <r.gumienny@unibas.ch>
 *
 * Distributed under terms of the GPL license.
 */
$(document).ready(function(){
	$("#content").find("[id^='tab']").hide(); // Hide all content
    $("#tabs li:first").attr("id","current"); // Activate the first tab
    $("#content #tab1").fadeIn(); // Show first tab's content
    $('#tabs a').click(function(e) {
        e.preventDefault();
        if ($(this).closest("li").attr("id") == "current"){ //detection for current tab
         return;
        }
        else{
          $("#content").find("[id^='tab']").hide(); // Hide all content
          $("#tabs li").attr("id",""); //Reset id's
          $(this).parent().attr("id","current"); // Activate this
          $('#' + $(this).attr('name')).fadeIn(); // Show content for the current tab
        }
		});

	$("#status_menu").addClass('active')

    //connect to the socket server.
	var data = [[]];
	var namespace = '/test';
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    var number = 0.0;

	// Plotting
	var options_temp = {
		series: {
            lines: { show: true },
            points: { show: false }
        },
		axisLabels: {
            show: true
        },
		yaxis: {
			show: true,
			min: 0,
			max: 100,
			autoscaleMargin: null,
			axisLabel: "Temp [°C]",
		},
		xaxis: {
			show: true,
			min: 0,
			max: 1,
			autoscaleMargin: null,
			axisLabel: "Time [min]",
		}
	};
	// var plot_power = $.plot($("#plot_power"), data, options);

	//draw gauge
	var options_gauge_temperature = {
		majorTickLabel : true,
		value : 60,
		label : 'Temp',
		unitsLabel : ' °C',
		min : 0,
		max : 100,
		majorTicks : 11,
		minorTicks : 5, // small ticks inside each major tick
		greenFrom : 20,
		greenTo : 60,
		yellowFrom : 60,
		yellowTo : 80,
		redFrom : 80,
		redTo : 100
	};

	var options_gauge_power = {
		majorTickLabel : true,
		value : 60,
		label : 'Power',
		unitsLabel : ' %',
		min : 0,
		max : 100,
		majorTicks : 11,
		minorTicks : 5, // small ticks inside each major tick
		greenFrom : 20,
		greenTo : 60,
		yellowFrom : 60,
		yellowTo : 80,
		redFrom : 80,
		redTo : 100
	};

	temperatureDisplay = new Gauge(document.getElementById('tempGauge'), options_gauge_temperature);
	powerDisplay = new Gauge(document.getElementById('powerGauge'), options_gauge_power);


    //receive details from server
    socket.on('current_temperature', function(msg) {
        console.log("Received temperature: " + msg.temperature);
		temperatureDisplay.setValue(msg.temperature);
		$("#temp_status").attr("placeholder", msg.temperature);
    });

    socket.on('current_power', function(msg) {
        console.log("Received power: " + msg.power);
		powerDisplay.setValue(msg.power);
		$("#power_status").attr("placeholder", msg.power);
    });

    socket.on('current_step', function(msg) {
		$("#current_step").attr("placeholder", msg.step);
		$("#set_temperature").attr("placeholder", msg.set_temp);
    });

    socket.on('current_recipe', function(msg) {
		$("#current_recipe").attr("placeholder", msg.recipe);
    });

    socket.on('remaining_time', function(msg) {
		$("#remaining_time").attr("placeholder", msg.remaining_time);
    });


	socket.on('enable_continue_button', function(msg) {
		console.log("I try to enable button")
		$('#continue_button').prop('disabled', false);
		socket.emit('button_enabled')
    });

	socket.on('disable_continue_button', function(msg) {
		console.log("I try to disable button")
		$('#continue_button').prop('disabled', true);
		socket.emit('button_disabled')
    });

	$('#continue_button').on('click', function(event) {
	  event.preventDefault(); // To prevent following the link (optional)
	  socket.emit('continue_clicked')
	});

	socket.on('data_for_plot', function(msg) {
		var data_tmp = [[]]
		var max_tmp = 0.0;
		console.log("I got the data");
		console.log(msg);
		for (var key in msg) {
			data_tmp[0].push([parseFloat(key), parseFloat(msg[key].tem)]);
			if (max_tmp <= parseFloat(msg[key])){
				max_tmp = parseFloat(msg[key])
			};
		};
		var max_time = data_tmp[0][data_tmp[0].length - 1][0];
		options_temp.xaxis.max = max_time;
		console.log(data_tmp)
		data = data_tmp
		$.plot($("#plot_temp"), data, options_temp);
		// plot_temp.setData(data_tmp);
		// plot_temp.draw();
    });

	socket.on('new_data_for_plot', function(msg) {
		console.log("New data")
		console.log(data[0].length);
		console.log([parseFloat(msg.time), parseFloat(msg.temp)]);
		data[0].push([parseFloat(msg.time), parseFloat(msg.temp)]);
		console.log(data[0].length);
		var max_time = parseFloat(msg.time);
		options_temp.xaxis.max = max_time;
		$.plot($("#plot_temp"), data, options_temp);
    });



});
