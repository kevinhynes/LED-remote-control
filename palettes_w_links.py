import webcolors


palettes = [
    # https://coolors.co/palette/dad7cd-a3b18a-588157-3a5a40-344e41
    {'forest': {
        "Timberwolf": "dad7cd",
        "Sage": "a3b18a",
        "Fern green": "588157",
        "Hunter green": "3a5a40",
        "Brunswick green": "344e41"}
    },

    # https://coolors.co/palette/582f0e-7f4f24-936639-a68a64-b6ad90-c2c5aa-a4ac86-656d4a-414833-333d29
    {'camp': {
        "Seal brown": "582f0e",
        "Russet": "7f4f24",
        "Raw umber": "936639",
        "Lion": "a68a64",
        "Khaki": "b6ad90",
        "Sage": "c2c5aa",
        "Sage 2": "a4ac86",
        "Reseda green": "656d4a",
        "Ebony": "414833",
        "Black olive": "333d29"}
    },

    # https://coolors.co/palette/143601-1a4301-245501-538d22-73a942-aad576
    {'grassland': {
        "Pakistan green": "143601",
        "Pakistan green 2": "1a4301",
        "Dark moss green": "245501",
        "Avocado": "538d22",
        "Asparagus": "73a942",
        "Pistachio": "aad576"}
    },

    # https://coolors.co/palette/cdb4db-ffc8dd-ffafcc-bde0fe-a2d2ff
    {'cotton_candy': {
        "Thistle": "cdb4db",
        "Fairy Tale": "ffc8dd",
        "Carnation pink": "ffafcc",
        "Uranian Blue": "bde0fe",
        "Light Sky Blue": "a2d2ff"}
    },

    # https://coolors.co/palette/03045e-023e8a-0077b6-0096c7-00b4d8-48cae4-90e0ef-ade8f4-caf0f8
    {'sky': {
        "Federal blue": "03045e",
        "Marian blue": "023e8a",
        "Honolulu Blue": "0077b6",
        "Blue Green": "0096c7",
        "Pacific cyan": "00b4d8",
        "Vivid sky blue": "48cae4",
        "Non Photo blue": "90e0ef",
        "Non Photo blue 2": "ade8f4",
        "Light cyan": "caf0f8"}
    },

    # https://coolors.co/palette/012a4a-013a63-01497c-014f86-2a6f97-2c7da0-468faf-61a5c2-89c2d9-a9d6e5
    {'deep_sky': {
        "Prussian blue": "012a4a",
        "Indigo dye": "013a63",
        "Indigo dye 2": "01497c",
        "Indigo dye 3": "014f86",
        "UCLA Blue": "2a6f97",
        "Cerulean": "2c7da0",
        "Air Force blue": "468faf",
        "Air superiority blue": "61a5c2",
        "Sky blue": "89c2d9",
        "Light blue": "a9d6e5"}
    },

    # https://coolors.co/palette/ffadad-ffd6a5-fdffb6-caffbf-9bf6ff-a0c4ff-bdb2ff-ffc6ff-fffffc
    {'ice_cream_truck': {
        "Melon": "ffadad",
        "Sunset": "ffd6a5",
        "Cream": "fdffb6",
        "Tea green": "caffbf",
        "Electric blue": "9bf6ff",
        "Jordy Blue": "a0c4ff",
        "Periwinkle": "bdb2ff",
        "Mauve": "ffc6ff",
        "Baby powder": "fffffc"}
    },

    # https://coolors.co/palette/7400b8-6930c3-5e60ce-5390d9-4ea8de-48bfe3-56cfe1-64dfdf-72efdd-80ffdb
    {'jazz_cup': {
        "French violet": "7400b8",
        "Grape": "6930c3",
        "Slate blue": "5e60ce",
        "United Nations Blue": "5390d9",
        "Picton Blue": "4ea8de",
        "Aero": "48bfe3",
        "Sky blue": "56cfe1",
        "Tiffany Blue": "64dfdf",
        "Turquoise": "72efdd",
        "Aquamarine": "80ffdb"}
    },

    # https://coolors.co/palette/f72585-b5179e-7209b7-560bad-480ca8-3a0ca3-3f37c9-4361ee-4895ef-4cc9f0
    {'cyberpunk': {
        "Rose": "f72585",
        "Fandango": "b5179e",
        "Grape": "7209b7",
        "Chrysler blue": "560bad",
        "Dark blue": "480ca8",
        "Zaffre": "3a0ca3",
        "Palatinate blue": "3f37c9",
        "Neon blue": "4361ee",
        "Chefchaouen Blue": "4895ef",
        "Vivid sky blue": "4cc9f0"}
    },

    # https://coolors.co/palette/2d00f7-6a00f4-8900f2-a100f2-b100e8-bc00dd-d100d1-db00b6-e500a4-f20089
    {'bright_cyberpunk': {
        "Blue": "2d00f7",
        "Electric indigo": "6a00f4",
        "Violet": "8900f2",
        "Veronica": "a100f2",
        "Veronica 2": "b100e8",
        "Electric purple": "bc00dd",
        "Steel pink": "d100d1",
        "Steel pink 2": "db00b6",
        "Hollywood cerise": "e500a4",
        "Magenta": "f20089"}
    },

    # https://coolors.co/palette/ff6d00-ff7900-ff8500-ff9100-ff9e00-240046-3c096c-5a189a-7b2cbf-9d4edd
    {'halloween_party': {
        "Pumpkin": "ff6d00",
        "Safety orange": "ff7900",
        "UT orange": "ff8500",
        "Princeton orange": "ff9100",
        "Orange peel": "ff9e00",
        "Russian violet": "240046",
        "Persian indigo": "3c096c",
        "Tekhelet": "5a189a",
        "French violet": "7b2cbf",
        "Amethyst": "9d4edd"}
    },

    # https://coolors.co/palette/757bc8-8187dc-8e94f2-9fa0ff-ada7ff-bbadff-cbb2fe-dab6fc-ddbdfc-e0c3fc
    {'mauves': {
        "Glaucous": "757bc8",
        "Tropical indigo": "8187dc",
        "Tropical indigo 2": "8e94f2",
        "Vista Blue": "9fa0ff",
        "Powder blue": "ada7ff",
        "Mauve": "bbadff",
        "Mauve 2": "cbb2fe",
        "Mauve 3": "dab6fc",
        "Mauve 4": "ddbdfc",
        "Mauve 5": "e0c3fc"}
    },

    # https://coolors.co/palette/10002b-240046-3c096c-5a189a-7b2cbf-9d4edd-c77dff-e0aaff
    {'purples': {
        "Russian violet": "10002b",
        "Russian violet 2": "240046",
        "Persian indigo": "3c096c",
        "Tekhelet": "5a189a",
        "French violet": "7b2cbf",
        "Amethyst": "9d4edd",
        "Heliotrope": "c77dff",
        "Mauve": "e0aaff"}
    },

    # https://coolors.co/palette/03071e-370617-6a040f-9d0208-d00000-dc2f02-e85d04-f48c06-faa307-ffba08
    {'lava': {
        "Rich black": "03071e",
        "Chocolate cosmos": "370617",
        "Rosewood": "6a040f",
        "Penn red": "9d0208",
        "Engineering orange": "d00000",
        "Sinopia": "dc2f02",
        "Persimmon": "e85d04",
        "Princeton orange": "f48c06",
        "Orange (web)": "faa307",
        "Selective yellow": "ffba08"}
    },

    # https://coolors.co/palette/ff4800-ff5400-ff6000-ff6d00-ff7900-ff8500-ff9100-ff9e00-ffaa00-ffb600
    {'fire': {
        "Tangelo": "ff4800",
        "Orange (Pantone)": "ff5400",
        "Orange (Pantone) 2": "ff6000",
        "Pumpkin": "ff6d00",
        "Safety orange": "ff7900",
        "UT orange": "ff8500",
        "Princeton orange": "ff9100",
        "Orange peel": "ff9e00",
        "Orange (web)": "ffaa00",
        "Selective yellow": "ffb600"}
    },

    # https://coolors.co/palette/d9ed92-b5e48c-99d98c-76c893-52b69a-34a0a4-168aad-1a759f-1e6091-184e77
    {'greenblue': {
        "Mindaro": "d9ed92",
        "Light green": "b5e48c",
        "Light green 2": "99d98c",
        "Emerald": "76c893",
        "Keppel": "52b69a",
        "Verdigris": "34a0a4",
        "Bondi blue": "168aad",
        "Cerulean": "1a759f",
        "Lapis Lazuli": "1e6091",
        "Indigo dye": "184e77"}
    },

    # https://coolors.co/palette/007f5f-2b9348-55a630-80b918-aacc00-bfd200-d4d700-dddf00-eeef20-ffff3f
    {'neon_grass': {
        "Viridian": "007f5f",
        "Sea green": "2b9348",
        "Kelly green": "55a630",
        "Apple green": "80b918",
        "Yellow Green": "aacc00",
        "Pear": "bfd200",
        "Pear 2": "d4d700",
        "Pear 3": "dddf00",
        "Yellow": "eeef20",
        "Yellow 2": "ffff3f"}
    },

    # https://coolors.co/palette/f94144-f3722c-f8961e-f9844a-f9c74f-90be6d-43aa8b-4d908e-577590-277da1
    {'mexico': {
        "Imperial red": "f94144",
        "Orange (Crayola)": "f3722c",
        "Carrot orange": "f8961e",
        "Coral": "f9844a",
        "Saffron": "f9c74f",
        "Pistachio": "90be6d",
        "Zomp": "43aa8b",
        "Dark cyan": "4d908e",
        "Payne's gray": "577590",
        "Cerulean": "277da1"}
    },

    # https://coolors.co/palette/9b5de5-f15bb5-fee440-00bbf9-00f5d4
    {'pinata': {
        "Amethyst": "9b5de5",
        "Brilliant rose": "f15bb5",
        "Maize": "fee440",
        "Deep Sky Blue": "00bbf9",
        "Aquamarine": "00f5d4"}
    },

    # https://coolors.co/palette/ffbe0b-fb5607-ff006e-8338ec-3a86ff
    {'neon_pinata': {
        "Amber": "ffbe0b",
        "Orange (Pantone)": "fb5607",
        "Rose": "ff006e",
        "Blue Violet": "8338ec",
        "Azure": "3a86ff"}
    },

    # https://coolors.co/palette/28410b-3c5c07-4f7703-719a19-92bd2e-a5d534-603720-6c3e23-784426-9c6544
    {'minecraft': {
        "Pakistan green": "28410b",
        "Dark moss green": "3c5c07",
        "Avocado": "4f7703",
        "Asparagus": "719a19",
        "Apple green": "92bd2e",
        "Yellow Green": "a5d534",
        "Seal brown": "603720",
        "Kobicha": "6c3e23",
        "Russet": "784426",
        "Raw umber": "9c6544"}
    },
]

