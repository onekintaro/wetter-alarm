#TODO: Check if the condition is correct
symbol_to_condition = {
    'clear-night': [-1],
    'cloudy': [18, 19],
    'fog': [2],
    'hail': [],
    'lightning': [26, 28],
    'lightning-rainy': [30],
    'partlycloudy': [11, 12, 13, 14, 15, 16],
    'pouring': [4, 20, 22, 23, 25, 29],
    'rainy': [4, 20, 22, 23, 25, 29],
    'snowy': [6, 21, 24, 27],
    'snowy-rainy': [24],
    'sunny': [10],
    'windy': [],
    'windy-variant': [],
    'partly-cloudy-night': [-10, -11, -12, -13, -14, -15, -16],
    'rainy-night': [-4, -20, -22, -23, -25, -29],
    'snowy-night': [-6, -21, -24, -27],
    'lightning-night': [-28],
    'lightning-rainy-night': [-30],
    'cloudy-night': [-3,-18, -19],
    'fog-night': [-2],
}

def symbol_convert(symbol: int) -> str:
    for key, value in symbol_to_condition.items():
        if symbol in value:
            return key
    return 'unknown'

#TODO: Complete Data
mood_to_condition = {
    'clear-night': ['moony'],
    'cloudy': ['cloudy', 'cloudynight'],
    'exceptional': [],
    'fog': ['foggy', 'foggynight'],
    'hail': [],
    'lightning': [],
    'lightning-rainy': ['stormy', 'stormynight'],
    'partlycloudy': ['partlycloudy', 'partlymoony'],
    'pouring': [],
    'rainy': ['rainy', 'rainynight'],
    'snowy': ['snowy', 'snowynight'],
    'snowy-rainy': [],
    'sunny': ['sunny'],
    'windy': [],
    'windy-variant': []
}

def mood_convert(mood: str) -> str:
    for key, value in mood_to_condition.items():
        if mood in value:
            return key
    return 'unknown'