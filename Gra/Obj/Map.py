
# struct MapObject {
#     int id;
#     float x, y;
#     int size;
#     int hp;
# };

# struct Map {
#     int width;
#     int height;
#     enum MapType {
#         Sand,
#         Grass,
#     } type ;
# };

# struct Tower {
#     struct MapObject base;
#     int range;
#     int damage;
# };
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

class Tower(MapObject):
    def __init__(self, id, x, y, size, hp, range, damage):
        super().__init__(id, x, y, size, hp)
        self.range = range
        self.damage = damage