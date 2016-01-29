/*
 * application.js
 * Copyright (C) 2016 Rafal Gumienny <r.gumienny@unibas.ch>
 *
 * Distributed under terms of the GPL license.
 */
$(document).ready(function(){
	String.prototype.replaceAll = function(search, replacement) {
		var target = this;
		return target.replace(new RegExp(search, 'g'), replacement);
	};

	function removeStep(step){
		$('#step' + step.toString() + "_raw").remove();
	};

	var step_count = 1;
	var stepstring =     '<div id="stepSTEPNUM_raw" class="row">' +
		'<div class="col-md-1">' +
			'<p id="step_number">Step</p>' +
		'</div>' +
        '<div class="col-md-2">' +
            '<div class="form-group">' +
				'<label class="control-label" for="date_deb">Step name</label>' +
				'<input name="step_name" type="text" placeholder="Name of the step" class="form-control input-md" required>' +
          '</div>' +
        '</div>' +
        '<div class="col-md-1">' +
            '<div class="form-group">' +
				'<label class="control-label" for="date_deb">Time</label>' +
				'<div class="input-group">' +
					'<input name="step_time" type="number" placeholder="Time" class="form-control input-md" required>' +
					'<span class="input-group-addon">min</span>' +
				'</div>' +
          '</div>' +
        '</div>' +
        '<div class="col-md-1">' +
            '<div class="form-group">' +
				'<label class="control-label" for="date_deb">Temperature</label>' +
				'<div class="input-group">' +
					'<input name="step_temp" type="number" placeholder="Temp" class="form-control input-md" required>' +
					'<span class="input-group-addon">°C</span>' +
				'</div>' +
          '</div>' +
        '</div>' +
		'<div class="form-group">' +
		'<button type="button" id="delete_step_button" class="btn btn-xs btn-danger" onClick="$(\'#stepSTEPNUM_raw\').remove()"><span class="glyphicon glyphicon-remove"></span></button>' +
		'</div>' +
    '</div>'


	$("#recipes_menu").addClass('active')

	$('#add_step_button').on('click', function(event) {
		step_count += 1
		var newstep = stepstring.replaceAll("STEPNUM", step_count.toString())
		$('#steps_fieldset').append(newstep)
	});


});
