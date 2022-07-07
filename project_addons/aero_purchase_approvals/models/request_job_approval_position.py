# -*- coding: utf-8 -*-

from odoo import models, fields, api


class request_job_approval_position(models.Model):
    _name = 'request.job.approval.position'
    _description = 'Request Job Approval Position'

    job_approval_position_id = fields.Many2one('job.approval.position', string="Job Position")
    required = fields.Boolean(string='Required')
    approval_category_id = fields.Many2one('approval.category', string="Approval Type")
