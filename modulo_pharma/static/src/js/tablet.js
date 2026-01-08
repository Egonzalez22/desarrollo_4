/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import Tablet from "@mrp_workorder/components/tablet";

patch(Tablet.prototype, "modulo_pharma.TabletPatch", {

    openResultadosTree() {
        return new Promise(resolve => {
                this.env.services.action.doAction(
                    {
                        name: this.env._t("Resultados"),
                        type: 'ir.actions.act_window',
                        view_mode: 'list, form',
                        views: [[false, 'list'],[false, 'form']],
                        target: 'new',
                        res_model: this.data['res_model'],
                        domain: [['id', 'in', this.data['resultados']]],
                        res_id: false
                    },
                    {
                        additionalContext: {
                            'default_workorder_id': this.workorderId
                        },
                        onClose: resolve,
                    },
                );
            });
    },
    get views() {
        // Obtén las vistas originales
        const originalViews = this._super ? this._super() : this.constructor.prototype.views;

        // Agrega la nueva vista personalizada
        const customViews = this.data['resultados'].map((resultadoId) => {
            return {
                type: 'workorder_form',
                mode: 'edit',
                resModel: this.data['res_model'],
                viewId: this.viewsId.resultados_view,
                resId: resultadoId,
                display: { controlPanel: false },
                workorderBus: this.workorderBus,
                onRecordChanged: async (rootRecord) => {
                    await rootRecord.save();
                    this.render(true);
                },
            };
        });

        // Devuelve las vistas originales más la personalizada
        return { ...originalViews, custom: customViews };
    },
});
