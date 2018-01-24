# -*- coding: utf-8 -*-

from utils import read_file

SIM_STATUS_FILES = [
    '/sys/class/gpio/gpio339/value',
    '/sys/class/gpio/gpio340/value',
    '/sys/class/gpio/gpio341/value'
]

def get_wan_connections():
    """Returns list of SIM connections

    Sample Reponse:

        [
        {
            "id": "SIM1",
            "name": "SIM 1",
            "connection_type": "SIM",
            "connection_available": true,
            "connected": true,
            "info": {
                "sim_locked": true,
                "apn_configured": true,
                "network_info": {
                    "operator": "Operator Name",
                    "imei": 350089999084990,
                    "cell_id": 300300,
                    "lac": 300,
                    "mnc": 304,
                    "mcc": 639,
                    "network_type": "2G"
                }
            }
        }
        ]

    :return: list(dict)
    """
    conns = []
    for (i, path) in enumerate(SIM_STATUS_FILES):
        key = i + 1
        c_id = 'SIM%d' %(key)
        name = 'SIM %d' % (key)
        file_resp = read_file(path)
        available = False
        connected = False
        if file_resp != False and file_resp == '1':
            available = True
        c_data = dict(
            id=c_id,
            name=name,
            available=available,
            connected=connected,
            info={}
        )
        conns.append(c_data)
    return conns
