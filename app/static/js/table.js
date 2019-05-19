$(document).ready(function () {
    $('#table_id').DataTable({
        "language": {
            "decimal": "",
            "emptyTable": "Brak wynikow dla podanego zapytania",
            "info": "Rekordy od _START_ do _END_ z _TOTAL_ wynikow.",
            "infoEmpty": "Brak wynikow",
            "infoFiltered": "(wyfiltrowane z _MAX_ rekordow)",
            "infoPostFix": "",
            "thousands": ",",
            "lengthMenu": "Pokaz _MENU_ rekordow",
            "loadingRecords": "Ladowanie...",
            "processing": "Przetwarzanie...",
            "search": "Wyszukaj:",
            "zeroRecords": "Brak wynikow",
            "paginate": {
                "first": "Poczatek",
                "last": "Koniec",
                "next": "Dalej",
                "previous": "Do tylu"
            },
            "aria": {
                "sortAscending": ": aktywuj by sortowac rosnaco",
                "sortDescending": ": aktywuj by sortowac malejaco"
            }
        }
    });
});
