odoo.define('pos_invoice.invoice_button', function(require) {
	const InvoiceButton = require('point_of_sale.InvoiceButton')
	const Registries = require('point_of_sale.Registries')

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
                    await this.env.legacyActionManager.do_action('factura_autoimpresor.factura_report_action', {
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
})
