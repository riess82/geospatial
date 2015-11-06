# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2011-2012 Camptocamp SA
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
#
##############################################################################
# TODO create a base Geocoder module
from urllib import urlencode
from urllib2 import urlopen
import xml.dom.minidom
import logging, exceptions
_logger = logging.getLogger(__name__)

import re
import pdb

from shapely.geometry import Point

from openerp.osv import fields, orm
from openerp.osv.osv import except_osv
from tools.translate import _

try:
    import requests
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.warning('requests is not available in the sys path')


logger = logging.getLogger('GeoNames address encoding')


class ResPartner(orm.Model):
    """Auto geo coding of addresses"""

    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'geo_point': fields.geo_point(
            'Addresses coordinate', readonly=True)
    }

    def _can_geocode(self, cursor, uid, context):
        usr = self.pool['res.users']
        return usr.browse(
            cursor, uid, uid, context).company_id.enable_geocoding

    def geocode_from_geonames(self, cursor, uid, ids, srid='900913',
                              strict=True, context=None):
        context = context or {}
        url = u'http://nominatim.openstreetmap.org/search'
        filters = {}
        if not isinstance(ids, list):
            ids = [ids]
        for add in self.browse(cursor, uid, ids, context):
            logger.info('geolocalize %s', add.name)
            if add.country_id.code and (add.city or add.zip) and add.street:
                filters[u'country'] = add.country_id.code.encode('utf-8')
                if add.city:
                    filters[u'city'] = add.city.encode('utf-8')
                #prefer city name over zip
                if not add.city and add.zip:
                    filters[u'postalcode'] = add.zip.encode('utf-8')
                if add.street:
					#second try with shortened street
					if context.get('second_try') == True:
						street = add.street.encode('utf-8')
						search_part = re.search(r'(?!\d+\.)\b\d+', street)
						if not search_part:
							exit()
						house_number_start = search_part.start()
						right_part = street[house_number_start:]
						found_parts = re.split("[, \-\/!?:]+", right_part)
						first_number_length = len(found_parts[0])
						new_street = street[:house_number_start+first_number_length]
						filters[u'street'] = new_street
					else:
						filters[u'street'] = add.street.encode('utf-8')
                filters[u'limit'] = u'1'
                filters[u'format'] = u'json'

                request_result = requests.get(url, params=filters)
                try:
                    request_result.raise_for_status()
                except Exception as e:
					_logger.exception('Geocoding error')
					raise exceptions.Warning(_(
						'Geocoding error. \n %s') % e.message)
                vals = request_result.json()
                vals = vals and vals[0] or {}
                if not vals:
					# should show warning window but save data anyway, not working
					#_logger.exception('Geocoding error, no position returned')
					#raise exceptions.Warning(_(
					#    'Positioning error. \n'))
					data = {'geo_point': ''}
					add.write(data)
					#call function again but with shortened street variable
					if context.get('second_try') != True:
						context.update({'second_try': True})
						self.geocode_from_geonames(cursor, uid, ids, srid='900913', strict=strict, context=context)
					else:
						context.update({'second_try': None})
					continue
                try:
                    point = Point(float(vals['lon']),float(vals['lat']))
                    data = {'geo_point': point}
                    add.write(data)
                    # We use postgres to do projection in order not to install
                    # GDAL dependences
                    sql = """
                    UPDATE
                    res_partner
                    SET
                    geo_point = ST_Transform(st_SetSRID(geo_point, 4326), %s)
                    WHERE id = %s"""
                    cursor.execute(sql, (srid, add.id))
                except Exception as exc:
                    _logger.exception('error while updating geocodes')
                    if strict:
                        raise except_osv(_('Geoencoding fails'), str(exc))
        return ids

    def write(self, cursor, uid, ids, vals, context=None):
        res = super(ResPartner, self).write(
            cursor, uid, ids, vals, context=None)
        do_geocode = self._can_geocode(cursor, uid, context)
        if do_geocode \
            and "country_id" in vals \
            or 'city' in vals \
            or 'street' in vals \
                or 'zip' in vals:
            self.geocode_from_geonames(cursor, uid, ids, context=context)
        return res

    def create(self, cursor, uid, vals, context=None):
        res = super(ResPartner, self).create(cursor, uid, vals, context=None)
        do_geocode = self._can_geocode(cursor, uid, context=context)
        if do_geocode:
            self.geocode_from_geonames(cursor, uid, res, context=context)
        return res
