'''Las_SERV'''
import lasio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter

# LAS FILE CORRECTIONS OR CONVERSIONS
def convertService(self : 'LASConverter', las_dat):
    """ Change Service Company to Eucalptus | remove ~other headers """
    # Get las SERV
    if 'SERV' not in las_dat.version.keys():
        las_dat.version['SERV'] = lasio.HeaderItem('SERV', value='EUKY',descr='Eucalyptus Consulting Inc.')
    else:
        las_dat.version.SERV = 'EUKY'
        las_dat.version.SERV.descr = 'Eucalyptus Consulting Inc.'

    # Remove ~Other line if only about IHS
    if las_dat.other.find('IHS'):  # Remove tops nomenclature statement
        las_dat.other = ''