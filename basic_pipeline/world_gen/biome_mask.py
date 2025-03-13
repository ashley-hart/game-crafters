# Creating biome masks to be used by the world  
# generator as a preprocessing step.

from enum import Enum
import numpy as np
# from pygame_main import SMALL_MAP, MEDIUM_MAP, LARGE_MAP
EXTRA_SMALL_MAP = 9 # n = 3
SMALL_MAP = 17 # n = 4
MEDIUM_MAP = 33 # n = 5
LARGE_MAP = 65 # n = 6
EXTRA_LARGE_MAP = 129 # n = 7

class Biome(Enum):
    WATER = 0
    DESERT = 1
    PLAINS = 2
    FOREST = 3
    TUNDRA = 4
    MOUNTAINS = 5
    
biome_dict = {
    'water': Biome.WATER,
    'desert': Biome.DESERT,
    'plains': Biome.PLAINS,
    'forest': Biome.FOREST,
    'tundra': Biome.TUNDRA,
    'mountains': Biome.MOUNTAINS,
}
    
class BiomeMask():
    
    def __init__(self, size):
        self.width = size
        self.height = size
        self.mask = []
        
        for _ in range(0, size):
            self.mask.append([Biome.WATER for _ in range(0, size)])
            
def print_mask(mask):
    for row in mask:
        print("".join(str(cell.value) for cell in row))
        # print("".join(str(cell) for cell in row))
            
def create_biome_mask(size, user_params):
    # Plains is the default biome
    # mask = np.full((size, size), 'plains', dtype=object)
    mask = np.full((size, size), biome_dict['plains'], dtype=object)
    
    print(f"Creating a biome mask with the following items: ", user_params.items())
    
    for region, biome in user_params.items():
        
        print(f"Creating biome mask for {{ {region}, {biome} }}...")
        
        if region == 'north':
            mask[:size//3, :] = biome_dict[biome]
        elif region == 'south':
            mask[-size//3:, :] = biome_dict[biome]
        elif region == 'east':
            mask[:, -size//3:] = biome_dict[biome]
        elif region == 'west':
            mask[:, :-size//3] = biome_dict[biome]
        elif region == 'northeast':
            mask[:size//3, -size//3:] = biome_dict[biome]
        elif region == 'northwest':
            mask[:size//3, :size//3] = biome_dict[biome]
        elif region == 'southeast':
            mask[-size//3:, -size//3:] = biome_dict[biome]
        elif region == 'southwest':
            mask[-size//3:, :size//3] = biome_dict[biome]
        elif region == 'center':
            center = size // 2
            radius = size // 6
            mask[center-radius-1:center+radius+1, center-radius-1:center+radius+1] = biome_dict[biome]
        else:
            print("Invalid region provided: ", region)
            return None
        
    return mask 
        
        
if __name__ == "__main__":
    print(f"Creating a biome mask")
    # b_mask = BiomeMask(EXTRA_SMALL_MAP)
    # b_mask = BiomeMask(SMALL_MAP)
    print(f"Displaying biome mask")
    # print(b_mask.print_mask())
    
    user_params = {'north': 'desert',
                   'south': 'mountains',
                   'center': 'forest'}
    b_mask = create_biome_mask(SMALL_MAP, user_params)
    print_mask(b_mask)
    print(Biome(1))
    
    
            