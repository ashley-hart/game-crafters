from map import Map


def run(game_map, map_w, map_h) -> None:
    while True:
        game_map.display_map()
        user_input = input("> ")
        
        if user_input in ["QUIT", "quit", "q", "exit"]:
            break
        if user_input == "\n":
            print("Generating new map...")
            game_map = Map(map_w, map_h)
        
if __name__ == "__main__":
    map_w, map_h = 30, 15
    game_map = Map(map_w, map_h)
    run(game_map, map_h, map_w)