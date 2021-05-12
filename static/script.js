// $(window).load(function(){
//   $("#content").hide(1000);
// });

(function () {
  'use strict'

  // Side bar Live time 
  const clockElement = $( "#clock" );

  function updateClock ( clock ) {
    clock.text(new Date().toLocaleTimeString());
  }
  setInterval(() => {
    updateClock( clockElement );
  }, 1000);

  // Get cuurent date 
  $("#date").text(new Date().toString().slice(0, 16));
  
  // Get current year 
  $("#year").text(new Date().getFullYear());

  // Active route links
  let route = "/" + window.location.pathname.split("/").pop()
  const target = $('.nav-item a[href= "'+route+'"]');
  target.addClass('active')

  // Mobile side bar toggle button
  $("#sidebarToggle").on("click", function(){
    $(".sidebar").toggle(1000);
    $("#content").toggle(500);
  });

  // close button for notification pop outs
  $("#closeAlert").on("click", function(e){
    $("#AlertParent").hide(1000);
  });

   // feather icon
   feather.replace();
  
}());


