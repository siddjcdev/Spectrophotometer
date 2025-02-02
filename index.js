$(function() {
 
    $("#btnCuvette").click(function(){
        alert("Step 1 Complete!");
        $(this).closest('tr').find('.step-action').prop('checked', true);
        $(this).closest('tr').addClass('active');
        $(this).hide();
    });

    $("#btnColor").click(function(){
        let color = $("#colors").val() 
        if (color == 'none') {
            alert('Please select a color.')
            return
        }
        else{
            alert("Step 2 Complete!");
            $(this).closest('tr').find('.step-action').prop('checked', true);
            $(this).closest('tr').addClass('active');
            $(this).hide();
        }
       
    });
    $("#btnScan").click(function(){
        scanColor(this);
        
    });
    $("#btnSensor").click(function(){
        alert("Step 4 Complete!");
        $(this).closest('tr').find('.step-action').prop('checked', true);
        $(this).closest('tr').addClass('active');
        $(this).hide();
    });
    $("#btnResults").click(function(){
        alert("Congratulations! You have completed all steps of to analyze your sample. Hopefully, you are satisfied with your results.");
        $(this).closest('tr').find('.step-action').prop('checked', true);
        $(this).closest('tr').addClass('active');
        $(this).hide();
    });

    $("#btnRefresh").click(function(){
        var result = confirm("Are you sure that you want to restart the experiment?");
        location.reload(true);
    });
    // $('.js-check-all').on('click', function() {
  
    //     if ( $(this).prop('checked') ) {
    //         $('th input[type="checkbox"]').each(function() {
    //             $(this).prop('checked', true);
    //             $(this).closest('tr').addClass('active');
    //         })
    //     } else {
    //         $('th input[type="checkbox"]').each(function() {
    //             $(this).prop('checked', false);
    //       $(this).closest('tr').removeClass('active');
    //         })
    //     }
  
    // });
  
    $('th[scope="row"] input[type="checkbox"]').on('click', function() {
      if ( $(this).closest('tr').hasClass('active') ) {
        $(this).closest('tr').removeClass('active');
      } else {
        $(this).closest('tr').addClass('active');
      }
    });
  });
function scanColor(btn) {
    let color = $("#colors").val() 
    if (color == 'none') {
        alert('Please select a color.')
        return
        
    }
    //alert("Selected color = "+color)
    let postData = {
    "action": "scanColor",
    "color": color
    };

    $.ajax({
        url: '/api', // Replace with your API endpoint
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(postData),
        success: function(response) {
            console.log('Success:', response);
            $(".intensity-0").html(response.I0)
            $(".intensity-1").html(response.I1)
            $(".absorbance").html(response.A)
            $(".concentration").html(response.C)
            $("#cled-state").css("background-color", "rgb(0,255,0)");
            alert("Step 3 Complete!");
            $(btn).closest('tr').find('.step-action').prop('checked', true);
            $(btn).closest('tr').addClass('active');
            $(btn).hide();
            
            
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}