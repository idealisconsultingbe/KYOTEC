# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import api, exceptions, fields, models, _


class ApprovalApprover(models.Model):
    """
    Approval Approver
    """
    _inherit = "approval.approver"

    def _create_activity(self) -> None:
        """
        Override the method.
        Disable creation of activity
        :return: None
        """
        return