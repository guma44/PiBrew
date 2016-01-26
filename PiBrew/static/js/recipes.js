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

	$('#delete_recipe_button').on('click', function(event) {
	  var e = document.getElementById('recipe_select');
	  var item = e.options[e.selectedIndex].value;
	  console.log('Delete clicked')
	  if (item != ''){
		  var loc = 'http://' + document.domain + ':' + location.port + '/delete/' + item
		  window.location.href = loc
	  };
	});

	$('#add_recipe_button').on('click', function(event) {
	  var e = document.getElementById('recipe_select');
	  var item = e.options[e.selectedIndex].value;
	  console.log('Add clicked')
	  var loc = 'http://' + document.domain + ':' + location.port + '/new'
	  window.location.href = loc
	});

	$('#brew_recipe_button').on('click', function(event) {
		console.log("Brew button")
	  event.preventDefault(); // To prevent following the link (optional)
	  var e = document.getElementById('recipe_select');
	  var item = e.options[e.selectedIndex].value;
	  if (item != ''){
		  var loc = 'http://' + document.domain + ':' + location.port + '/brew/' + item
		  window.location.href = loc
	  };
	});




});
