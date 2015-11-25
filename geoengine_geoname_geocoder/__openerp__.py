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
{'name': 'Auto Geocoding of partners',
 'version': '0.2',
 'category': 'GeoBI',
 'description': """ Geolocalise your partner based on longitude and latitude provided by
`OpenStreetMap via its Nominatim service
<http://wiki.openstreetmap.org/wiki/Nominatim>`_. Please read carefully the
`usage policy <http://wiki.openstreetmap.org/wiki/Nominatim_usage_policy>`_
before using the module.

This module tries to find an address, trying to strip the street field of added parts like door number. This will probably result in total chaos for street strings not following the pattern [street name] [house number] [additional stuff].
The module also tries to removes some substrings (hardcoded for the time being) from the city field.

 Technical notes:
 PostGIS must support projection (proj4)
 We use postgis to do the reprojection in order to avoid gdal python deps.
 """,
 'update_xml': ['company_view.xml', 'wizard/bulk_encode_view.xml'],
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'license': 'AGPL-3',
 'website': 'http://openerp.camptocamp.com',
 'depends': ['base', 'sale', 'geoengine_partner'],
 'installable': True,
 'active': False,
 'icon': '/base_geoengine/static/src/images/map_icon.png'}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
