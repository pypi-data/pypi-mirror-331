from minigrid.core.world_object import Key, Door, Goal

# Define the mapping
grid_world_object_mapping = {
    "Key1": (Key("yellow"), (10, 10)),
    "Key2": (Key("yellow"), (1, 2)),
    "Door": (Door("yellow"), (4, 3)),
    "Green_Goal": (Goal(), (9, 2)),
    "OutsideRoom": (None, (2, 11)),
}