import csv
import pathlib
from PIL import Image
from random import randint

########################################################################
# Settings - Change as required
########################################################################

# Maximum number of each rarity
MAX_RARITY_COUNT_LIST = {
    "Legendary": 25,
    "Mythic": 100,
    "Rare": 175,
    "Uncommon": 300,
    "Common": 400,
}

TOTAL_ARTWORK = 1000

# Name of your artwork
NAME = 'NFT Artwork Name'

# Mapping of Rarity Type to Base Number
BASES = {
    "Legendary": 5,  # Legendary is Pink Base
    "Mythic": 4,  # Mythic is Purple Base
    "Rare": 3,  # Rare is Blue Base
    "Uncommon": 2,  # Uncommon is Green Base
    "Common": 1,  # Common is Orange Base
}

# Name of the parts starts from 1 onwards
PART_NAMES = {
    # "part folder name" : ["part file number 1", "part file number 2", "part file number 3" and so on]
    "base": ["Orange", "Green", "Blue", "Purple", "Pink"],
    "left_leg": ["Orange Left Leg", "Green Left Leg", "Blue Left Leg", "Purple Left Leg", "Pink Left Leg"],
    "right_leg": ["Orange Right Leg", "Green Right Leg", "Blue Right Leg", "Purple Right Leg", "Pink Right Leg"],
    "left_arm": ["Orange Left Arm", "Green Left Arm", "Blue Left Arm", "Purple Left Arm", "Pink Left Arm"],
    "right_arm": ["Orange Right Arm", "Green Right Arm", "Blue Right Arm", "Purple Right Arm", "Pink Right Arm"],
    "body": ["Orange Body", "Green Body", "Blue Body", "Purple Body", "Pink Body"],
    "head": ["Orange Head", "Green Head", "Blue Head", "Purple Head", "Pink Head"],
}

# No Change Required Unless You Want To

# Start and End ID of Generated NFTs
START_ID = 1
CSV_FILE_NAME = "nft-info.csv"

########################################################################
# Data - No change required
########################################################################

RARITY = []
PROBABILITY_COUNT = []

# Trackers
RELEASED_NFT_LIST = []
RARITY_COUNTER = {}

for key, value in MAX_RARITY_COUNT_LIST.items():
    RARITY.append(key)
    PROBABILITY_COUNT.append((value, key))
    RARITY_COUNTER[key] = 0

# Current folder directory path
FOLDER_PATH = str(pathlib.Path(__file__).parent.resolve())

# Check existing CSV for released NFTs
my_file = pathlib.Path(CSV_FILE_NAME)
if my_file.is_file():
    with open(CSV_FILE_NAME, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        print("Loading %s..." % CSV_FILE_NAME)
        for row in spamreader:
            # Add each entry to RELEASED LIST
            RELEASED_NFT_LIST.append('-'.join(row[2:-1]))
            # Calculate current rarity list
            if row[1] not in RARITY_COUNTER:
                RARITY_COUNTER[row[1]] = 0
            # Add each Rarity found to counter
            RARITY_COUNTER[row[1]] += 1
        print("===== CURRENT LOADED RARITY COUNT =====")
        print(RARITY_COUNTER)
else:
    CSV_HEADER = ["name", "rarity"]
    for key, value in PART_NAMES.items():
        CSV_HEADER.append(key)
    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(CSV_HEADER)
    print("Created %s CSV File" % CSV_FILE_NAME)


########################################################################
# Utility code
########################################################################

def _compose_image(image_files, token_id):
    composite = None
    for image_file in image_files:
        foreground = Image.open(image_file).convert('RGBA')

        if composite:
            composite = Image.alpha_composite(composite, foreground)
        else:
            composite = foreground

    output_path = 'output/%s.png' % token_id
    composite.save(output_path)

########################################################################
# Calculation Helpers
########################################################################


def weighted_random(pairs):
    total = sum(pair[0] for pair in pairs)
    r = randint(1, total)
    for (weight, value) in pairs:
        r -= weight
        if r <= 0:
            return value

########################################################################
# Artwork Generation
########################################################################


for token_id in range(START_ID, TOTAL_ARTWORK + 1):
    token_id = int(token_id)
    art_name = '%s #%s' % (NAME, token_id)
    tracker = []
    traits_tracker = []
    traitIsInList = True
    rarity = weighted_random(PROBABILITY_COUNT)

    while traitIsInList:
        if RARITY_COUNTER[rarity] < MAX_RARITY_COUNT_LIST[rarity]:
            base = BASES[rarity]
            traits_tracker.append(str(base))
            for i in range(1, len(PART_NAMES)):
                traits_tracker.append(
                    str(randint(1, len(MAX_RARITY_COUNT_LIST))))
            current_art_traits = "-".join(traits_tracker)
            if current_art_traits not in RELEASED_NFT_LIST:
                RELEASED_NFT_LIST.append(current_art_traits)
                RARITY_COUNTER[rarity] += 1
                traitIsInList = False

    PART_FILE_PATHS = []
    part_index = 0
    for key, value in PART_NAMES.items():
        PART_FILE_PATHS.append('input/%s/%s.png' %
                               (key, traits_tracker[part_index]))
        part_index += 1

    _compose_image(PART_FILE_PATHS, token_id)
    print("Generated %s image" % art_name)

    # Add to CSV
    meta_info = [art_name, rarity]
    part_index = 0
    for key, value in PART_NAMES.items():
        meta_info.append(PART_NAMES[key][int(traits_tracker[part_index])-1])
        part_index += 1

    with open(CSV_FILE_NAME, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(meta_info)
    print("Wrote %s to CSV file" % art_name)
    print("===== RARITY COUNT =====")
    print(RARITY_COUNTER)
print("Completed Generation of %s" % art_name)
