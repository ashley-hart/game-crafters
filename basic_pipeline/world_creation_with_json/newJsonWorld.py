import json
import tcod as libtcod
import time
import cProfile
import argparse

parser = argparse.ArgumentParser(description='World generation simulator')
parser.add_argument('--display', action='store_true', help='Display the world on screen')
parser.add_argument('--config', type=str, default='trail.json', help='Path to configuration JSON file')
parser.add_argument('--output', type=str, help='Base name for output files (without extension)')
args = parser.parse_args()

# Load configuration from JSON file
with open(args.config, "r") as f:
    config = json.load(f)

# Global Parameters from config
WORLD_WIDTH = config["world"]["width"]
WORLD_HEIGHT = config["world"]["height"]
SCREEN_WIDTH = config["screen"]["width"]
SCREEN_HEIGHT = config["screen"]["height"]

CIVILIZED_CIVS = config["civilizations"]["civilized"]
TRIBAL_CIVS = config["civilizations"]["tribal"]
MIN_RIVER_LENGTH = config["world"]["min_river_length"]
CIV_MAX_SITES = config["civilizations"]["max_sites"]
EXPANSION_DISTANCE = config["civilizations"]["expansion_distance"]
WAR_DISTANCE = config["civilizations"]["war_distance"]

pr = cProfile.Profile()
pr.enable()

################################################################################
#                              CLASSES                                         #
################################################################################

class Tile:
    def __init__(self, height, temp, precip, drainage, biome):
        self.height = height
        self.temp = temp
        self.precip = precip
        self.drainage = drainage
        self.biome = biome
        self.hasRiver = False
        self.isCiv = False
        self.biomeID = 0
        self.prosperity = 0

class Race:
    def __init__(self, Name, PrefBiome, Strenght, Size, ReproductionSpeed, Aggressiveness, Form):
        self.Name = Name
        self.PrefBiome = PrefBiome
        self.Strenght = Strenght
        self.Size = Size
        self.ReproductionSpeed = ReproductionSpeed
        self.Aggressiveness = Aggressiveness
        self.Form = Form

class CivSite:
    def __init__(self, x, y, category, suitable, popcap):
        self.x = x
        self.y = y
        self.category = category
        self.suitable = suitable
        self.popcap = popcap
        self.Population = 0
        self.isCapital = False

class Army:
    def __init__(self, x, y, Civ, Size):
        self.x = x
        self.y = y
        self.Civ = Civ
        self.Size = Size

class Civ:
    def __init__(self, Race, Name, Government, Color, Flag, Aggression):
        self.Name = Name
        self.Race = Race
        self.Government = Government
        self.Color = Color
        self.Flag = Flag
        self.Aggression = Race.Aggressiveness + Government.Aggressiveness
        self.Sites = []
        self.SuitableSites = []
        self.atWar = False
        self.Army = Army(None, None, None, None)
        self.TotalPopulation = 0

    def PrintInfo(self):
        print(self.Name)
        print(self.Race.Name)
        print(self.Government.Name)
        print('Aggression:', self.Aggression)
        print('Suitable Sites:', len(self.SuitableSites), '\n')

class GovernmentType:
    def __init__(self, Name, Description, Aggressiveness, Militarization, TechBonus):
        self.Name = Name
        self.Description = Description
        self.Aggressiveness = Aggressiveness
        self.Militarization = Militarization
        self.TechBonus = TechBonus

class War:
    def __init__(self, Side1, Side2):
        self.Side1 = Side1
        self.Side2 = Side2

################################################################################
#                              FUNCTIONS                                       #
################################################################################

def ClearConsole():
    for x in range(SCREEN_WIDTH):
        for y in range(SCREEN_HEIGHT):
            libtcod.console_put_char_ex(0, x, y, ' ', libtcod.black, libtcod.black)
    libtcod.console_flush()

def PointDistRound(pt1x, pt1y, pt2x, pt2y):
    distance = abs(pt2x - pt1x) + abs(pt2y - pt1y)
    return round(distance)

