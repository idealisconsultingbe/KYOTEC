# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class job_approval_position(models.Model):
    _name = 'job.approval.position'
    _description = 'Job Approval Position'

    name = fields.Char(string="Name")
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_approval_position_rel', 'approval_position_id', 'employee_id', string='Assigned')
    