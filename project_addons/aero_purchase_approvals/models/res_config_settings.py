# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approver_responsible_id = fields.Many2one('res.users', string="Approver Responsible", readonly=False, related='company_id.approver_responsible_id')