def FlagGenerator(Color):
    # Build a flag using fixed choices from config
    Flag = [[0 for _ in range(4)] for _ in range(12)]
    BackColor1 = Color
    back_color2_index = config["flag_templates"].get("back_color2_index", 0)
    OverColor1_index = config["flag_templates"].get("over_color1_index", 0)
    OverColor2_index = config["flag_templates"].get("over_color2_index", 0)
    BackColor2 = Palette[back_color2_index]
    OverColor1 = Palette[OverColor1_index]
    OverColor2 = Palette[OverColor2_index]

    BackFile = open(config["flag_templates"]["background"], 'r')
    OverlayFile = open(config["flag_templates"]["overlay"], 'r')

    # Determine background and overlay type choices
    Back = config["flag_templates"].get("background_choice", 1)
    Overlay = config["flag_templates"].get("overlay_choice", 1)
    for _ in range(53 * (Back - 1)):
        BackFile.read(1)
    for _ in range(53 * (Overlay - 1)):
        OverlayFile.read(1)

    for y in range(4):
        for x in range(12):
            C = BackFile.read(1)
            while C == '\n':
                C = BackFile.read(1)
            if C == '#':
                Flag[x][y] = BackColor1
            elif C == '"':
                Flag[x][y] = BackColor2

            C = OverlayFile.read(1)
            while C == '\n':
                C = OverlayFile.read(1)
            if C == '#':
                Flag[x][y] = OverColor1
            elif C == '"':
                Flag[x][y] = OverColor2

    BackFile.close()
    OverlayFile.close()
    return Flag

def LowestNeighbour(X, Y, World):
    minval = 1
    newX, newY = 0, 0
    if X + 1 < WORLD_WIDTH and World[X + 1][Y].height < minval:
        minval = World[X + 1][Y].height
        newX, newY = X + 1, Y
    if Y + 1 < WORLD_HEIGHT and World[X][Y + 1].height < minval:
        minval = World[X][Y + 1].height
        newX, newY = X, Y + 1
    if X - 1 > 0 and World[X - 1][Y].height < minval:
        minval = World[X - 1][Y].height
        newX, newY = X - 1, Y
    if Y - 1 > 0 and World[X][Y - 1].height < minval:
        minval = World[X][Y - 1].height
        newX, newY = X, Y - 1

    error = 0
    if newX == 0 and newY == 0:
        error = 1
    return (newX, newY, error)

def PoleGen(hm, NS):
    # NS 0 for south pole, 1 for north pole.
    if NS == 0:
        rng_values = config["world_gen"]["pole_generation"]["south"]["rng_values"]
        fixed_value = config["world_gen"]["pole_generation"]["south"]["fixed_value"]
        for i in range(WORLD_WIDTH):
            rng = rng_values[i % len(rng_values)]
            for j in range(rng):
                libtcod.heightmap_set_value(hm, i, WORLD_HEIGHT - 1 - j, fixed_value)
    elif NS == 1:
        rng_values = config["world_gen"]["pole_generation"]["north"]["rng_values"]
        fixed_value = config["world_gen"]["pole_generation"]["north"]["fixed_value"]
        for i in range(WORLD_WIDTH):
            rng = rng_values[i % len(rng_values)]
            for j in range(rng):
                libtcod.heightmap_set_value(hm, i, j, fixed_value)
    return

