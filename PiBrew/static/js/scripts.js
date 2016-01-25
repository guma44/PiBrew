/*
 * application.js
 * Copyright (C) 2016 Rafal Gumienny <r.gumienny@unibas.ch>
 *
 * Distributed under terms of the GPL license.
 */
$(document).ready(function(){

	// Setting the tabs

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

    //connect to the socket server.
	var namespace = '/test'
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    var number = 0.0;

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
		temperatureDisplay.setValue(msg.temperature)
    });

    socket.on('current_power', function(msg) {
        console.log("Received power: " + msg.power);
		powerDisplay.setValue(msg.power);
    });

	$('#brew_button').on('click', function(event) {
	  event.preventDefault(); // To prevent following the link (optional)
	  socket.emit('brew_clicked')
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

	$('#show_recipe_button').on('click', function(event) {
	  var e = document.getElementById('recipe_select');
	  var item = e.options[e.selectedIndex].value;
	  socket.emit('show_recipe', {data: item})
	});




});
