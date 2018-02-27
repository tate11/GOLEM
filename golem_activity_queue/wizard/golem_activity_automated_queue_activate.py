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

""" GOLEM Resources management """

from odoo import models, fields, api, _

class GolemActivityAutomatedQueueActivateWizard(models.TransientModel):
    """GOLEM Activity Automated Queue wizard : Activatate automated Queue """
    _name = "golem.activity.automated.queue.activate.wizard"

    activity_id = fields.Many2one("golem.activity")
    automated_registration_from_queue = fields.Boolean(default=True)


    # lancer liste editable d'inscription sur attente
    def activate_queue(self):
        """ Activate Queue for the activity"""

        self.ensure_one()
        activation = self[0]
        activation.activity_id.write({
            'queue_allowed': True,
            'automated_registration_from_queue': activation.automated_registration_from_queue
            })


        """
        self.env['golem.activity.queue'].create({'member_id': activityQueue.member_id.id,
                                                 'activity_id': activityQueue.activity_id.id})
        message = _('the member {} is registred in queue for the activity {} with success')
        return {
            'warning' : {
                'title' : _('Warning'),
                'message': (message.format(activityQueue.member_id.name,
                                           activityQueue.activity_id.name))
            }
        }"""
