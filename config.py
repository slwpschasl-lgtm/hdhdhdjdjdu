BOT_TOKEN = "9262571218:AAGb0wGJZoRnvL9ulqTuLS4LA2V3AAv_A9I"
ADMIN_ID = 8617877923
SHOP_NAME = "BARMALEY"
OPERATOR_LINK = "https://t.me/bsaurpmpaolrety"
REVIEWS_BOT_LINK = "https://t.me/your_reviews_bot"

EXCHANGE_RATES = {
    "USD_TO_BTC": 0.000016,
    "USD_TO_LTC": 0.023,
    "USD_TO_USDT": 1.0,
}

WALLETS = {
    "btc": "bc1qv7yh605582wglfpz5sxcsya54r5jlu3zlw50gg",
    "ltc": "ltc1q7c6l9r4954acksjkvcg66jvzqcrffcx0cyv356",
    "usdt_trc20": "TQH6uCrxQoqCdnS37o5exNr94khkhbcEDw"
}

STATES = {
    "idaho": {"name": "Idaho", "coefficient": 0.90},
    "iowa": {"name": "Iowa", "coefficient": 0.95},
    "alabama": {"name": "Alabama", "coefficient": 0.92},
    "alaska": {"name": "Alaska", "coefficient": 1.25},
    "arizona": {"name": "Arizona", "coefficient": 0.88},
    "arkansas": {"name": "Arkansas", "coefficient": 0.91},
    "wyoming": {"name": "Wyoming", "coefficient": 0.90},
    "washington": {"name": "Washington", "coefficient": 1.15},
    "vermont": {"name": "Vermont", "coefficient": 1.00},
    "virginia": {"name": "Virginia", "coefficient": 1.02},
    "wisconsin": {"name": "Wisconsin", "coefficient": 1.05},
    "hawaii": {"name": "Hawaii", "coefficient": 1.50},
    "delaware": {"name": "Delaware", "coefficient": 1.10},
    "georgia": {"name": "Georgia", "coefficient": 0.90},
    "west virginia": {"name": "West Virginia", "coefficient": 0.92},
    "illinois": {"name": "Illinois", "coefficient": 1.25},
    "indiana": {"name": "Indiana", "coefficient": 0.92},
    "california": {"name": "California", "coefficient": 1.45},
    "kansas": {"name": "Kansas", "coefficient": 0.95},
    "kentucky": {"name": "Kentucky", "coefficient": 0.91},
    "colorado": {"name": "Colorado", "coefficient": 1.08},
    "connecticut": {"name": "Connecticut", "coefficient": 1.35},
    "louisiana": {"name": "Louisiana", "coefficient": 0.91},
    "massachusetts": {"name": "Massachusetts", "coefficient": 1.40},
    "minnesota": {"name": "Minnesota", "coefficient": 1.04},
    "mississippi": {"name": "Mississippi", "coefficient": 0.88},
    "missouri": {"name": "Missouri", "coefficient": 0.93},
    "michigan": {"name": "Michigan", "coefficient": 1.10},
    "montana": {"name": "Montana", "coefficient": 0.91},
    "maine": {"name": "Maine", "coefficient": 1.00},
    "maryland": {"name": "Maryland", "coefficient": 1.20},
    "nebraska": {"name": "Nebraska", "coefficient": 0.95},
    "nevada": {"name": "Nevada", "coefficient": 1.00},
    "new hampshire": {"name": "New Hampshire", "coefficient": 0.96},
    "new jersey": {"name": "New Jersey", "coefficient": 1.38},
    "new mexico": {"name": "New Mexico", "coefficient": 0.94},
    "new york": {"name": "New York", "coefficient": 1.55},
    "ohio": {"name": "Ohio", "coefficient": 1.00},
    "oklahoma": {"name": "Oklahoma", "coefficient": 0.90},
    "oregon": {"name": "Oregon", "coefficient": 1.10},
    "pennsylvania": {"name": "Pennsylvania", "coefficient": 1.12},
    "rhode island": {"name": "Rhode Island", "coefficient": 1.30},
    "north dakota": {"name": "North Dakota", "coefficient": 0.92},
    "north carolina": {"name": "North Carolina", "coefficient": 0.95},
    "tennessee": {"name": "Tennessee", "coefficient": 0.91},
    "texas": {"name": "Texas", "coefficient": 0.85},
    "florida": {"name": "Florida", "coefficient": 0.93},
    "south dakota": {"name": "South Dakota", "coefficient": 0.92},
    "south carolina": {"name": "South Carolina", "coefficient": 0.92},
    "utah": {"name": "Utah", "coefficient": 0.90},
}

