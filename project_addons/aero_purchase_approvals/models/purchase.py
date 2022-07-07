# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from xmlrpc.client import Boolean
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

class PurchaseOrderLine(models.Model):
    """
    Purchase Order Line
    """
    _inherit = "purchase.order.line"

    error_message = fields.Text("Error Message", default="")

    # Override string value
    date_planned = fields.Datetime(string="Current Delivery Date")
    date_initial_delivery = fields.Datetime(string="Initial Delivery Date")

    def write(self, vals):
        """
        We can only modify specific field for purchase order that are in the 'to approve' state.
        """
        if self._context.get("purchase_bypass_check", False) is False:
            unlock_fields = ["date_planned", "date_order", "product_qty", "state"]
            qty_unlock_fields = ["taxes_id", "account_analytic_id", "analytic_tag_ids", "product_packaging_id", "cost_center_id"]

            for rec in self.filtered(lambda x: x.state in ["to approve"]):
                cleaned_vals = {key:  vals[key] for key in vals if key in unlock_fields}

                # Product_qty can only decrease for PO in the 'to approve' state
                if "product_qty" in cleaned_vals and float_compare(cleaned_vals["product_qty"], rec.product_qty, precision_rounding=rec.product_uom.rounding) > 0:
                    raise UserError("You cannot increase product quantity on 'to approve' purchase order")

                if "product_qty" in cleaned_vals:
                    product_cleans_vals = {key: vals[key] for key in vals if key in qty_unlock_fields}
                    if product_cleans_vals:
                        cleaned_vals.update(product_cleans_vals)

                lock_field = []
                for field in vals:
                    change = False

                    # transcode to compare actual value with new value
                    if isinstance(vals[field], list):
                        new_value = vals[field][0][2] if vals[field] and len(vals[field][0]) > 1 else False
                        if new_value:
                            new_value = new_value[0] if isinstance(new_value, list) and new_value else False
                        else:
                            new_value = False
                    else:
                        new_value = vals[field]

                    # if at least one line have a current value different than the new value then there is a change
                    current_value = rec[field] # todo if field is record than current_value = pol[field].id otherwise current_value = pol[field]
                    if current_value != new_value:
                        change = True

                    if field not in cleaned_vals.keys() and change and field != "product_qty":
                        lock_field.append(field)

                if lock_field:
                    error_message = f"You cannot modify {', '.join(lock_field)} on purchase order line to approve."
                    cleaned_vals.update({
                        "error_message": error_message,
                    })
                super(PurchaseOrderLine, rec).write(cleaned_vals)
            return super(PurchaseOrderLine, self.filtered(lambda x: x.state not in ["to approve"])).write(vals)
        return super(PurchaseOrderLine, self).write(vals)


