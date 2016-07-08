# -*- coding: utf-8 -*-

#    Copyright 2016 Fabien Bourgeois <fabien@yaltik.com>
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

from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    nationality_id = fields.Many2one(default=_get_default_nationality_id)
    country_id = fields.Many2one(default=_get_default_nationality_id)

    # Gender overwriting : no need for 'other' choice
    gender = fields.Selection([('male', _('Male')), ('female', _('Female'))])

    member_id = fields.One2many('golem.member', 'partner_id', 'GOLEM Member',
                                readonly=True)
    member_number = fields.Char('Member number', related='member_id.number')

    @api.multi
    def create_golem_member(self):
        self.ensure_one()
        gm = self.env['golem.member']
        gm.create({'partner_id': self.id})
        return True


class GolemMember(models.Model):
    _name = 'golem.member'
    _description = 'GOLEM Member'
    _inherit = 'mail.thread'
    _inherits = {'res.partner': 'partner_id'}

    @api.model
    def _default_season(self):
        """ Get default season """
        domain = [('is_default', '=', True)]
        return self.env['golem.season'].search(domain)

    number = fields.Char('Member number', store=True, readonly=True,
                         compute='_compute_number')
    number_manual = fields.Char('Manual number', size=50, index=True,
                                help='Manual number overwriting automatic '
                                'numbering')
    pictures_agreement = fields.Boolean('Pictures agreement?')
    opt_out_sms = fields.Boolean('Out of SMS campaigns')
    season_ids = fields.Many2many('golem.season', string='Seasons',
                                  required=True, auto_join=True,
                                  default=_default_season)
    is_current = fields.Boolean('Current user?', default=False, readonly=True,
                                store=True, compute='_compute_is_current')
    is_number_manual = fields.Boolean('Is number manual?', store=False,
                                      compute='_compute_is_number_manual')

    _sql_constraints = [('golem_member_number_manual_uniq',
                         'UNIQUE (number_manual)',
                         _('This member number has already been used.'))]

    @api.depends('number_manual', 'season_ids')
    def _compute_number(self):
        """ Computes number according to pre-existing number and chosen
        seasons, or sets as manual """
        for member in self:
            conf = self.env['ir.config_parameter']
            if conf.get_param('golem_numberconfig_isautomatic') == '0':
                member.number = member.number_manual
            else:
                if member.id:
                    member.number = ''
                    if conf.get_param('golem_numberconfig_isperseason') == '1':
                        for s in member.season_ids:
                            domain = ['&',
                                      ('member_id', '=', member.id),
                                      ('season_id', '=', s.id)]
                            member_num = self.env['golem.member.number']
                            mn = member_num.search(domain)
                            if not mn:
                                s.member_counter += 1
                                s.write({'member_counter': s.member_counter})
                                pkey = 'golem_numberconfig_prefix'
                                pfx = conf.get_param(pkey)
                                number = pfx + str(s.member_counter)
                                data = {'member_id': member.id,
                                        'season_id': s.id,
                                        'number': number}
                                mn = member_num.create(data)
                            if s.is_default:
                                member.number = mn.number
                    else:
                        domain = ['&',
                                  ('member_id', '=', member.id),
                                  ('season_id', '=', None)]
                        member_num = self.env['golem.member.number']
                        mn = member_num.search(domain)
                        if not mn:
                            last = int(conf.get_param('golem_number_counter',
                                                      0))
                            last += 1
                            conf.set_param('golem_number_counter', str(last))
                            pfx = conf.get_param('golem_numberconfig_prefix')
                            number = pfx + str(last)
                            data = {'member_id': member.id,
                                    'season_id': None,
                                    'number': number}
                            mn = member_num.create(data)
                        member.number = mn.number

    @api.depends('season_ids')
    def _compute_is_current(self):
        """ Computes is current according to seasons """
        default_s = self._default_season()
        for m in self:
            m.is_current = default_s in m.season_ids

    @api.depends('lastname')
    def _compute_is_number_manual(self):
        conf = self.env['ir.config_parameter']
        is_num_man = (conf.get_param('golem_numberconfig_isautomatic') == '0')
        self.is_number_manual = is_num_man


class GolemMemberSeason(models.Model):
    """ GOLEM Member Numbers """
    _name = 'golem.member.number'
    _description = 'GOLEM Member Numbers'

    name = fields.Char('Name', compute='_compute_name')
    member_id = fields.Many2one('golem.member', string='Member', index=True,
                                required=True, ondelete='cascade',
                                auto_join=True)
    season_id = fields.Many2one('golem.season', string='Season', index=True,
                                auto_join=True)
    number = fields.Char('Number', index=True, readonly=True)

    @api.depends('season_id')
    def _compute_name(self):
        for row in self:
            row.name = row.season_id.name


class GolemNumberConfig(models.TransientModel):
    """ Configuration for number computing """
    _name = 'golem.member.numberconfig'
    _description = 'Configuration for number computing'

    @api.model
    def _default_is_automatic(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('golem_numberconfig_isautomatic', '1')

    @api.model
    def _default_is_per_season(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('golem_numberconfig_isperseason', '0')

    @api.model
    def _default_prefix(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('golem_numberconfig_prefix', '')

    is_automatic = fields.Selection([('1', _('Yes')), ('0', _('No'))],
                                    string='Computed automatically?',
                                    default=_default_is_automatic)
    is_per_season = fields.Selection([('1', _('Yes')), ('0', _('No'))],
                                     string='Per season number?',
                                     default=_default_is_per_season)
    prefix = fields.Char('Optional prefix', default=_default_prefix)

    @api.multi
    def apply_config(self):
        self.ensure_one()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_numberconfig_isautomatic', self.is_automatic)
        conf.set_param('golem_numberconfig_isperseason', self.is_per_season)
        conf.set_param('golem_numberconfig_prefix', self.prefix or '')

    @api.multi
    def apply_recompute(self):
        self.ensure_one()
        self.apply_config()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_number_counter', '0')
        self.env['golem.member.number'].search([]).unlink()
        self.env['golem.season'].search([]).write({'member_counter': 0})
        self.env['golem.member'].search([])._compute_number()
