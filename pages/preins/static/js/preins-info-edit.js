
$(document).ready(function() {

    // fonctions de mise a jour des regions
    function updateRegions(choice) {
        var propagate = false;
        var correctOptions = $('#region_origine_id option[value^="' + choice + '"]');
        var incorrectOptions = $('#region_origine_id option:not([value^="' + choice + '"])');
        var choiceOption = $('#region_origine_id option[value=""]');
        var field = $('#region_origine_id');
        
        field.val('');
        if (correctOptions.length == 0 )  {
            field.attr('disabled', 'disabled');
        } else if (correctOptions.length == 1 ) {
            field.val(correctOptions.attr('value'))
            incorrectOptions.hide();
            correctOptions.hide();
            choiceOption.hide();
            field.removeAttr('disabled');
            propagate = true
        } else {
            incorrectOptions.hide();
            correctOptions.show();
            choiceOption.show();
            field.removeAttr('disabled');
        }
        return propagate;
    }

    // fonctions de mise a jour des regions
    function updateDepartements(choice) {
        var correctOptions = $('#departement_origine_id option[value^="' + choice + '"]');
        var incorrectOptions = $('#departement_origine_id option:not([value^="' + choice + '"])');
        var choiceOption = $('#departement_origine_id option[value=""]');
        var field = $('#departement_origine_id');
        
        field.val('');
        if (correctOptions.length == 0 )  {
            field.attr('disabled', 'disabled');
        } else if (correctOptions.length == 1 ) {
            field.val(correctOptions.attr('value'))
            incorrectOptions.hide();
            correctOptions.hide();
            choiceOption.hide();
            field.removeAttr('disabled');
        } else {
            incorrectOptions.hide();
            correctOptions.show();
            choiceOption.show();
            field.removeAttr('disabled');
        }
    }


    // Mise a jour initiale
    var pays = $('#nationalite_id').val()
    var region = $('#region_origine_id').val()
    var dept = $('#departement_origine_id').val()
    console.log(pays)
    console.log(region)
    console.log(dept)
    updateRegions(pays)
    $('#region_origine_id').val(region)
    updateDepartements(region)
    $('#departement_origine_id').val(dept)


    // precedures evenementielles
    $('#nationalite_id').change(function () {
        choice = $(this).val();
        var propagate = updateRegions(choice);
        if (propagate) {
            updateDepartements(choice);
        } else {
            updateDepartements('');
        }
    })

    $('#region_origine_id').change(function () {
        choice = $(this).val();
        updateDepartements(choice);
    })
    
});