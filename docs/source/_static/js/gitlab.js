jQuery(function(){
    var ci_dashboard = "https://ska-telescope.gitlab.io/ska_ci_dashboard/";
    var dashboard_table = $("#ci-dashboard > table");
    if( dashboard_table.length ){
        $.get(ci_dashboard, function(data){
            dashboard_table.html($(data).find("#dataTable"));            
        });
    }
});

