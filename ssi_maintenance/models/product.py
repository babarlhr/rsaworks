# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime
import requests


class ProductTemplate(models.Model):
    _inherit = "product.template"

    storage_subscription = fields.Boolean('Update Storage Subscription', help="Check this box to use this product as the storage subscription line.")

