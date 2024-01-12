# -*- coding: utf-8 -*-
{
    "name": "Autonsi WMS JPARK",
    "summary": "",
    "description": "",
    "author": "Autonsi",
    "website": "http://www.yourcompany.com",
    "category": "Autonsi",
    "version": "0.1",
    "sequence": 0,
    # any module necessary for this one to work correctly
    "depends": ["autonsi_wms", "autonsi_standard"],
    "data": [
        "views/fg_receiving_views.xml",
        "views/mat_receiving_view.xml",
        "views/mat_putaway_view.xml",
        "views/mat_shipping_view.xml",
        "views/fg_packing_views.xml",
        "views/fg_shipping_views.xml",
        "views/wip_receiving_views.xml",
        "views/wip_shipping_views.xml",
        "views/wip_return_views.xml",
        "views/mat_return_views.xml",
        "views/fg_return_views.xml",
    ],
}
