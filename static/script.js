$( document ).ready( function() {

    $("#addButton").click( function( event ) {
        event.preventDefault();
        create();
    });

    function create() {
        $.ajax({
            url: "/add",
            type: "POST",
            dataType: "json",
            data: { "title": $("#title").val(), "text": $("#text").val() },
        })

        .done(function(response) {
            var $newElement = "<article class='entry' "+
                              "id='"+response.id+"'>"+
                              "<a href='/detail/"+response.id+"'"+
                              "class='title'>"+
                              "<h3>"+response.title+"</h3></a>"+
                              "<p class='dateline'>"+response.created_+"</p>"+
                              "<div class='entry_body'>"+
                              response.mkdown+"</div></article>";
            $(".entry:first").before($newElement);
            $("#createForm").hide();
            $('#title').val('');
            $('#text').val('');
        })

        .fail(function(response) {
            alert("error");
        })
    };

    $("#addLink").click( function( event ) {
        event.preventDefault();
        $("#createForm").show();
    });

    $(document).click(function(event) {
        if(!$(event.target).closest('#createForm').length
        && !$(event.target).is('#addLink')) {
            $('#createForm').hide();
        }
    });

    $(document).click(function(event) {
        if(!$(event.target).closest('#editForm').length
        && !$(event.target).is('#editLink')) {
            $('#editForm').hide();
        }
    });

    $("#editLink").click(function(event) {
        event.preventDefault();
        $("#editForm").show();
    });

    $("#editButton").click(function(event) {
        event.preventDefault();
        update();
    });

    function update() {
        var pathArray = window.location.pathname.split("/");
        $.ajax({
            url: "/edit/"+pathArray[2],
            type: "POST",
            dataType: "json",
            data: {"title": $("#title").val(),
                   "text": $("#text").val()},
        })

        .done(function(response) {
            $(".title").html(response.title);
            $(".entry_body").html(response.mkdown);
            $("#editForm").hide();
        })

        .fail(function(response) {
            alert("error");
        })
    };

});