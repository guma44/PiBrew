/*
 * application.js
 * Copyright (C) 2016 Rafal Gumienny <r.gumienny@unibas.ch>
 *
 * Distributed under terms of the GPL license.
 */
$(document).ready(function(){
    //connect to the socket server.
	var namespace = '/test'
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    var number = 0.0;

	//draw gauge
	var options_gauge = {
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
		yellowTo : 90,
		redFrom : 90,
		redTo : 100
	};

	gaugeDisplay = new Gauge(document.getElementById('tempGauge'), options_gauge);


    //receive details from server
    socket.on('current_temperature', function(msg) {
        console.log("Received temperature: " + msg.temperature);
		gaugeDisplay.setValue(msg.temperature)
		socket.emit('current_temperature', {data: msg.temperature})
    });

});
