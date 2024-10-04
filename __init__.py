# -*- coding: utf-8 -*-
def classFactory(iface):
    from .iQ_ItsNodeLinkConverter import iQgisNodeLinkConverter
    return iQgisNodeLinkConverter(iface)