def TectonicGen(hm, hor):
    # hor: 0 for vertical, 1 for horizontal tectonic border.
    TecTiles = [[0 for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
    if hor == 1:
        pos = config["world_gen"]["tectonic"]["horizontal"]["position"]
        variation = config["world_gen"]["tectonic"]["horizontal"]["variation"][0]
        for x in range(WORLD_WIDTH):
            TecTiles[x][pos] = 1
            pos += variation
            pos = max(0, min(pos, WORLD_HEIGHT - 1))
    elif hor == 0:
        pos = config["world_gen"]["tectonic"]["vertical"]["position"]
        variation = config["world_gen"]["tectonic"]["vertical"]["variation"][0]
        for y in range(WORLD_HEIGHT):
            TecTiles[pos][y] = 1
            pos += variation
            pos = max(0, min(pos, WORLD_WIDTH - 1))
    for x in range(WORLD_WIDTH // 10, WORLD_WIDTH - WORLD_WIDTH // 10):
        for y in range(WORLD_HEIGHT // 10, WORLD_HEIGHT - WORLD_HEIGHT // 10):
            if TecTiles[x][y] == 1 and libtcod.heightmap_get_value(hm, x, y) > 0.3:
                hill_size = config["world_gen"]["tectonic"].get("hill_size", 3)
                hill_height = config["world_gen"]["tectonic"].get("hill_height", 0.15)
                libtcod.heightmap_add_hill(hm, x, y, hill_size, hill_height)
    return

def Temperature(temp, hm):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            heighteffect = 0
            if y > WORLD_HEIGHT / 2:
                libtcod.heightmap_set_value(temp, x, y, WORLD_HEIGHT - y - heighteffect)
            else:
                libtcod.heightmap_set_value(temp, x, y, y - heighteffect)
            heighteffect = libtcod.heightmap_get_value(hm, x, y)
            if heighteffect > 0.8:
                heighteffect *= 5
                if y > WORLD_HEIGHT / 2:
                    libtcod.heightmap_set_value(temp, x, y, WORLD_HEIGHT - y - heighteffect)
                else:
                    libtcod.heightmap_set_value(temp, x, y, y - heighteffect)
            if heighteffect < 0.25:
                heighteffect *= 10
                if y > WORLD_HEIGHT / 2:
                    libtcod.heightmap_set_value(temp, x, y, WORLD_HEIGHT - y - heighteffect)
                else:
                    libtcod.heightmap_set_value(temp, x, y, y - heighteffect)
    return

def Percipitaion(preciphm, temphm):
    libtcod.heightmap_add(preciphm, config["precipitation"]["offset"])
    precip_noise = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY)
    noise_params = config["precipitation"]["noise_parameters"]
    libtcod.heightmap_add_fbm(preciphm, precip_noise,
                              noise_params["scale"][0],
                              noise_params["scale"][1],
                              0, 0,
                              noise_params["octaves"],
                              1, noise_params["gain"])
    libtcod.heightmap_normalize(preciphm, 0.0, 1.0)
    return

def Prosperity(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            World[x][y].prosperity = (1.0 - abs(World[x][y].precip - 0.6) +
                                       1.0 - abs(World[x][y].temp - 0.5) +
                                       World[x][y].drainage) / 3
    return

def RiverGen(World, start_x, start_y):
    # Use fixed starting coordinates from config
    X = start_x
    Y = start_y
    if World[X][Y].height < 0.8:
        return
    XCoor = [X]
    YCoor = [Y]
    while World[X][Y].height >= 0.2:
        X, Y, error = LowestNeighbour(X, Y, World)
        if error == 1:
            break
        try:
            if (World[X][Y].hasRiver or World[X+1][Y].hasRiver or
                World[X-1][Y].hasRiver or World[X][Y+1].hasRiver or
                World[X][Y-1].hasRiver):
                break
        except IndexError:
            break
        if X in XCoor and Y in YCoor:
            break
        XCoor.append(X)
        YCoor.append(Y)
    if len(XCoor) <= MIN_RIVER_LENGTH:
        return
    for i in range(len(XCoor)):
        if World[XCoor[i]][YCoor[i]].height < 0.2:
            break
        World[XCoor[i]][YCoor[i]].hasRiver = True
    return

def MasterWorldGen():
    print(' * World Gen START * ')
    starttime = time.time()

    # Create heightmap and add hills from config
    hm = libtcod.heightmap_new(WORLD_WIDTH, WORLD_HEIGHT)
    for hill in config["world_gen"]["main_hills"]:
        libtcod.heightmap_add_hill(hm, hill["x"], hill["y"], hill["size"], hill["height"])
    print('- Main Hills -')
    for hill in config["world_gen"]["small_hills"]:
        libtcod.heightmap_add_hill(hm, hill["x"], hill["y"], hill["size"], hill["height"])
    print('- Small Hills -')
    libtcod.heightmap_normalize(hm, 0.0, 1.0)

    noisehm = libtcod.heightmap_new(WORLD_WIDTH, WORLD_HEIGHT)
    noise2d = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY)
    simplex_params = config["world_gen"]["simplex_noise"]["parameters"]
    libtcod.heightmap_add_fbm(noisehm, noise2d,
                              simplex_params["octaves"],
                              simplex_params["frequency"],
                              0, 0,
                              simplex_params["lacunarity"],
                              1, simplex_params["gain"])
    libtcod.heightmap_normalize(noisehm, 0.0, 1.0)
    libtcod.heightmap_multiply_hm(hm, noisehm, hm)
    print('- Apply Simplex -')

    PoleGen(hm, 0)
    print('- South Pole -')
    PoleGen(hm, 1)
    print('- North Pole -')

    TectonicGen(hm, 0)
    TectonicGen(hm, 1)
    print('- Tectonic Gen -')

    libtcod.heightmap_rain_erosion(hm, WORLD_WIDTH * WORLD_HEIGHT,
                                   config["world_gen"]["erosion"]["coefficient"],
                                   0, 0)
    print('- Erosion -')
    libtcod.heightmap_clamp(hm, 0.0, 1.0)

    temp = libtcod.heightmap_new(WORLD_WIDTH, WORLD_HEIGHT)
    Temperature(temp, hm)
    libtcod.heightmap_normalize(temp, 0.0, 1.0)
    print('- Temperature Calculation -')

    preciphm = libtcod.heightmap_new(WORLD_WIDTH, WORLD_HEIGHT)
    Percipitaion(preciphm, temp)
    libtcod.heightmap_normalize(preciphm, 0.0, 1.0)
    print('- Percipitaion Calculation -')

    drainhm = libtcod.heightmap_new(WORLD_WIDTH, WORLD_HEIGHT)
    drain = libtcod.noise_new(2, libtcod.NOISE_DEFAULT_HURST, libtcod.NOISE_DEFAULT_LACUNARITY)
    libtcod.heightmap_add_fbm(drainhm, drain,
                              config["drainage"]["noise_parameters"]["scale"][0],
                              config["drainage"]["noise_parameters"]["scale"][1],
                              0, 0,
                              config["drainage"]["noise_parameters"]["octaves"],
                              1, config["drainage"]["noise_parameters"]["gain"])
    libtcod.heightmap_normalize(drainhm, 0.0, 1.0)
    print('- Drainage Calculation -')

    elapsed_time = time.time() - starttime
    print(' * World Gen DONE *    in: ', elapsed_time, ' seconds')

    World = [[None for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            World[x][y] = Tile(libtcod.heightmap_get_value(hm, x, y),
                                libtcod.heightmap_get_value(temp, x, y),
                                libtcod.heightmap_get_value(preciphm, x, y),
                                libtcod.heightmap_get_value(drainhm, x, y),
                                0)
    print('- Tiles Initialized -')
    Prosperity(World)
    print('- Prosperity Calculation -')

    # Apply biome rules (a simple, fixed ordering here)
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            precip = World[x][y].precip
            temp_val = World[x][y].temp
            drainage = World[x][y].drainage
            height_val = World[x][y].height
            # (For demonstration, a series of if/elif statements replace your random biome assignments.)
            if precip >= 0.10 and precip < 0.33 and drainage < 0.5:
                World[x][y].biomeID = 16
            elif precip >= 0.10 and precip > 0.33:
                World[x][y].biomeID = 2
                if precip >= 0.66:
                    World[x][y].biomeID = 1
            elif precip >= 0.33 and precip < 0.66 and drainage >= 0.33:
                World[x][y].biomeID = 15
            elif temp_val > 0.2 and precip >= 0.66 and drainage > 0.33:
                World[x][y].biomeID = 5
                if precip >= 0.75:
                    World[x][y].biomeID = 6
            elif precip >= 0.10 and precip < 0.33 and drainage >= 0.5:
                World[x][y].biomeID = 14
            elif precip < 0.10:
                World[x][y].biomeID = 4
                if drainage > 0.5:
                    World[x][y].biomeID = 14
                if drainage >= 0.66:
                    World[x][y].biomeID = 8
            if height_val <= 0.2:
                World[x][y].biomeID = 0
            if temp_val <= 0.2 and height_val > 0.15:
                World[x][y].biomeID = 11
            if height_val > 0.6:
                World[x][y].biomeID = 9
            if height_val > 0.9:
                World[x][y].biomeID = 10
    print('- BiomeIDs Atributed -')

    # Use fixed river start coordinates from config
    river_config = config["world_gen"].get("river", {})
    start_x = river_config.get("start_x", 0)
    start_y = river_config.get("start_y", 0)
    RiverGen(World, start_x, start_y)
    print('- River Gen -')

    libtcod.heightmap_delete(hm)
    libtcod.heightmap_delete(temp)
    libtcod.heightmap_delete(noisehm)
    print(' * Biomes/Rivers Sorted *')

    return World

def ReadRaces():
    RacesFile = 'Races.txt'
    NLines = sum(1 for _ in open(RacesFile))
    NRaces = NLines // 7
    f = open(RacesFile)
    Races = [None for _ in range(NRaces)]
    for x in range(NRaces):
        Info = [None for _ in range(7)]
        for y in range(7):
            data = f.readline()
            start = data.index("]") + 1
            end = data.index("\n", start)
            Info[y] = data[start:end]
        PreferedBiomes = [int(s) for s in str.split(Info[1]) if s.isdigit()]
        Races[x] = Race(Info[0], PreferedBiomes, int(Info[2]), int(Info[3]),
                        int(Info[4]), int(Info[5]), Info[6])
    f.close()
    print('- Races Read -')
    return Races

def ReadGovern():
    GovernFile = 'CivilizedGovernment.txt'
    NLines = sum(1 for _ in open(GovernFile))
    NGovern = NLines // 5
    f = open(GovernFile)
    Governs = [None for _ in range(NGovern)]
    for x in range(NGovern):
        Info = [None for _ in range(5)]
        for y in range(5):
            data = f.readline()
            start = data.index("]") + 1
            end = data.index("\n", start)
            Info[y] = data[start:end]
        Governs[x] = GovernmentType(Info[0], Info[1], int(Info[2]), int(Info[3]), int(Info[4]))
    f.close()
    print('- Government Types Read -')
    return Governs

def CivGen(Races, Govern):
    Civs = []
    # Generate civilized civilizations using fixed indices from config
    for i in range(CIVILIZED_CIVS):
        Name = config["names"]["civilized"][i % len(config["names"]["civilized"])] + " " + config["civilizations_config"]["civilized"]["name_suffix"]
        race_index = config["civilizations_config"]["civilized"].get("race_index", 0)
        Race_obj = Races[race_index]
        while Race_obj.Form != "civilized":
            race_index = (race_index + 1) % len(Races)
            Race_obj = Races[race_index]
        gov_index = config["civilizations_config"]["civilized"].get("government_index", 0)
        Government = Govern[gov_index]
        color_hex = config["civilizations_config"]["civilized"]["color"]
        Color = libtcod.Color(int(color_hex[1:3], 16),
                              int(color_hex[3:5], 16),
                              int(color_hex[5:7], 16))
        Flag = FlagGenerator(Color)
        Civs.append(Civ(Race_obj, Name, Government, Color, Flag, 0))
    # Generate tribal civilizations similarly
    for i in range(TRIBAL_CIVS):
        Name = config["names"]["tribal"][i % len(config["names"]["tribal"])] + " " + config["civilizations_config"]["tribal"]["name_suffix"]
        race_index = config["civilizations_config"]["tribal"].get("race_index", 0)
        Race_obj = Races[race_index]
        while Race_obj.Form != "tribal":
            race_index = (race_index + 1) % len(Races)
            Race_obj = Races[race_index]
        Government = GovernmentType(
            config["civilizations_config"]["tribal"]["government"]["name"],
            config["civilizations_config"]["tribal"]["government"]["description"],
            config["civilizations_config"]["tribal"]["government"]["aggressiveness"],
            config["civilizations_config"]["tribal"]["government"]["militarization"],
            config["civilizations_config"]["tribal"]["government"]["tech_bonus"]
        )
        color_hex = config["civilizations_config"]["tribal"]["color"]
        Color = libtcod.Color(int(color_hex[1:3], 16),
                              int(color_hex[3:5], 16),
                              int(color_hex[5:7], 16))
        Flag = FlagGenerator(Color)
        Civs.append(Civ(Race_obj, Name, Government, Color, Flag, 0))
    print('- Civs Generated -')
    return Civs

def SetupCivs(Civs, World, Chars, Colors):
    for civ in Civs:
        civ.Sites = []
        civ.SuitableSites.clear()
        for i in range(WORLD_WIDTH):
            for j in range(WORLD_HEIGHT):
                for biome in civ.Race.PrefBiome:
                    if World[i][j].biomeID == biome:
                        civ.SuitableSites.append(CivSite(i, j, "", 1, 0))
        fixed_site_index = config["civilizations_config"].get("initial_site_index", 0)
        if not civ.SuitableSites:
            # Fallback: assign a default tile (e.g., (0, 0)) or handle the error
            print(f"No suitable sites found for civilization: {civ.Name}. Assigning default location (0,0).")
            X, Y = 0, 0
        else:
            # If the fixed index is out-of-range, use the first available site.
            if fixed_site_index >= len(civ.SuitableSites):
                print(f"initial_site_index ({fixed_site_index}) is out of range for {civ.Name}; using first available site.")
                fixed_site_index = 0
            X = civ.SuitableSites[fixed_site_index].x
            Y = civ.SuitableSites[fixed_site_index].y

        World[X][Y].isCiv = True
        
        FinalProsperity = World[X][Y].prosperity * 150
        if World[X][Y].hasRiver:
            FinalProsperity *= 1.5
        PopCap = 4 * civ.Race.ReproductionSpeed + FinalProsperity
        PopCap = round(PopCap * 2)  # Capital bonus
        civ.Sites.append(CivSite(X, Y, "Village", 0, PopCap))
        civ.Sites[0].isCapital = True
        civ.Sites[0].Population = 20

        Chars[X][Y] = 31
        Colors[X][Y] = civ.Color

        civ.PrintInfo()
        
    print('- Civs Setup -')
    print(' * Civ Gen DONE *')
    return Civs


def NewSite(Civ, Origin, World, Chars, Colors):
    fixed_index = config["civilizations_config"].get("new_site_index", 0)
    X = Civ.SuitableSites[fixed_index].x
    Y = Civ.SuitableSites[fixed_index].y
    World[X][Y].isCiv = True
    FinalProsperity = World[X][Y].prosperity * 150
    if World[X][Y].hasRiver:
        FinalProsperity *= 1.5
    PopCap = round(3 * Civ.Race.ReproductionSpeed + FinalProsperity)
    Civ.Sites.append(CivSite(X, Y, "Village", 0, PopCap))
    Civ.Sites[-1].Population = 20
    Chars[X][Y] = 31
    Colors[X][Y] = Civ.Color
    global needUpdate
    needUpdate = True
    return Civ

def ProcessCivs(World, Civs, Chars, Colors, Month):
    print("------------------------------------------")
    for civ in Civs:
        print(civ.Name)
        print(civ.Race.Name)
        civ.TotalPopulation = 0
        for site in civ.Sites:
            NewPop = int(round(site.Population * civ.Race.ReproductionSpeed / 1500))
            if site.Population > site.popcap / 2:
                NewPop //= 6
            site.Population += NewPop
            if site.Population > site.popcap:
                site.Population = int(round(site.popcap))
                if len(civ.Sites) < CIV_MAX_SITES:
                    site.Population = int(round(site.popcap / 2))
                    civ = NewSite(civ, site, World, Chars, Colors)
            civ.TotalPopulation += site.Population
            for other in Civs:
                if other == civ:
                    continue
                for other_site in other.Sites:
                    if PointDistRound(site.x, site.y, other_site.x, other_site.y) < WAR_DISTANCE:
                        alreadyWar = False
                        for war in Wars:
                            if (war.Side1 == civ and war.Side2 == other) or (war.Side1 == other and war.Side2 == civ):
                                alreadyWar = True
                        if not alreadyWar:
                            Wars.append(War(civ, other))
                            if not other.atWar:
                                other.Army = Army(other.Sites[0].x,
                                                  other.Sites[0].y,
                                                  other,
                                                  other.TotalPopulation * other.Government.Militarization / 100)
                                other.atWar = True
                            if not civ.atWar:
                                civ.Army = Army(civ.Sites[0].x,
                                                civ.Sites[0].y,
                                                civ,
                                                civ.TotalPopulation * civ.Government.Militarization / 100)
                                civ.atWar = True
            print(f"X: {site.x} Y: {site.y} Population: {site.Population}")
        print(f"{civ.Army.x} {civ.Army.y} {civ.Army.Size}\n")
    return

def TerrainMap(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            hm_v = World[x][y].height
            libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '0', libtcod.blue, libtcod.black)
            if hm_v > 0.1:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '1', libtcod.blue, libtcod.black)
            if hm_v > 0.2:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '2', Palette[0], libtcod.black)
            if hm_v > 0.3:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '3', Palette[0], libtcod.black)
            if hm_v > 0.4:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '4', Palette[0], libtcod.black)
            if hm_v > 0.5:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '5', Palette[0], libtcod.black)
            if hm_v > 0.6:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '6', Palette[0], libtcod.black)
            if hm_v > 0.7:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '7', Palette[0], libtcod.black)
            if hm_v > 0.8:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '8', libtcod.dark_sepia, libtcod.black)
            if hm_v > 0.9:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '9', libtcod.light_gray, libtcod.black)
            if hm_v > 0.99:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '^', libtcod.darker_gray, libtcod.black)
    libtcod.console_flush()
    return