# These are FastLED predefined palettes
cloud_colors = [
    webcolors.name_to_hex('blue'),
    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('darkblue'),

    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('darkblue'),

    webcolors.name_to_hex('blue'),
    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('skyblue'),
    webcolors.name_to_hex('skyblue'),

    webcolors.name_to_hex('lightblue'),
    webcolors.name_to_hex('white'),
    webcolors.name_to_hex('lightblue'),
    webcolors.name_to_hex('skyblue'),
]
forest_colors = [
    webcolors.name_to_hex('darkgreen'),
    webcolors.name_to_hex('darkgreen'),
    webcolors.name_to_hex('darkolivegreen'),
    webcolors.name_to_hex('darkgreen'),

    webcolors.name_to_hex('green'),
    webcolors.name_to_hex('forestgreen'),
    webcolors.name_to_hex('olivedrab'),
    webcolors.name_to_hex('green'),

    webcolors.name_to_hex('seagreen'),
    webcolors.name_to_hex('mediumaquamarine'),
    webcolors.name_to_hex('limegreen'),
    webcolors.name_to_hex('yellowgreen'),

    webcolors.name_to_hex('lightgreen'),
    webcolors.name_to_hex('lawngreen'),
    webcolors.name_to_hex('mediumaquamarine'),
    webcolors.name_to_hex('forestgreen')
]
heat_colors = [
    0x000000, 0x330000, 0x660000, 0x990000,
    0xCC0000, 0xFF0000, 0xFF3300, 0xFF6600,
    0xFF9900, 0xFFCC00, 0xFFFF00, 0xFFFF33,
    0xFFFF66, 0xFFFF99, 0xFFFFCC, 0xFFFFFF
]
lava_colors = [
    webcolors.name_to_hex('black'),
    webcolors.name_to_hex('maroon'),
    webcolors.name_to_hex('black'),
    webcolors.name_to_hex('maroon'),

    webcolors.name_to_hex('darkred'),
    webcolors.name_to_hex('darkred'),
    webcolors.name_to_hex('maroon'),
    webcolors.name_to_hex('darkred'),

    webcolors.name_to_hex('darkred'),
    webcolors.name_to_hex('darkred'),
    webcolors.name_to_hex('red'),
    webcolors.name_to_hex('orange'),

    webcolors.name_to_hex('white'),
    webcolors.name_to_hex('orange'),
    webcolors.name_to_hex('red'),
    webcolors.name_to_hex('darkred'),
]
ocean_colors = [
    webcolors.name_to_hex('midnightblue'),
    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('midnightblue'),
    webcolors.name_to_hex('navy'),

    webcolors.name_to_hex('darkblue'),
    webcolors.name_to_hex('mediumblue'),
    webcolors.name_to_hex('seagreen'),
    webcolors.name_to_hex('teal'),

    webcolors.name_to_hex('cadetblue'),
    webcolors.name_to_hex('blue'),
    webcolors.name_to_hex('darkcyan'),
    webcolors.name_to_hex('cornflowerblue'),

    webcolors.name_to_hex('aquamarine'),
    webcolors.name_to_hex('seagreen'),
    webcolors.name_to_hex('aqua'),
    webcolors.name_to_hex('lightskyblue'),
]
party_colors = [
    0x5500AB, 0x84007C, 0xB5004B, 0xE5001B,
    0xE81700, 0xB84700, 0xAB7700, 0xABAB00,
    0xAB5500, 0xDD2200, 0xF2000E, 0xC2003E,
    0x8F0071, 0x5F00A1, 0x2F00D0, 0x0007F9
]
rainbow_colors = [
    0xFF0000, 0xD52A00, 0xAB5500, 0xAB7F00,
    0xABAB00, 0x56D500, 0x00FF00, 0x00D52A,
    0x00AB55, 0x0056AA, 0x0000FF, 0x2A00D5,
    0x5500AB, 0x7F0081, 0xAB0055, 0xD5002B
]
rainbow_stripe_colors = [
    0xFF0000, 0x000000, 0xAB5500, 0x000000,
    0xABAB00, 0x000000, 0x00FF00, 0x000000,
    0x00AB55, 0x000000, 0x0000FF, 0x000000,
    0x5500AB, 0x000000, 0xAB0055, 0x000000
]