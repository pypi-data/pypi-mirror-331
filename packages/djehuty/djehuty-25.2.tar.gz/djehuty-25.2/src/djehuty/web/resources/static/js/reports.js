jQuery(document).ready(function () {
    jQuery(".hide-for-javascript").removeClass("hide-for-javascript");
    jQuery("#reports-table").DataTable({
        "order": [],
        columnDefs: [{ orderable: false,  targets: 0 }],
        pageLength: 25
    });
    jQuery("#reports-table").show();
});
