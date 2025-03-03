jQuery(document).ready(function () {
    jQuery(".hide-for-javascript").removeClass("hide-for-javascript");
    jQuery("#table-unpublished").DataTable({
        columnDefs: [{ type: 'file-size', targets: 2 },
                     { orderable: false,  targets: 4 }],
        order: [[3, 'desc']]
    });
    jQuery("#table-unpublished").show();
    jQuery("#table-unpublished-loader").remove();

    jQuery("#table-published").DataTable({
        columnDefs: [{ type: 'file-size', targets: 2 }],
        order: [[3, 'desc']]
    });
    jQuery("#table-published").show();
    jQuery("#table-published-loader").remove();

    jQuery("#table-review").DataTable({
        columnDefs: [{ type: 'file-size', targets: 2 }],
        order: [[3, 'desc']]
    });
    jQuery("#table-review").show();
    jQuery("#table-review-loader").remove();
});
