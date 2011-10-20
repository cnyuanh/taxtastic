"""Creates a CSV file describing lineages for a set of taxa"""
# This file is part of taxtastic.
#
#    taxtastic is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    taxtastic is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with taxtastic.  If not, see <http://www.gnu.org/licenses/>.

from taxtastic import ncbi, greengenes
import os
from os import path
import logging

log = logging.getLogger(__name__)

modules = {'ncbi': ncbi, 'greengenes': greengenes}

def build_parser(parser):

    parser.add_argument(
        '-d', '--database-file',
        dest = 'database_file',
        metavar = 'FILE',
        help = """Name of the sqlite database file [TAXSRC_taxonony.db].""")

    parser.add_argument(
        '-p', '--download-dir',
        dest = 'download_dir',
        default = None,
        metavar = 'PATH',
        help = """Name of the directory into which to download the zip
        archive. [default is the same directory as the database file]""")

    parser.add_argument(
        '-t', '--taxonomy',
        metavar='TAXSRC',
        default='ncbi', choices=modules.keys(),
        help="""Taxonomy database to use [%(default)s].""")

    parser.add_argument(
        '-x', '--clobber', action = 'store_true',
        dest = 'clobber', default = False,
        help = """Download a new zip archive containing NCBI taxonomy
        and/or re-create the database even if one or both already
        exists. [%(default)s]""")

def action(args):
    dbname = args.database_file
    mod = modules[args.taxonomy]

    # Set default
    if not args.database_file:
        args.database_file = '{0}_taxonomy.db'.format(args.taxonomy)

    pth, fname = path.split(dbname)
    zip_dest = args.download_dir or pth or '.'

    zfile, downloaded = mod.fetch_data(
        dest_dir = zip_dest,
        clobber = args.clobber)

    if not os.access(dbname, os.F_OK) or args.clobber:
        log.warning('creating new database in %s using data in %s' % \
                        (dbname, zfile))
        con = mod.db_connect(dbname, clobber=True)
        mod.db_load(con, zfile)
        con.close()
    else:
        log.warning('taxonomy database already exists in %s' % dbname)
