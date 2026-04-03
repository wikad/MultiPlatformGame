class Map:
    def __init__(self, width, height, map_type):
        self.width = width
        self.height = height
        self.type = map_type

class MapObject:
    def __init__(self, id, x, y, size, hp):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.hp = hp