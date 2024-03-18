$(document).ready(function() {
    
    var auto_load_on = 0;
    var auto_load_intervalID = "";
     $("#queued_notification").html("");
    
     $("#createvm").click(function () {
         submit_to_server();
     });
    
    
    
    
     $("#createvm").addClass('btn-secondary');
     $( "#createvm" ).prop( "disabled", true );
    
    $("#fileinput").addClass('d-none');
    $("#error_injection_status").addClass('d-none');
    
    $('input[type="file"]').change(function(e) { 
            $("#fileinput").addClass('d-none');
            var fileName = e.target.files[0].name;
            //alert("A file has been selected. "+ fileName); 
            var reader = new FileReader();
            //reader.readAsArrayBuffer(e.target.files[0]);
            reader.onload = readFiles(e)
            //reader.onload = loadHandler;
            reader.onerror = errorHandler;
    });
    
    
    
        
    var days_set = 0;
    var low_set = 0;
    var high_set = 0;
    var up_set = 0;
    
    var memory = "";
    var cpucores = "";
    var storage= "";
    var ostoinstall = "";
    
    var searched = "";
    var searching = "";
    
   
    
function readFiles(event) {
    var fileList = event.target.files;
    for(var i=0; i < fileList.length; i++ ) {
        loadAsText(fileList[i]);
    }
}

function loadAsText(theFile) {
    var reader = new FileReader();

    reader.onload = function(loadedEvent) {
        // result contains loaded file.
        const file = event.target.result;
        const allLines = file.split(/\r\n|\n/);
        process_delete_storage_list(allLines);
    }
    reader.readAsText(theFile);
}
    
function errorHandler() {
    alert ("A filer operation error has occured")
    }
    

    
    
    setInterval(function(){
        get_datastore_metrics();
    }, 5000);
    
    
startTime();
    
function startTime() {
  var today = new Date();
  var h = today.getHours();
  var m = today.getMinutes();
  var s = today.getSeconds();
  m = checkTime(m);
  s = checkTime(s);
    $("#clockheading").html( h + ":" + m + ":" + s);
  
  var t = setTimeout(startTime, 500);
}
function checkTime(i) {
  if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
  return i;
}
 

    


function get_queue(queue) {
     $.ajax({
             type: "POST",
             url: "get_" + queue + "_queue",
             data: JSON.stringify("sql_string" + ":" + "test"),
             contentType: "application/json; charset=utf-8",
             dataType: "json",
             success: function(response){
                $("#" + queue + "_queue").html("");
                $("#" + queue + "_queue").html(response.logData);
                if (queue == "job") {
                    $("#job_p").html("JOB QUEUE: " + response.jobs_in_queue);
                    $("#total_jobs_submitted").html("TOTAL JOBS SUBMITTED: "+response.total_jobs_submitted);
                }
                else if (queue == "wait") {
                     $("#wait_p").html("WAIT QUEUE: " + response.jobs_in_queue);
                }
                 else if (queue == "completed") {
                     $("#completed_p").html("COMPLETED / EXIT: " + response.jobs_in_queue+ " |  TOTAL JOBS EXITED: " + response.total_jobs_exited);
                }
                else {
                 alert("wrong queue specificed in javascript get_queue()")
                }
            },
            error: function (response) {
                $("#error_log").html(response.logData);
            }
         });
  }
    

    
function get_datastore_metrics() {
     $.ajax({
             type: "POST",
             url: "get_datastore_metrics",
             data: JSON.stringify("sql_string" + ":" + "test"),
             contentType: "application/json; charset=utf-8",
             dataType: "json",
             success: function(response){
                 $("#vm_count").html("Virtual Machines: "+response.vm_count);
                $("#memory_alloc").html("Memory alloc: "+response.memory_alloc);
                $("#capacity").html("Datastore capacity: "+response.capacity);
                $("#freespace").html("Datastore Available:  "+response.freespace);
                $("#largest_freespace").html("Datastore max vm: "+response.largest_freespace);
                $("#dc_provisioned").html("Datastore used: " +response.dc_provisioned);
                $("#vminfo").html(response.vminfo);
               
                 
                 
            },
             error: function (response) {
                 //alert("Post hit an error");
                $("#error_log").html(response.logData);
            }
         });
  }
    
$("#memory a ").click(function () {
     let x = $(this).text();
      $("#para-mem").text(x);
    memory = x;
     //$("#daysbutton").toggleClass('btn-success').toggleClass('btn-warning');
    $("#buttonmemory").addClass('btn-warning');
    days_set = 1;
    $("#divtable").html("");
    hide_top_part();
     $("#searchingforstocks").addClass('d-none');
    if (days_set == 1 && low_set == 1 && high_set == 1 && up_set == 1)
        {
            enable_create_vm();
            //$("#buttoncs").removeClass('d-none');
        }
     });
    
    
    $("#cpucores a ").click(function () {
     let x = $(this).text();
      $("#para-cpu").text(x);
        cpucores = x;
        $("#buttoncpucores").addClass('btn-warning');
    up_set = 1;
        $("#divtable").html("");
        hide_top_part();
        $("#searchingforstocks").addClass('d-none');
    if (days_set == 1 && low_set == 1 && high_set == 1 && up_set == 1)
        {
            enable_create_vm();
            //$("#buttoncs").removeClass('d-none');
        }
     });

    $("#storage a ").click(function () {
     let x = $(this).text();
         $("#para-storage").text(x);
        storage = x;
        $("#buttonstorage").addClass('btn-warning');
        low_set = 1;
        $("#divtable").html("");
        hide_top_part();
        $("#searchingforstocks").addClass('d-none');
        if (days_set == 1 && low_set == 1 && high_set == 1 && up_set == 1)
        {
            //$("#buttoncs").removeClass('d-none');
            enable_create_vm();
        }
      }); 
    
     $("#ostoinstall a ").click(function () {
     let x = $(this).text();
    $("#para-os").text(x);
         ostoinstall = x;
         
         $("#buttonostoinstall").addClass('btn-warning');
         high_set = 1;
         $("#divtable").html("");
         hide_top_part();
         $("#searchingforstocks").addClass('d-none');
         if (days_set == 1 && low_set == 1 && high_set == 1 && up_set == 1)
        {
            enable_create_vm();
            //$("#buttoncs").removeClass('d-none');
        }
     }); 
    
  function hide_top_part() {
      
  }
    
 
    function enable_create_vm() {
       
      
        
       $("#buttonostoinstall").removeClass('btn-warning');
       $("#buttonstorage").removeClass('btn-warning');
       $("#buttoncpucores").removeClass('btn-warning');
       $("#buttonmemory").removeClass('btn-warning');
      
       $("#buttonostoinstall").addClass('btn-danger');
       $("#buttonstorage").addClass('btn-danger');
       $("#buttoncpucores").addClass('btn-danger');
       $("#buttonmemory").addClass('btn-danger');
        
        $("#createvm").addClass('btn-success');
        $( "#createvm" ).prop( "disabled", false );
    }
    
   
      function submit_to_server() 
       {
    
        $("#buttonostoinstall").removeClass('btn-danger');
       $("#buttonstorage").removeClass('btn-danger');
       $("#buttoncpucores").removeClass('btn-danger');
       $("#buttonmemory").removeClass('btn-danger');
       $( "#createvm" ).prop( "disabled", true );
        $("#createvm").removeClass('btn-success');
        $("#createvm").addClass('btn-secondary');
        
         $("#para-mem").text("");
       $("#para-cpu").text("");
       $("#para-storage").text("");
       $("#para-os").text("");
        
       days_set = 0;
       low_set = 0;
       high_set = 0;
       up_set = 0;
       
        
       //========================================================
       
       
       var data =  {
                    "memory" : memory,
                    "cpucores" : cpucores,
                    "storage" : storage,
                    "ostoinstall" : ostoinstall,
                };
        
         $.ajax({
			type: 'POST',
            contentType: 'application/json',
			url: "/vcenter_create_vm",
             //data: JSON.stringify("volume" + ":" + volume),
			//data: JSON.stringify("sql_string" + ":" + query),
             
             data : JSON.stringify(data),
			dataType: "json",
             
             success: function(response){
                  //$("#countdown").hide();
                 
               
                 //  $("#divtable").text("Test message to data area")
                 //alert("Success")
            },
             error: function (response) {
         //$("#sql_output").html(response.statusText);
         $("#request_status").html(response.data);
    }
		});
       
       //==========================================
      
    
       }
    
    
    
    //################################################
    
    
    
    
    
    
    
    
    
    
    
    

    
});
