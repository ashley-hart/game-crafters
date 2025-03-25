import numpy as np
from world_config import MapSizes, Biome, biome_dict
from utility_methods import print_grid
    
# ! Do I even need this class?
# Creating biome masks to be used by the world  
# generator as a preprocessing step.
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
        
        # print(f"Creating biome mask for {{ {region}, {biome} }}...")
        
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
    
    user_params = {'north': 'desert',
                   'south': 'mountains',
                   'southwest': 'desert',
                   'center': 'forest'}
    b_mask = create_biome_mask(MapSizes.SMALL_MAP.value, user_params)
    
    print(f"Displaying base biome mask")
    print_grid(b_mask)
       
    print(f"Displaying final biome mask")
    print_grid(b_mask)