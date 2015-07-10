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
                              "class='title'"+
                              "<h3>"+response.title+"</h3></a>"+
                              "<p class='dateline'>"+response.created_+"</p>"+
                              "<div class='entry_body'>"+
                              response.mkdown+"</div></article>";
            $(".entry").before($newElement);
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

});