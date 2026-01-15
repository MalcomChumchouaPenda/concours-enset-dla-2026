
$(document).ready(function() {

    // desactivation des choix
    $('#region_origine_id').attr('disabled', 'disabled');
    $('#departement_origine_id').attr('disabled', 'disabled');
    // $('#option_id option[value=""]').attr('disabled', 'disabled');
    // $('#classe_id option[value=""]').attr('disabled', 'disabled');

    console.log(filiere_choice)

    // fonctions de mise a jour des options
    function updateOptions(choice) {
        var propagate = false;
        var correctOptions = $('#option_id option[value^="' + choice + '"]');
        var incorrectOptions = $('#option_id option:not([value^="' + choice + '"])');
        var choiceOption = $('#option_id option[value=""]');
        var field = $('#option_id');
        
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

    // fonctions de mise a jour des classes
    function updateClasses(choice) {
        var correctOptions = $('#classe_id option[value^="' + choice + '"]');
        var incorrectOptions = $('#classe_id option:not([value^="' + choice + '"])');
        var choiceOption = $('#classe_id option[value=""]');
        var field = $('#classe_id');
        
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

    // fonctions de mise a jour des departements
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

    // mise a jours
    
    // var filiere_choice = $('#filiere_id').val();
    // var option_choice = $('#option_id').val();
    // var classe_choice = $('#classe_id').val();

    // console.log(filiere_choice);
    // console.log(option_choice);
    // console.log(classe_choice);

    // if (filiere_choice != '' & option_choice == '') {
    //     var propagate = updateOptions(filiere_choice);
    //     if (propagate) {
    //         updateClasses(filiere_choice);
    //     } else {
    //         updateClasses('');
    //     }
    // }

    // precedures evenementielles

    // $('#filiere_id').change(function () {
    //     choice = $(this).val();
    //     var propagate = updateOptions(choice);
    //     if (propagate) {
    //         updateClasses(choice);
    //     } else {
    //         updateClasses('');
    //     }
    // })

    // $('#option_id').change(function () {
    //     choice = $(this).val();
    //     updateClasses(choice);
    // })


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