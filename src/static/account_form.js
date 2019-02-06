
var conditional_fields = $("#1-email_address");
if (!$("#id_1-forward").prop('checked') === true) {
  conditional_fields.hide();
}

$("#id_1-forward").change(function() {
    if ($(this).prop('checked') === true) {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
    }
});