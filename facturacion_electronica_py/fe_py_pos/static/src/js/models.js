odoo.define('fe_py_pos.models', function (require) {
    "use strict";

    const { Order, PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const CustomOrder = (Order) => class CustomOrder extends Order {
        constructor() {
            super(...arguments);
            this.set_to_invoice(true);
        }

    }
    Registries.Model.extend(Order, CustomOrder);

    const CustomPosGlobalState = (PosGlobalState) => class CustomPosGlobalState extends PosGlobalState {

        async _processData(loadedData) {
            await super._processData(loadedData);
            // Cargamos también la ciudad en el pos
            this.cities = loadedData['res.city'];
        }
    }
    Registries.Model.extend(PosGlobalState, CustomPosGlobalState);

    return { CustomOrder, CustomPosGlobalState };
});
