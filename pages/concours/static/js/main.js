
$(document).ready(function() {

    // find first invalid feedback
    var firstInvalid = $(this).find('.invalid-feedback').first();
    var firstInvalidCell = firstInvalid.closest('td');
    if (firstInvalidCell.length) {
        var tableContainer = firstInvalidCell.closest('.table-responsive');
        var offset = firstInvalidCell.offset();
        console.log(tableContainer.html())

        // vertical scroll
        $('html, body').animate({
            scrollTop: offset.top - 200  // adjust for spacing
        }, 200) // duration of animation

        // horizontal scroll
        tableContainer.animate({
            scrollLeft: offset.left -tableContainer.offset().left - 100  // adjust for spacing
        }, 200) // duration of animation

    } else if (firstInvalid.length) {
        $('html, body').animate({
            scrollTop: firstInvalid.offset().top - 200  // adjust for spacing
        }, 200) // duration of animation
    }


    // Ajouter une nouvelle ligne du cursus
    $('#add_row').click(function() {
        var newRow = $('#cursus_table tbody tr:first').clone(); // Cloner la première ligne
        newRow.find('input').val(''); // Vider les champs de la nouvelle ligne
        $('#cursus_table tbody').append(newRow); // Ajouter la ligne clonée à la fin du tableau
        updateFieldNames(); // Mettre à jour les noms des champs pour qu'ils soient uniques
    });

    // Supprimer une ligne
    $('#cursus_table').on('click', '.delete-row', function() {
        $(this).closest('tr').remove();
        updateFieldNames();
    });

    // Fonction pour mettre à jour les noms des champs pour chaque ligne
    function updateFieldNames() {
        $('#cursus_table tbody tr').each(function(index) {
            $(this).find('input').each(function() {
                var fieldId = $(this).attr('id').replace('0', index);
                var fieldName = $(this).attr('name').replace('0', index);
                $(this).attr('id', fieldId);
                $(this).attr('name', fieldName);
            });
        });
    }

});