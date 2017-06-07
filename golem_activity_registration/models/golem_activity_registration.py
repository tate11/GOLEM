# -*- coding: utf-8 -*-

#    copyright 2017 fabien bourgeois <fabien@yaltik.com>
#
#    this program is free software: you can redistribute it and/or modify
#    it under the terms of the gnu affero general public license as
#    published by the free software foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    this program is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu affero general public license for more details.
#
#    you should have received a copy of the gnu affero general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.

""" GOLEM Activity Registration """

from odoo import models, fields, api, _

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    activity_registration_ids = fields.One2many('golem.activity.registration',
                                                'member_id', 'Current activities',
                                                domain=[('is_current', '=', True)])
    activity_registration_all_ids = fields.One2many('golem.activity.registration',
                                                    'member_id', 'All activities')


class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'
    _sql_constraints = [('golem_activity_places_signed',
                         'CHECK (places >= 0)',
                         _('Number of places cannot be negative.'))]

    activity_registration_ids = fields.One2many('golem.activity.registration',
                                                'activity_id', 'Members',
                                                index=True)
    places_used = fields.Integer('Places used', compute='compute_places_used',
                                 store=True)

    @api.multi
    @api.depends('activity_registration_ids')
    def compute_places_used(self):
        """ Computes used places """
        for activity in self:
            activity.places_used = len(activity.activity_registration_ids)

    places = fields.Integer('Places', default=20)
    places_remain = fields.Integer('Remaining places', store=True,
                                   compute='_compute_places_remain')

    @api.multi
    @api.depends('places', 'places_used')
    def _compute_places_remain(self):
        """ Computes remaining places """
        for activity in self:
            activity.places_remain = activity.places - activity.places_used

    @api.constrains('places_remain')
    def _check_remaining_places(self):
        """ Forbid inscription when there is no more place """
        for activity in self:
            if activity.places_remain < 0:
                emsg = _('Sorry, there is no more place !')
                raise models.ValidationError(emsg)


class GolemActivityRegistration(models.Model):
    """ GOLEM Activity Registration """
    _name = 'golem.activity.registration'
    _description = 'GOLEM Activity Registration'

    member_id = fields.Many2one('golem.member', string='Member', required=True,
                                ondelete='cascade', index=True)
    activity_id = fields.Many2one('golem.activity', required=True, index=True,
                                  string='Activity', ondelete='cascade')
    season_id = fields.Many2one(string='Season',
                                related='activity_id.season_id', store=True)
    is_current = fields.Boolean('Current season?',
                                related='activity_id.is_current', store=True)

    _sql_constraints = [
        ('registration_uniq', 'UNIQUE (member_id, activity_id)',
         _('This member has already been registered for this activity.'))]

    @api.constrains('member_id', 'activity_id')
    def _check_season_reliability(self):
        """ Forbid registration when member season if not coherent with
        activity season or are duplicates """
        for reg in self:
            if reg.activity_id.season_id not in reg.member_id.season_ids:
                emsg = _('Subscription can not be executed : the targeted '
                         'member is not on the same season as the activity.')
                raise models.ValidationError(emsg)
