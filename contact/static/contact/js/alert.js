function sweetConfirm(elt, config) {
    Swal.fire(config)
        .then((result) => {
            if (result.isConfirmed) {
                htmx.trigger('#bulk-delete', 'sweet:confirmed', {});
            }
        });
}

function fireModal(source) {
    Swal.fire({
        title: 'Delete these contacts?',
        showCancelButton: true,
        confirmButtonText: 'Delete'
    }).then((result) => {
        if (result.isConfirmed) {
            htmx.ajax('DELETE', '/contacts', {source: source, target: document.body})
        }
    });
}