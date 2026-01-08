from odoo import _, api, fields, models,exceptions


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    grouped_landed_cost_ids=fields.Many2many('stock.landed.cost',string="Grouped landed costs",copy=False)

    @api.depends('line_ids', 'line_ids.is_landed_costs_line','grouped_landed_cost_ids')
    def _compute_landed_costs_visible(self):
        for account_move in self:
            if account_move.landed_costs_ids or account_move.grouped_landed_cost_ids:
                account_move.landed_costs_visible = False
            else:
                account_move.landed_costs_visible = any(line.is_landed_costs_line for line in account_move.line_ids)

    def action_view_landed_costs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        domain = [('id', 'in', self.landed_costs_ids.ids+self.grouped_landed_cost_ids.ids)]
        context = dict(self.env.context, default_vendor_bill_id=self.id)
        views = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_tree2').id, 'tree'), (False, 'form'), (False, 'kanban')]
        return dict(action, domain=domain, context=context, views=views)

    def button_create_landed_costs(self):

        if len(self)==1:
            return super(AccountMove,self).button_create_landed_costs()
        else:
            not_landed=False
            for record in self:
                if any(record.line_ids.mapped('is_landed_costs_line')):
                    continue
                else:
                    not_landed=True
                    break
            if not_landed:
                raise exceptions.ValidationError('Alguna de las facturas no contiene costos en destino')
                
            if any(self.filtered(lambda x:x.state!='posted')):
                raise exceptions.ValidationError('Las facturas seleccionadas deben estar publicadas')
            if any(self.mapped('landed_costs_ids')) or any(self.mapped('grouped_landed_cost_ids')):
                raise exceptions.ValidationError('Ya existen costos en destino para alguna de las facturas seleccionadas')
            
            cost_lines=[]
            landed_costs_lines=[]
            move_ids=[]
            for move in self:
                # Agregamos el ID de cada linea de la factura que sea de costo en destino
                for line in move.line_ids.filtered(lambda line: line.is_landed_costs_line):
                    landed_costs_lines.append(line.id)

                move_ids.append(move.id)
            move_line_ids=self.env['account.move.line'].browse(landed_costs_lines)
            products=move_line_ids.mapped('product_id')
            for product in products:
                price_unit=0
                for cost_line in move_line_ids.filtered(lambda x:x.product_id==product):
                    balance = abs(cost_line.balance)
                    amount_currency = abs(cost_line.amount_currency)
                    if balance > 0 and amount_currency > 0:
                        currency_rate = balance / amount_currency
                    else:
                        currency_rate = 1
                    price_unit+=currency_rate*cost_line.price_subtotal
                line={
                        'product_id': product.id,
                        'name': product.name,
                        'account_id': product.product_tmpl_id.get_product_accounts()['stock_input'].id,
                        'price_unit': price_unit,
                        'split_method': product.split_method_landed_cost or 'equal',
                    }
                cost_lines.append((0,0,line))
            landed_costs = self.env['stock.landed.cost'].create({
                'vendor_bill_ids': [(6,0,move_ids)],
                'cost_lines': cost_lines,
            })
            if landed_costs:
                self.write({'grouped_landed_cost_ids':[(6,0,landed_costs.ids)]})
            action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
            return dict(action, view_mode='form', res_id=landed_costs.id, views=[(False, 'form')])
