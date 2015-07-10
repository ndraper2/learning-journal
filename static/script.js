$( document ).ready( function() {

    $("#addButton").click( function( event ) {
        event.preventDefault();
        create();
    });

    function create() {
        $.ajax({
            url: "/add",
            type: "POST",
            dataType: 'json',
            data: { "title": $("#title").val(), 'text': $("#text").val},
        })

        .done(function(response) {
            $("title").val = response.title;
            $("text").val = response.text;
        })

        .fail(function(response) {
            alert("error");
        })
    };

    $("#addLink").click( function( event ) {
        event.preventDefault();
        showCreateForm();
    });

    function showCreateForm() {
        $("#createForm").show()
    };

});