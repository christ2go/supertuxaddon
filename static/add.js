window.Parsley.addValidator('requiredon', {
  validateString: function(value,req) {
      if($("#"+req).is(":checked"))
        return !(value=="");
      return true;
  },
  messages: {
    en: 'Thsi field is required',
    de: "Dieses Feld muss ausgefüllt werden."
  }
});


window.Parsley.addValidator('namenotused', {
  validateString: function() {
      x = false;
      $.ajax({
          url: $SCRIPT_ROOT + '/_isavailable',
          async: false,
          data: {
              "name": $("#addon-name-speaking").val()
          },
          success: function(value){
              x = !value["rv"];
              return value;
          },
   error: function(){
       x = false;
       return false;
   }
    });
      return x;

  },
  messages: {
    en: 'This Addonname is already in use!',
    de: "Dieses Name ist schon vergeben."
  }
});



$( document ).ready(function() {
    // Activate on page selectpicker
$("[name='managed-mode']").bootstrapSwitch({
        onColor:'success',
        onSwitchChange: function(e,s){
            $(".managed-only").slideToggle();
        }
    });
$('.selectpicker').selectpicker({
  style: 'btn-info',
  size: 4
});
    // Hide managed only
    $(".managed-only").hide();


    // Change the displayes slug, whenever the input changes.
   $("#addon-name").on("input",function(){
       console.log("ok!");
       if($("#addon-name").val() == "")
       {
           $("#addon-name-speaking").html("None");
           return;
       }
       $("#addon-name-speaking").html(getSlug($("#addon-name").val()));
   });

    $("#addaddon").submit(function(ev){
    });



    $("#addaddon").parsley({
        successClass: "has-success",
        errorClass: "has-error",
        classHandler: function(el) {
    return el.$element.closest(".form-group");
}
,
        errorsWrapper: "<span class='help-block'></span>",
        errorTemplate: "<span></span>",
        //inputs: Parsley.options.inputs + ',[data-parsley-requiredOn]'

    });

});
