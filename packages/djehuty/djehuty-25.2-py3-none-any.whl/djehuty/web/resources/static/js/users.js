function clear_accounts_cache (event) {
    if (event !== null) {
        event.preventDefault();
        event.stopPropagation();
    }
    jQuery.ajax({
        url:         "/v3/admin/accounts/clear-cache",
        type:        "GET",
        accept:      "application/json",
    }).done(function () { location.reload();
    }).fail(function () {
        show_message ("failure", "<p>Failed to clear the accounts cache.</p>");
    });
}

jQuery(document).ready(function () {
    jQuery(".hide-for-javascript").removeClass("hide-for-javascript");
    jQuery("#users-table").DataTable({
        columnDefs: [{ orderable: false,  targets: 3 }],
        pageLength: 25
    });
    jQuery("#users-table").show();
    jQuery("#remove-cache").on("click", function (event) {
        clear_accounts_cache (event);
    });
});
