odoo.define('fe_py_pos.PartnerDetailsEdit', function (require) {
    'use strict';

    const { _t } = require("web.core");
    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const CustomPartnerDetailsEdit = (PartnerDetailsEdit) => class CustomPartnerDetailsEdit extends PartnerDetailsEdit {
        setup() {
            super.setup();
            this.intFields = ["country_id", "state_id", "city_id", "property_product_pricelist"];

            this.changes = {
                ...this.changes,
                tipo_documento: this.props.partner.tipo_documento || "",
                contribuyente: this.props.partner.contribuyente || "",
                nro_documento: this.props.partner.nro_documento || "",
                city_id: this.props.partner.city_id && this.props.partner.city_id[0],
            };

            // Cargamos el select de city con todas las ciudades. Luego se filtrará por state (Se pude implementar busqueda por ajax, pero odoo pre-carga todos los datos)
            this.cities = this.env.pos.cities

            // Validaciones para visibilidad de campos de RUC y Nro de documento
            let es_contribuyente = this.props.partner.contribuyente || false;
            this.showVatField = es_contribuyente;
            this.showNroDocumentoField = !es_contribuyente;

            // Si es contribuyente, forzamos a que el tipo de documento sea RUC
            if (es_contribuyente) {
                this.changes.tipo_documento = "0";
            }
        }

        saveChanges() {
            const processedChanges = {};
            for (const [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
            if (
                processedChanges.state_id &&
                this.env.pos.states.find((state) => state.id === processedChanges.state_id).country_id[0] !== processedChanges.country_id
            ) {
                processedChanges.state_id = false;
            }

            if (
                (!this.props.partner.name && !processedChanges.name) ||
                processedChanges.name === ""
            ) {
                return this.showPopup("ErrorPopup", {
                    title: _t("A Customer Name Is Required"),
                });
            }

            /**
             * Validaciones personalizadas
             */
            const es_contribuyente = processedChanges["tipo_documento"] == "0"
            // Si es contribuyente, eliminamos el tipo_documento
            if (es_contribuyente) {
                delete processedChanges["tipo_documento"]
                processedChanges["contribuyente"] = true
            } else {
                processedChanges["contribuyente"] = false
            }

            // Si el cliente no es contribuyente, debe tener un tipo y nro de documento
            if (processedChanges.contribuyente === false || this.props.partner.contribuyente === false) {
                // Si se selecciona que no es contribuyente, se debe obviar la validación del RUC
                processedChanges['obviar_validacion'] = true;

                if (!processedChanges.tipo_documento && !this.props.partner.tipo_documento) {
                    return this.showPopup('ErrorPopup', {
                        title: _t('El Tipo de Documento es requerido'),
                    });
                }
                if (!processedChanges.nro_documento && !this.props.partner.nro_documento) {
                    return this.showPopup('ErrorPopup', {
                        title: _t('El nro de documento es requerido'),
                    });
                }

                // 153259: Se copia el dato del nro de documento al campo VAT
                if (!processedChanges.vat && !this.props.partner.vat) {
                    processedChanges.vat = processedChanges.nro_documento || this.props.partner.nro_documento;
                }

            } else {

                // Si el cliente es contribuyente, debe tener vat
                if (!processedChanges.vat && !this.props.partner.vat) {
                    return this.showPopup('ErrorPopup', {
                        title: _t('El RUC es requerido'),
                    });
                }
            }


            processedChanges.id = this.props.partner.id || false;
            this.trigger('save-changes', { processedChanges });
        }

        async captureChange(event) {
            await super.captureChange(event);
            const { name, value } = event.target;

            // Filtramos las ciudades de acuerdo al state
            if (name === 'state_id') {
                await this.onChangeState(parseInt(value));
            }

            // Si se cambia el tipo de documento, cambiamos la visibilidad de campos nro_documento/vat
            // Acá no se verifica por el campo "contribuyente" porque este campo no se carga desde el formulario
            if (name === 'tipo_documento') {
                // 0 = RUC: Ocultar nro_documento
                if (value == '0') {
                    this.showVatField = true;
                    this.showNroDocumentoField = false;
                } else {
                    this.showVatField = false;
                    this.showNroDocumentoField = true;
                }
                this.render();
            }
        }

        async onChangeState(stateId) {
            this.cities = this.env.pos.cities.filter(city => city.state_id[0] === stateId);
            this.render();
        }
    }
    Registries.Component.extend(PartnerDetailsEdit, CustomPartnerDetailsEdit);

});