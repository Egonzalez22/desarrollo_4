from odoo import fields, api, models, exceptions


class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    def _get_last_sequence(self, relaxed=False, with_prefix=None, lock=True):
        result = super(SequenceMixin, self)._get_last_sequence(relaxed, with_prefix, lock)
        if not result and self._name == 'account.move':
            journal_timbrado = self.journal_id.timbrados_ids.filtered(lambda x: x.tipo_documento == self.move_type)
            if journal_timbrado:
                journal_timbrado = journal_timbrado[0]
                return '-'.join([
                    journal_timbrado.nro_establecimiento.rjust(3, '0'),
                    journal_timbrado.nro_punto_expedicion.rjust(3, '0'),
                    str(journal_timbrado.proximo_numero - 1).rjust(7, '0')
                ])
        return result