SHIPPING_COSTS = {
    "alabama": 40, "alaska": 160, "arizona": 35, "arkansas": 35,
    "california": 70, "colorado": 45, "connecticut": 65, "delaware": 60,
    "florida": 45, "georgia": 40, "hawaii": 190, "idaho": 55,
    "illinois": 60, "indiana": 45, "iowa": 45, "kansas": 40,
    "kentucky": 45, "louisiana": 35, "maine": 70, "maryland": 65,
    "massachusetts": 75, "michigan": 55, "minnesota": 50, "mississippi": 35,
    "missouri": 40, "montana": 55, "nebraska": 45, "nevada": 50,
    "new hampshire": 65, "new jersey": 70, "new mexico": 35, "new york": 80,
    "north carolina": 50, "north dakota": 50, "ohio": 50, "oklahoma": 30,
    "oregon": 65, "pennsylvania": 60, "rhode island": 70, "south carolina": 45,
    "south dakota": 45, "tennessee": 40, "texas": 25, "utah": 45,
    "vermont": 65, "virginia": 55, "washington": 70, "west virginia": 50,
    "wisconsin": 50, "wyoming": 50,
}

SHIPPING_DAYS = {
    "alabama": "2-4", "alaska": "6-9", "arizona": "2-3", "arkansas": "1-3",
    "california": "3-5", "colorado": "2-4", "connecticut": "4-6", "delaware": "4-5",
    "florida": "3-5", "georgia": "2-4", "hawaii": "7-10", "idaho": "3-5",
    "illinois": "2-4", "indiana": "2-4", "iowa": "2-4", "kansas": "2-3",
    "kentucky": "2-4", "louisiana": "1-3", "maine": "4-6", "maryland": "3-5",
    "massachusetts": "4-6", "michigan": "3-5", "minnesota": "3-5", "mississippi": "1-3",
    "missouri": "2-3", "montana": "3-5", "nebraska": "2-4", "nevada": "2-4",
    "new hampshire": "4-6", "new jersey": "4-6", "new mexico": "1-3", "new york": "4-7",
    "north carolina": "3-5", "north dakota": "3-5", "ohio": "3-5", "oklahoma": "1-2",
    "oregon": "4-6", "pennsylvania": "3-5", "rhode island": "4-6", "south carolina": "3-4",
    "south dakota": "3-5", "tennessee": "2-4", "texas": "1-2", "utah": "2-4",
    "vermont": "4-6", "virginia": "3-5", "washington": "4-6", "west virginia": "3-5",
    "wisconsin": "3-5", "wyoming": "3-4",
}

SWITCH_SHIPPING = 15
SWITCH_SHIPPING_DAYS = "3-5"

WEAPONS = {
    "glock19": {"name": "Glock 19 Gen5", "base_price": 600, "category": "handguns", "fixed_price": False, "description": "Reliable and compact 9mm pistol. Perfect for everyday carry.", "image": "glock19.jpg"},
    "glock17": {"name": "Glock 17 Gen5", "base_price": 580, "category": "handguns", "fixed_price": False, "description": "Full-size 9mm service pistol with high magazine capacity.", "image": "glock17.jpg"},
    "taurus_g2c": {"name": "Taurus G2c", "base_price": 300, "category": "handguns", "fixed_price": False, "description": "Budget-friendly, lightweight, and easy to conceal.", "image": ""},
    "taurus_g3c": {"name": "Taurus G3c", "base_price": 300, "category": "handguns", "fixed_price": False, "description": "Upgraded version of G2c with improved trigger and sights.", "image": ""},
    "sw_sd9": {"name": "Smith & Wesson SD9", "base_price": 380, "category": "handguns", "fixed_price": False, "description": "Striker-fired polymer pistol, great ergonomics.", "image": ""},
    "hipoint_c9": {"name": "Hi-Point C9", "base_price": 160, "category": "handguns", "fixed_price": False, "description": "The cheapest option. Heavy, but gets the job done.", "image": ""},
    "taurus_85": {"name": "Taurus Model 85", "base_price": 240, "category": "handguns", "fixed_price": False, "description": "Compact .38 Special revolver, ideal for backup.", "image": ""},
    "russian_ak": {"name": "Russian AK", "base_price": 2500, "category": "long_guns", "fixed_price": True, "description": "Authentic Russian-made AK. High demand, fixed price.", "image": "russian_ak.jpg"},
    "micro_draco": {"name": "Century Arms Micro Draco", "base_price": 1100, "category": "long_guns", "fixed_price": False, "description": "Compact AK pistol. Fierce and aggressive.", "image": ""},
    "mp15": {"name": "Smith & Wesson M&P15", "base_price": 850, "category": "long_guns", "fixed_price": False, "description": "Modern AR-15 platform rifle. 5.56x45mm NATO.", "image": ""},
    "tec9": {"name": "Intratec Tec-9", "base_price": 750, "category": "smg", "fixed_price": False, "description": "Infamous semi-automatic pistol with a large magazine.", "image": ""},
    "glock_switch": {"name": "Glock Switch", "base_price": 79, "category": "accessory", "fixed_price": True, "description": "Auto-sear device. Made from aluminum.", "image": "switch.jpg"}
}

CATEGORIES = {
    "handguns": "Handguns",
    "long_guns": "Long Guns",
    "smg": "SMG",
    "accessory": "Accessories"
}
