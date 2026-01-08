odoo.define('pos_invoice.InvoiceButton', function (require) {
    const InvoiceButton = require('point_of_sale.InvoiceButton')
    const Registries = require('point_of_sale.Registries')
    const core = require('web.core')
    // addons/point_of_sale/static/src/js/InvoiceButton.js
    // line 26

    const InvoiceButtonCustom = InvoiceButton => class extends InvoiceButton {

        async _downloadInvoice(orderId) {
            try {
                const [orderWithInvoice] = await this.rpc({
                    method: 'read',
                    model: 'pos.order',
                    args: [orderId, ['account_move']],
                    kwargs: { load: false },
                });
                if (orderWithInvoice && orderWithInvoice.account_move) {
                    debugger;
                    // Establecemos el tipo de documento seleccionado en la configuracion
                    let default_invoice_template = 'account.account_invoices';

                    if(this.env.pos.config.tipo_documento_factura == 'autoimpresor'){
                        default_invoice_template = 'factura_autoimpresor.factura_report_action';
                    }
                    if(this.env.pos.config.tipo_documento_factura == 'electronico'){
                        default_invoice_template = 'facturacion_electronica_py.factura_report_action';
                    }

                    await this.env.legacyActionManager.do_action(default_invoice_template, {
                        additional_context: {
                            active_ids: [orderWithInvoice.account_move],
                        },
                    });
                }
            } catch (error) {
                if (error instanceof Error) {
                    throw error;
                } else {
                    // NOTE: error here is most probably undefined
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('Unable to download invoice.'),
                    });
                }
            }
        }

    }

    Registries.Component.extend(InvoiceButton, InvoiceButtonCustom)
});
