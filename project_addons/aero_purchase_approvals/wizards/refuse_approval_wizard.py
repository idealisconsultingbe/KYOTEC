from odoo import api, exceptions, fields, models, _


class RefuseApprovalWizard(models.TransientModel):
    """
    Refuse Approval Wizard
    """
    _name = "refusal.approve.wizard"
    _description = "Wizard allowing to indicates a reason for the approbation refusal"

    refusal_message = fields.Text("Message")
    approval_id = fields.Many2one("approval.request", "Approval Request")

    def do_confirm(self) -> None:
        """
        Confirm wizard
        :return: None
        """
        self.ensure_one()
        self.approval_id.sudo().action_refuse(refusal_message=self.refusal_message)
