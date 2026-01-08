odoo.define('factura_multi_pago.auto_save', function(require) {
    let focus
    function clickSave() {
        var inp = document.getElementsByTagName('input')
        focus = false
        for (var i = 0; i < inp.length; i++) {
            var isFocused = (document.activeElement === inp[i])
            if (isFocused) {
                focus = true
            }
        }

        const breadcumbLink = document.querySelector('.breadcrumb-item a')
        if (
            !document.querySelector('.o_form_status_indicator_buttons.d-flex.invisible') &&
            !focus && breadcumbLink &&
            breadcumbLink.textContent == 'Recibo de cliente'
        ) {
            try {
                console.log('save')
                document.querySelector('.o_form_button_save').click()
            } catch {
                console.log('error')
            }
        }
        setTimeout(clickSave, 5000)
    }
    clickSave()

    /*
    var FormController = require('web.FormController')
    var core = require('web.core')

    FormController.include({
        events: {
            'change input': '_onChange',
        },

        _onChange: function (event) {
            console.log("value changed!")
        },

        _onFieldChanged: function (event) {
            this._super.apply(this, arguments)
        },
    })
    */
});
