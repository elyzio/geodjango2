// Municipality → AdministrativePost
// $("#id_administrativepost").prop("disabled", true);
// $("#id_village").prop("disabled", true);
// $("#id_aldeia").prop("disabled", true);
$("#id_municipality").change(function () {
  var municipalityId = $(this).val();
  // Reset and disable all lower-level selects
  $("#id_administrativepost")
    .html('<option value="">--Select Administrative--</option>');
  $("#id_village")
    .html('<option value="">----------</option>');
  $("#id_aldeia")
    .html('<option value="">----------</option>');
  if (municipalityId) {
    $.ajax({
      url: "{% url 'ajax_load_administrativeposts' %}",
      data: { municipality_id: municipalityId },
      success: function (data) {
        $.each(data, function (index, item) {
          $("#id_administrativepost").append(
            $("<option></option>").val(item.id).text(item.name)
          );
        });
        $("#id_administrativepost").prop("disabled", false);
      },
    });
  }
});

// AdministrativePost → Village
$("#id_administrativepost").change(function () {
  var administrativepostId = $(this).val();
  $("#id_village")
    .html('<option value="">--Select Village--</option>');
  $("#id_aldeia")
    .html('<option value="">----------</option>');

  if (administrativepostId) {
    $.ajax({
      url: "{% url 'ajax_load_villages' %}",
      data: { administrativepost_id: administrativepostId },
      success: function (data) {
        $.each(data, function (index, item) {
          $("#id_village").append(
            $("<option></option>").val(item.id).text(item.name)
          );
        });
        $("#id_village").prop("disabled", false);
      },
    });
  }
});

// Village → Aldeia
$("#id_village").change(function () {
  var villageId = $(this).val();
  $("#id_aldeia")
    .html('<option value="">--Select Aldeia--</option>');

  if (villageId) {
    $.ajax({
      url: "{% url 'ajax_load_aldeias' %}",
      data: { village_id: villageId },
      success: function (data) {
        $.each(data, function (index, item) {
          $("#id_aldeia").append(
            $("<option></option>").val(item.id).text(item.name)
          );
        });
        $("#id_aldeia").prop("disabled", false);
      },
    });
  }
});
