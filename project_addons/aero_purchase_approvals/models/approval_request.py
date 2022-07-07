# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from xmlrpc.client import Boolean
from odoo import api, Command, fields, models, _


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", copy=False)
    purchase_order_line_ids = fields.One2many('purchase.order.line', related='purchase_order_id.order_line', string="Purchase Order Line")
    currency_id = fields.Many2one('res.currency', related='purchase_order_id.currency_id')
    purchase_order_amount_untaxed = fields.Monetary(string='Untaxed Amount', related='purchase_order_id.amount_untaxed')
    purchase_order_amount_tax = fields.Monetary(string='Tax Amount', related='purchase_order_id.amount_tax')
    purchase_order_amount_total = fields.Monetary(string='Total Amount', related='purchase_order_id.amount_total')

    def action_approve(self, approver=None):
        super(ApprovalRequest, self).action_approve(approver)
        # Approve Purchase Order
        for request in self:
            if request.request_status == 'approved' and request.category_id.approval_type == 'purchase_approbation' and request.purchase_order_id:
                request.purchase_order_id.button_approve()

    def action_refuse(self, approver=None, refusal_message:str=None):
        """
        If no refusal message is set, launch wizard to get it.
        :param refusal_message: string
        """
        self.ensure_one()

        if refusal_message is None: 
            return {
                "name": "Refuse Approval Message",
                "type": "ir.actions.act_window",
                "res_model": "refusal.approve.wizard",
                "view_type": "form",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_approval_id": self.id,
                },
            }   

        self.message_post(
            body= f"Refusal Message: {refusal_message}",
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        res = super(ApprovalRequest, self).action_refuse(approver=approver)
        self.purchase_order_id.reset_to_draft(refusal_message=refusal_message)

        # Notify the requester of the refusal.
        template = self.env.ref('aero_purchase_approvals.email_template_approval_refused')
        template.send_mail(self.id, notif_layout='mail.mail_notification_light', force_send=True)
        return res

    def action_cancel(self) -> None:
        """
        Set to "cancel" and "draft" linked <purchase.order>
        :param cancel_message: 
        :param stop_cascade: bool
        :return: None
        """
        res = super(ApprovalRequest, self).action_cancel()

        # Meaning, this call come from "approval" view and not from <purchase.order>
        if self._context.get("stop_cascade", False) is False:  
            for rec in self:
                rec.purchase_order_id.message_post(
                    body=_("This order has been cancel by an approval."),
                    message_type="comment",
                    subtype_xmlid="mail.mt_note",
                    author_id=self._uid
                )
                rec.purchase_order_id.with_context({"stop_cascade": True}).button_cancel()
        return res

    @api.depends('category_id', 'request_owner_id')
    def _compute_approver_ids(self):
        for request in self:
            super(ApprovalRequest, request)._compute_approver_ids()
            # Overide to compute approval_ids for organisation chart method
            approvers = request.category_id.get_approver_to_notify(request.request_owner_id)
            approver_ids = self.env['approval.approver']
            for approver in approvers:
                approver_ids |= self.env['approval.approver'].create({
                    'user_id': approver.id,
                    'status': 'new',
                    'required': True,
                })
            approver_ids.write({'company_id': self.env.company.id})
            request.approver_ids = approver_ids
