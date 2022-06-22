from odoo import api, models, fields


class KyoSaleOrder(models.Model):
    _inherit = 'sale.order'

    spreadsheet_id = fields.Many2one('documents.document', string='Excel Sheet')

    def open_spreadsheet(self):
        if not self.spreadsheet_id:
            self.spreadsheet_id = self.create_spreadsheet()

        return {
            'type': "ir.actions.client",
            'tag': "action_open_spreadsheet",
            'params': {
                'spreadsheet_id': self.spreadsheet_id.id,
            },
        }

    def create_spreadsheet(self):
        return (
            self.env["documents.document"].create({
                "raw": r"{}",
                "handler": "spreadsheet",
                "mimetype": "application/o-spreadsheet",
            })
        )
