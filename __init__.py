# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
#     from .moct_checker import MoctChecker
    from .iQgis_21_NodeLinkChecker import iQgisNodeLinkChecker
    return iQgisNodeLinkChecker(iface)
