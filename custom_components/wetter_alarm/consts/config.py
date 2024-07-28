class Config:
    class Errors:
        NO_POI_FOUND = "error_no_poi_found"
        NO_CANTON = "error_no_canton"
        NO_POI_ID = "error_no_poi_id"
        INVALID_POI_ID = "error_invalid_poi_id"
    class POI:
        NAME = "poi_name"
        NAME_SHORT = "poi_name_short"
        KIND = "poi_kind"
        CANTON = "poi_canton"
        ID = "poi_id"
        MAP = "poi_map"
        SEARCH = "poi_search"
        DATA = "poi_data"
        LIST = "poi_list"
        SET_BY = "set_poi_by"
        BY_ID = "set_by_id"
        BY_SEARCH = "set_by_search"
        BY_MAP = "set_by_map"
        KIND = "poi_kind"
        KINDS_DEFAULTS = ['town', 'town_section']
        KINDS = [
            'airport',
            'alpine_hut',
            'building_of_interest',
            'campground',
            'golf',
            'pass',
            'peak', 
            'ski_area',
            'stadium',
            'town',
            'town_section',
            'unknown',
            'valley',
            'viewpoint',
            'zoo'
            ]
        CANTON = "canton"
        CANTONS = [
            "none",
            "AG",
            "AI",
            "AR",
            "BE",
            "BL",
            "BS",
            "FR",
            "GE",
            "GL",
            "GR",
            "JU",
            "LU",
            "NE",
            "NW",
            "OW",
            "SG",
            "SH",
            "SO",
            "SZ",
            "TG",
            "TI",
            "UR",
            "VD",
            "VS",
            "ZG",
            "ZH",
            "other"
        ]