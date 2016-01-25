/*
 * application.js
 * Copyright (C) 2016 Rafal Gumienny <r.gumienny@unibas.ch>
 *
 * Distributed under terms of the GPL license.
 */
$(document).ready(function(){

	$("#recipes_menu").addClass('active')

	$('#show_recipe_button').on('click', function(event) {
	  var e = document.getElementById('recipe_select');
	  var item = e.options[e.selectedIndex].value;
	  console.log('Show clicked')
	  if (item != ''){
		  var loc = 'http://' + document.domain + ':' + location.port + '/show/' + item
		  window.location.href = loc
	  };
	});




});
