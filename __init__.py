# -*- coding: utf-8 -*-
def classFactory(iface):
    from .iQ_ItsNodeLinkViewer import iQgisNodeLinkChecker
    return iQgisNodeLinkChecker(iface)
