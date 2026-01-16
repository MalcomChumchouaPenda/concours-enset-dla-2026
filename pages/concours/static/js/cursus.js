
        $(document).ready(function() {
            // Ajouter une nouvelle ligne
            $('#add_row').click(function() {
            // Cloner la première ligne
            var newRow = $('#cursus_table tbody tr:first').clone();
            
            // Vider les champs de la nouvelle ligne
            newRow.find('input').val('');
            
            // Ajouter la ligne clonée à la fin du tableau
            $('#cursus_table tbody').append(newRow);
            
            // Mettre à jour les noms des champs pour qu'ils soient uniques
            updateFieldNames();
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