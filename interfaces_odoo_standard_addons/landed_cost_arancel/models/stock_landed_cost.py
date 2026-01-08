from odoo import _, api, fields, models,tools
from odoo.exceptions import UserError, ValidationError




class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    freight_cost=fields.Monetary(string="Costo de flete")
    insurance_cost=fields.Monetary(string="Costo de seguro")
    

    def get_valuation_lines(self):
        self.ensure_one()
        lines = []

        for move in self._get_targeted_move_ids():
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.cost_method not in ('fifo', 'average') or move.state == 'cancel' or not move.product_qty:
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty,
                'porcentaje_arancel':move.product_id.porcentaje_arancel or 0
            }
            lines.append(vals)

        if not lines:
            target_model_descriptions = dict(self._fields['target_model']._description_selection(self.env))
            raise UserError(_("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average costing method.", target_model_descriptions[self.target_model]))
        return lines
    
    
    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            # rounding = cost.currency_id.rounding
            rounding = 0.01
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            total_porc_arancel=0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)
                former_cost = val_line_values.get('former_cost', 0.0)
                former_porc_arancel = val_line_values.get('porcentaje_arancel', 0.0)

                # round this because former_cost on the valuation lines is also rounded
                total_cost += cost.currency_id.round(former_cost)
                total_porc_arancel += former_porc_arancel

                total_line += 1
            for line in cost.cost_lines:
                value_split = 0.0
                #Fix para error de valoracion de productos
                total_value_da=0
                for valuation in cost.valuation_adjustment_lines:
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_current_cost_price' and total_cost and line.price_unit_da:
                            if self.freight_cost or self.insurance_cost:
                                total_value_da+=(valuation.former_cost/total_cost) * (self.freight_cost + self.insurance_cost+ total_cost) * valuation.porcentaje_arancel /100
                            else:
                                total_value_da+=(valuation.former_cost/total_cost) *  valuation.porcentaje_arancel /100
                                
                #######
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost and line.price_unit_without_da:
                            per_unit = (line.price_unit_without_da / total_cost)
                            value = valuation.former_cost * per_unit
                        elif line.split_method == 'by_current_cost_price' and total_cost and line.price_unit_da:
                            if total_value_da:
                                if self.freight_cost or self.insurance_cost:
                                    v=(valuation.former_cost/total_cost) * (self.freight_cost + self.insurance_cost+ total_cost) * valuation.porcentaje_arancel /100
                                else:
                                    v=(valuation.former_cost/total_cost) * valuation.porcentaje_arancel /100
                                    
                                factor=v/total_value_da
                                value=factor*line.price_unit_da
                            else:
                                raise ValidationError("No se puede realizar el cálculo debido a que posee lineas de costo de derecho aduanero"  
                                                      " pero ningun articulo con porcentaje arancelario establecido. Favor revisar sus lineas de costo"
                                                      " o los productos de la transferencia asociada a este coste de destino.")
                        else:
                            value = (line.price_unit / total_line)

                        if rounding:
                            value = tools.float_round(value, precision_rounding=rounding, rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True

class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    es_derecho_aduanero=fields.Boolean(string="Es derecho aduanero",related="product_id.es_derecho_aduanero")
    price_unit_da=fields.Monetary(string="Monto derecho aduanero",compute="compute_monto_derecho_aduanero")
    price_unit_without_da=fields.Monetary(string="Monto sin derecho aduanero",compute="compute_monto_derecho_aduanero")

    @api.depends('product_id','product_id.es_derecho_aduanero','price_unit')
    @api.onchange('product_id','product_id.es_derecho_aduanero','price_unit')
    def compute_monto_derecho_aduanero(self):
        for record in self:
            if record.product_id.es_derecho_aduanero:
                record.price_unit_da=record.price_unit
                record.price_unit_without_da=0
            else:
                record.price_unit_da=0
                record.price_unit_without_da=record.price_unit
class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    porcentaje_arancel=fields.Float(string="Arancel",default=0)
    monto_arancel=fields.Monetary(string="Monto arancel",default=0)
    
    former_cost = fields.Float(
        'Original Value')
    additional_landed_cost = fields.Float(
        'Additional Landed Cost')
    final_cost = fields.Float(
        'New Value', compute='_compute_final_cost',
        store=True)