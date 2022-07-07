# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    job_approvals_position_ids = fields.Many2many('job.approval.position', 'hr_employee_approval_position_rel', 'employee_id', 'approval_position_id', string='Job Approval Position')

    def _get_user_position(self, position):
        """ browse employee flowchart and return all manager with position """
        user_position_ids = self.env['res.users']
        manager_id = self.parent_id
        while manager_id:
            if position in manager_id.job_approvals_position_ids:
                user_position_ids |= manager_id.user_id
                manager_id = manager_id.parent_id
            else:
                manager_id = manager_id.parent_id
        return user_position_ids
