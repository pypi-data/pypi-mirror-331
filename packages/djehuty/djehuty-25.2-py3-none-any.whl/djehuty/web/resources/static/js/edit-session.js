function save_session (session_id) {
    event.preventDefault();
    event.stopPropagation();

    var jqxhr  = jQuery.ajax({
        url:         `/my/sessions/${session_id}/edit`,
        type:        "PUT",
        contentType: "application/json",
        accept:      "application/json",
        data:        JSON.stringify({ "name": jQuery("#name").val() })
    }).done(function () {
        window.location.replace("/my/dashboard");
    }).fail(function () {
        jQuery("#message")
            .addClass("failure")
            .append("<p>Please provide a token name</p>")
            .fadeIn(250);
    });
}

jQuery(document).ready(function (){
    jQuery(".hide-for-javascript").removeClass("hide-for-javascript");
    jQuery("#save").on("click", function (event) { save_session ("{{session.uuid}}"); });
});
