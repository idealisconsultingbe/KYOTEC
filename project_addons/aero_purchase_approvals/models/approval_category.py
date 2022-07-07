# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[('purchase_approbation', 'Purchase Approbation')])
    approval_method = fields.Selection([
        ('standard', 'standard'),
        ('organization_chart', 'organization chart'),]
        , default='standard', string='Approval Method', required=True, copy=False)
    request_job_approval_position_ids = fields.One2many('request.job.approval.position', 'approval_category_id', string='Job Level', copy=False)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True, readonly=True)
    po_minimum_amount = fields.Monetary(string='PO Minimum Amount', currency_field='currency_id')
    include_vat = fields.Boolean(string='VAT Include', default=False)
    sequence = fields.Integer(string='Sequence')

    def get_approver_to_notify(self, requester):
        self.ensure_one()
        approvers = self.env['res.users']
        # Overide to compute approval_ids for organisation chart method
        if self.approval_method == 'organization_chart':
            # browse employee flowchart
            # search job_approval_position_id in employee flowchart
            employee = requester.employee_id
            for request_approval_position in self.request_job_approval_position_ids:
                # Add job position
                approvers |= employee._get_user_position(position=request_approval_position.job_approval_position_id)

            # Every PO most be approved, if no approver has been found add the N+1.
            if not approvers and employee.parent_id:
                approvers |= employee.parent_id.user_id

            # If still no approver than add the approver responsible.
            if not approvers:
                approvers |= self.company_id.approver_responsible_id
            # The requester should always be in the approver + another person
            approvers |= requester
        return approvers
