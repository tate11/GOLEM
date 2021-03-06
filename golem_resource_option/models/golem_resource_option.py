# -*- coding: utf-8 -*-

#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" GOLEM Resource Option """


from odoo import models, fields, _


class GolemResourceOption(models.Model):
    """ GOLEM Resource Option Model """
    _name = 'golem.resource.option'
    _description = 'GOLEM Reservation Option Model'
    _order = 'name asc, resource_id asc'
    _sql_constraints = [('golem_resource_option_name_uniq',
                         'UNIQUE (name, resource_id)',
                         _('An option has already this name for this resource.'))]

    name = fields.Char('Option', required=True, index=True)
    resource_id = fields.Many2one('golem.resource', 'Resource',
                                  index=True, required=True)
    active = fields.Boolean(default=True)