# def BiomeMap(Chars, Colors):
#     for x in range(WORLD_WIDTH):
#         for y in range(WORLD_HEIGHT):
#             libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, Chars[x][y], Colors[x][y], libtcod.black)
#     libtcod.console_flush()
#     return

def BiomeMap(Chars, Colors):
    # Create a 2D array to store ASCII characters for the file output
    map_chars = [[' ' for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
    
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            # Store the character for file output
            if isinstance(Chars[x][y], int):
                map_chars[x][y] = chr(Chars[x][y])
            else:
                map_chars[x][y] = Chars[x][y]
                
            # Only display if --display flag is set
            if args.display:
                libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, 
                                           Chars[x][y], Colors[x][y], libtcod.black)
    
    if args.display:
        libtcod.console_flush()
    
    # Export to text file
    export_to_file("biome_map.txt", map_chars)
    
    return

def HeightGradMap(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            hm_v = World[x][y].height
            HeightColor = libtcod.Color(255, 255, 255)
            libtcod.color_set_hsv(HeightColor, 0, 0, hm_v)
            libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '\333', HeightColor, libtcod.black)
    libtcod.console_flush()
    return

def TempGradMap(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            tempv = World[x][y].temp
            tempcolor = libtcod.color_lerp(libtcod.white, libtcod.red, tempv)
            libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '\333', tempcolor, libtcod.black)
    libtcod.console_flush()
    return

def PrecipGradMap(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            tempv = World[x][y].precip
            tempcolor = libtcod.color_lerp(libtcod.white, libtcod.light_blue, tempv)
            libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '\333', tempcolor, libtcod.black)
    libtcod.console_flush()
    return

def DrainageGradMap(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            drainv = World[x][y].drainage
            draincolor = libtcod.color_lerp(libtcod.darkest_orange, libtcod.white, drainv)
            libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '\333', draincolor, libtcod.black)
    libtcod.console_flush()
    return

def ProsperityGradMap(World):
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            prosperitynv = World[x][y].prosperity
            prosperitycolor = libtcod.color_lerp(libtcod.white, libtcod.darker_green, prosperitynv)
            libtcod.console_put_char_ex(0, x, y + SCREEN_HEIGHT // 2 - WORLD_HEIGHT // 2, '\333', prosperitycolor, libtcod.black)
    libtcod.console_flush()
    return

def NormalMap(World):
    Chars = [[0 for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
    Colors = [[0 for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
    def SymbolDictionary(x):
        # Return a symbol based on the biomeID.
        if x in (15, 8):
            char = 251
        elif x == 1:
            char = 244
        elif x == 2:
            char = '"'
        else:
            char = '?'
        symbols = {
            0: '\367',
            1: char,
            2: char,
            3: 'n',
            4: '\367',
            5: 24,
            6: 6,
            8: char,
            9: 127,
            10: 30,
            11: 176,
            12: 177,
            13: 178,
            14: 'n',
            15: char,
            16: 139
        }
        return symbols.get(x, '?')
    def ColorDictionary(x):
        badlands = libtcod.Color(204, 159, 81)
        icecolor = libtcod.Color(176, 223, 215)
        darkgreen = libtcod.Color(68, 158, 53)
        lightgreen = libtcod.Color(131, 212, 82)
        water = libtcod.Color(13, 103, 196)
        mountain = libtcod.Color(185, 192, 162)
        desert = libtcod.Color(255, 218, 90)
        colors = {
            0: water,
            1: darkgreen,
            2: lightgreen,
            3: lightgreen,
            4: desert,
            5: darkgreen,
            6: darkgreen,
            8: badlands,
            9: mountain,
            10: mountain,
            11: icecolor,
            12: icecolor,
            13: icecolor,
            14: darkgreen,
            15: lightgreen,
            16: darkgreen
        }
        return colors.get(x, libtcod.white)
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            Chars[x][y] = SymbolDictionary(World[x][y].biomeID)
            Colors[x][y] = ColorDictionary(World[x][y].biomeID)
            if World[x][y].hasRiver:
                Chars[x][y] = 'o'
                Colors[x][y] = libtcod.light_blue
    return Chars, Colors

def export_to_file(filename, map_chars):
    # Use custom output name if provided, otherwise use the default with timestamp
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    if args.output:
        base_name = args.output
        # If output doesn't include file type, use the original filename's type
        if '.' not in base_name:
            output_filename = f"{base_name}"
        else:
            output_filename = base_name
    else:
        output_filename = f"{filename.split('.')[0]}_{timestamp}.txt"
    
    with open(output_filename, 'w') as f:
        # Add a timestamp and information header
        # f.write(f"# Map generated on {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        # f.write(f"# World size: {WORLD_WIDTH}x{WORLD_HEIGHT}\n")
        # f.write(f"# Generated from config: {args.config}\n\n")
        
        # Write the map by rows
        for y in range(WORLD_HEIGHT):
            row = ""
            for x in range(WORLD_WIDTH):
                row += map_chars[x][y]
            f.write(row + '\n')
    return

################################################################################
#                              STARTUP                                         #
################################################################################

# Only initialize the display if the --display argument is set
if args.display:
    # Set custom font and initialize console
    libtcod.console_set_custom_font("Andux_cp866ish.png", libtcod.FONT_LAYOUT_ASCII_INROW)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'pyWorld', False, libtcod.RENDERER_SDL)


# Palette (example colors)
Palette = [
    libtcod.Color(255, 45, 33),    # Red
    libtcod.Color(254, 80, 0),     # Orange
    libtcod.Color(0, 35, 156),     # Blue
    libtcod.Color(71, 45, 96),     # Purple
    libtcod.Color(0, 135, 199),    # Ocean Blue
    libtcod.Color(254, 221, 0),    # Yellow
    libtcod.Color(255, 255, 255),  # White
    libtcod.Color(99, 102, 106)    # Gray
]

isRunning = False
needUpdate = False

World = MasterWorldGen()
Chars, Colors = NormalMap(World)
Races = ReadRaces()
Govern = ReadGovern()
Civs = [None for _ in range(CIVILIZED_CIVS + TRIBAL_CIVS)]
Civs = CivGen(Races, Govern)
Civs = SetupCivs(Civs, World, Chars, Colors)
BiomeMap(Chars, Colors)

Month = 0
Wars = []
Wars.clear()
if args.display:
    # Main simulation loop
    while not libtcod.console_is_window_closed():
        while isRunning:
            ProcessCivs(World, Civs, Chars, Colors, Month)
            Month += 1
            print(f'Month: {Month}')
            libtcod.console_check_for_keypress(True)
            if libtcod.console_is_key_pressed(libtcod.KEY_SPACE):
                isRunning = False
                print("*PAUSED*")
                time.sleep(1)
            if needUpdate:
                BiomeMap(Chars, Colors)
                needUpdate = False
        key = libtcod.console_wait_for_keypress(True)
        if libtcod.console_is_key_pressed(libtcod.KEY_SPACE):
            isRunning = True
            print("*RUNNING*")
            time.sleep(1)
        if libtcod.console_is_key_pressed(libtcod.KEY_ESCAPE):
            isRunning = False
            pr.disable()
            pr.print_stats(sort='time')
        if key.vk == libtcod.KEY_CHAR:
            if key.c == ord('t'):
                TerrainMap(World)
            elif key.c == ord('h'):
                HeightGradMap(World)
            elif key.c == ord('w'):
                TempGradMap(World)
            elif key.c == ord('p'):
                PrecipGradMap(World)
            elif key.c == ord('d'):
                DrainageGradMap(World)
            elif key.c == ord('f'):
                ProsperityGradMap(World)
            elif key.c == ord('b'):
                BiomeMap(Chars, Colors)
            elif key.c == ord('r'):
                print("\n" * 100)
                print(" * NEW WORLD *")
                Month = 0
                Wars.clear()
                World = MasterWorldGen()
                Races = ReadRaces()
                Govern = ReadGovern()
                Civs = CivGen(Races, Govern)
                Chars, Colors = NormalMap(World)
                SetupCivs(Civs, World, Chars, Colors)
                BiomeMap(Chars, Colors) 
            elif key.c == ord('q'):
                break

else:
    # Non-interactive mode - just generate all maps and exit
    print("Running in non-interactive mode. Generating maps...")
    
    # Generate all map types
    TerrainMap(World)
    HeightGradMap(World)
    TempGradMap(World)
    PrecipGradMap(World)
    DrainageGradMap(World)
    ProsperityGradMap(World)
    BiomeMap(Chars, Colors)
    
    print("All maps generated successfully. Exiting...") 
