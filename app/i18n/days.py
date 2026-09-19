from app.config import SCHEDULE_LANG

DAY_NAMES = {
    "pt-BR": {
        "MON": "SEG",
        "TUE": "TER",
        "WED": "QUA",
        "THU": "QUI",
        "FRI": "SEX",
        "SAT": "SÁB",
        "SUN": "DOM",
    },

    "es-419": {
        "MON": "LUN",
        "TUE": "MAR",
        "WED": "MIÉ",
        "THU": "JUE",
        "FRI": "VIE",
        "SAT": "SÁB",
        "SUN": "DOM",
    },

    "ja-JP": {
        "MON": "月", # getsu = lua
        "TUE": "火", # ka = fogo
        "WED": "水", # sui = água
        "THU": "木", # moku = madeira
        "FRI": "金", # kin = ouro/metal
        "SAT": "土", # do = terra
        "SUN": "日", # nichi = sol
    }
}


def get_day_name(day):
    return DAY_NAMES[SCHEDULE_LANG][day]
