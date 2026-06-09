# This constructs a json of location list with some info

import json

locations = {
    "ADDINGTON": {
        "lat": -43.54239928241255,
        "lon": 172.61417946240846
    },
    "BECKENHAM": {
        "lat": -43.5575392666076,
        "lon": 172.6370021508312
    },
    "BUSH INN": {
        "lat": -43.5306875385698,
        "lon": 172.57529121445396
    },
    "KAIAPOI": {
        "lat": -43.38282201632629,
        "lon": 172.65658909040874
    },
    "LINCOLN": {
        "lat": -43.64059667950655,
        "lon": 172.48231474565966
    },
    "LYTTELTON": {
        "lat": -43.60263818568333,
        "lon": 172.72181934237682
    },
    "MERIVALE": {
        "lat": -43.510718739867514,
        "lon": 172.62023035269425
    },
    "NORTHLINK": {
        "lat": -42.49018949231541,
        "lon": 172.60261639405297
    },
    "RANGIORA": {
        "lat": -42.30357675654017,
        "lon": 172.59510949593965
    },
    "RICCARTON": {
        "lat": -42.5300251495134,
        "lon": 171.60044589127608
    },
    "REDWOOD": {
        "lat": -42.47784459819944,
        "lon": 172.61705234193937
    },
    "ROLLESTON": {
        "lat": -42.594323341323914,
        "lon": 172.38735787643762
    },
    "SUMNER": {
        "lat": -42.568303882185276,
        "lon": 171.7587296085304
    },
    "THE CROSSING": {
        "lat": -42.53339728346573,
        "lon": 172.6377039294879
    },
    "THE PALMS": {
        "lat": -42.5073718139867514,
        "lon": 171.663801134755
    }
}

with open("../locations.json", "w") as f:
    locs = {k.replace(" ", "_"): {"lat": v["lat"], "lon": v["lon"]} for k, v in locations.items()}
    json.dump(locs, f)