class PurchaseOrder(models.Model):
    """
    Purchase Order
    """
    _inherit = "purchase.order"

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

    approval_request_ids = fields.One2many('approval.request', 'purchase_order_id')
    approval_request_count = fields.Integer('Approval request count', compute='_compute_approval_request_count')
    user_id = fields.Many2one('res.users', string='Requester', index=True, tracking=True, required=True,
                              check_company=True, default=False)
    date_planned = fields.Datetime(string="Current Delivery Date",tracking=True)
    date_initial_delivery = fields.Datetime(string="Initial Delivery Date", required=True,tracking=True)
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', states={'done': [('readonly', True)]}, required=True,
                                  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")

    show_display_error_message = fields.Boolean("Show Error Message", compute="_compute_display_error_message")
    display_error_message = fields.Text("Display Error Message", compute="_compute_display_error_message")
    error_message = fields.Text("Error Message")
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', states=Purchase.READONLY_STATES,
                                      required=True, default=_default_picking_type,
                                      domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
                                      help="This will determine operation type of incoming shipment")

    def _compute_display_error_message(self) -> None:
        """
        Compute display error message value
        :return: None
        """
        for rec in self:
            error_message = rec.error_message and f"{rec.error_message}\n" or ""
            for line in rec.order_line.filtered(lambda x: x.error_message):
                error_message += line.error_message + "\n"
            rec.display_error_message = error_message
            rec.show_display_error_message = error_message and True or False

            rec.with_context({"purchase_bypass_check": True}).write({"error_message": ""})
            rec.order_line.with_context({"purchase_bypass_check": True}).write({"error_message": ""})   

    def write(self, vals):
        """
        Lock fields for purchase order to validate
        """
        unlock_fields = ["date_planned", "date_approve", "date_order", "order_line", "state", "mail_reminder_confirmed"]

        if self._context.get("purchase_bypass_check", False) is False:
            for rec in self.filtered(lambda x: x.state in ["to approve"]):
                cleaned_vals = {key: vals[key] for key in vals if key in unlock_fields}

                lock_field = []
                for field in vals:
                    if field not in unlock_fields:
                        lock_field.append(field)
                if lock_field:
                    error_message = f"You cannot modify {', '.join(lock_field)} on purchase order to approve."
                    cleaned_vals.update({
                        "error_message": error_message,
                    })
                super(PurchaseOrder, rec).write(cleaned_vals)
            return super(PurchaseOrder, self.filtered(lambda x: x.state not in ["to approve"])).write(vals)
        return super(PurchaseOrder, self).write(vals)

    def action_view_approval_request(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "approval.request",
            "domain": [('id', 'in', self.approval_request_ids.ids)],
            "context": {"create": False},
            "name": "Approval Request",
            'view_mode': 'kanban,tree,form',
        }
        return result

    @api.onchange("date_initial_delivery")
    def onchange_date_initial_delivery(self) -> None:
        """
        Sync <purchase.order.line> date_initial_delivery with purchase_order value.
        :return: None
        """
        for rec in self:
            for line_id in rec.order_line:
                line_id.date_initial_delivery = rec.date_initial_delivery

            if rec.state not in ["purchase", "cancel", "done"]:
                rec.date_planned = rec.date_initial_delivery

    @api.depends('approval_request_ids')
    def _compute_approval_request_count(self):
        for purchase in self:
            purchase.approval_request_count = len(purchase.approval_request_ids)

    def _get_approval_apply_category(self):
        """Return all applicable approval.category apply on the purchase order """
        # convert purchase order in company's currency
        amount_total = self.currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(), round=False)
        amount_untaxed = self.currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(), round=False)
        approval_category_ids = self.env['approval.category'].search([('approval_type', '=', 'purchase_approbation')])
        apply_approval_category_ids = self.env['approval.category']
        for approval_category in approval_category_ids:
            if approval_category.include_vat and float_compare(amount_total, approval_category.po_minimum_amount, precision_rounding=self.currency_id.rounding) >= 0:
                apply_approval_category_ids |= approval_category
            if not approval_category.include_vat and float_compare(amount_untaxed, approval_category.po_minimum_amount, precision_rounding=self.currency_id.rounding) >= 0:
                apply_approval_category_ids |= approval_category
        return apply_approval_category_ids

    def button_confirm(self):
        """ Overide odoo standard validation
        confirm rfq create approval request if needed
        """
        purchase_with_approval = self.env['purchase.order']
        for order in self:

            # Check mandatory filed before confirm
            if len(order.order_line) == 0:
                raise UserError("You cannot confirm purchase order without line")
            if order.order_line.filtered(lambda x: x.price_unit == 0 or x.product_qty == 0):
                raise UserError("You cannot confirm purchase order with no price unit or no null quantity")
            if order.order_line.filtered(lambda x: not x.cost_center_id):
                raise UserError("You cannot confirm, there are missing cost centers on PO lines")


            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()

            # find category apply on purchase order
            apply_approval_category_ids = order._get_approval_apply_category()
            approvers = self.env['res.users']
            for approval_category in apply_approval_category_ids:
                approvers |= approval_category.get_approver_to_notify(order.user_id)

            # create approval request if needed
            # It might not have approvers depending on who is the requester.
            if apply_approval_category_ids and approvers:
                apply_approval_category_ids = apply_approval_category_ids.sorted(lambda category: (category.po_minimum_amount, -1 * category.sequence), reverse=True)
                request_id = self.env['approval.request']
                request_id = request_id.sudo().create({
                    'name': ("Purchase %s" % order.name),
                    'request_owner_id': order.user_id.id,
                    'category_id': apply_approval_category_ids[0].id,
                    'purchase_order_id': order.id
                })
                # submit request
                request_id.sudo().action_confirm()
                order.write({'state': 'to approve'})
                purchase_with_approval |= order
        return super(PurchaseOrder, self - purchase_with_approval).button_confirm()

    def reset_to_draft(self, refusal_message:str=None) -> None:
        """
        Reset the order to "draft" and log the refusal message from the approval. 
        :param refusal_message: str 
        :return: None
        """
        self.ensure_one()

        if refusal_message:
            self.message_post(
                body=_(f"Reason for refusal: {refusal_message}"),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )

        self.with_context({
            "purchase_bypass_check": True, 
            "stop_cascade": True
        }).button_cancel()

        self.button_draft()

    def button_cancel(self):
        """
        Cancel purchase order. Cancel linked approval.
        :param stop_cascade: boolean
        :return: None
        """
        res = super(PurchaseOrder, self.with_context({"purchase_bypass_check": True})).button_cancel()

        if self._context.get("stop_cascade", False) is False:
            for rec in self:
                rec.approval_request_ids.with_context({"stop_cascade": True}).action_cancel()
