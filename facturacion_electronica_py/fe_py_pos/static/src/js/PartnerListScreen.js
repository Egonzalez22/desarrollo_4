odoo.define('fe_py_pos.PartnerListScreen', function (require) {
    'use strict';

    const PartnerListScreen = require('point_of_sale.PartnerListScreen');
    const Registries = require('point_of_sale.Registries');

    const CustomPartnerListScreen = (PartnerListScreen) => class CustomPartnerListScreen extends PartnerListScreen {
        consultarRUC() {
            // TODO: Se valida el RUC y se escribe en el modelo de ser necesario, pero todavía no se actualiza el dato del partner en el state actual
            // El XML si se genera con los datos actualizados
            const partner = this.state.selectedPartner;

            if (partner) {
                this.rpc({
                    model: 'res.partner',
                    method: 'action_validar_ruc_sifen',
                    args: [partner.id],
                }).then(result => {
                    this.showPopup('ConfirmPopup', {
                        title: this.env._t('Validado correctamente'),
                        body: result.result,
                    });
                });
            }
        }
    }
    Registries.Component.extend(PartnerListScreen, CustomPartnerListScreen);

});