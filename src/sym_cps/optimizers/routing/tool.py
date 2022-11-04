"""Some basic data structure for routing"""

class Coordinate_3d(object):
    def __init__(self, x: float, y: float, z: float):
        self._coordinate = [x, y, z]

    @property
    def x(self) -> float:
        return self._coordinate[0]
    @property
    def y(self) -> float:
        return self._coordinate[1]
    @property
    def z(self) -> float:
        return self._coordinate[2]
    @x.setter
    def x(self, val: float) :
        self._coordinate[0] = val
    @y.setter
    def y(self, val: float) :
        self._coordinate[1] = val
    @z.setter
    def z(self, val: float) :
        self._coordinate[2] = val

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


class Net(object):
    def __init__(self, end_1:Coordinate_3d, end_2: Coordinate_3d):
        self._end = []
        self._end.append(end_1)
        self._end.append(end_2)

    @property
    def ends() -> tuple[Coordinate_3d, Coordinate_3d]:
        return ()
    @property
    def end_1(self):
        return self._end[0]
    @property
    def end_2(self):
        return self._end[1]

    @end_1.setter
    def end_1(self, end_1: Coordinate_3d):
        self._end[0] = end_1

    @end_2.setter
    def end_2(self, end_2: Coordinate_3d):
        self._end[0] = end_2
        
class RoutingGrid(object):
    def __init__(self, num_x, num_y, num_z, width_x, width_y, width_z):
        """Create a routing grid with (x by y by z grids) and the real distance between each grid is width_x/width_y/width_z"""
        self._set_grids(num_x=num_x, num_y=num_y, num_z=num_z)
        self._width = [width_x, width_y, width_z]

    def _set_grids(self, num_x, num_y, num_z):
        self._grids = [[[None for i in range(num_x)] for j in range(num_y)] for k in range(num_z)]

    def get_grid_coor(self, coor: Coordinate_3d):
        return self._grids[coor.x][coor.y][coor.z]

    def get_grid(self, x, y, z):
        return self._grids[x][y][z]

    def check_empty_coor(self, coor: Coordinate_3d):
        return self._grids[coor.x][coor.y][coor.z] is None

    def check_empty(self, x, y, z):
        return self._grids[x][y][z] is None

    def print_if_exist(self):
        find = False
        for z, layer in enumerate(self._grids):
            for y, col in enumerate(layer):
                for x, element in enumerate(col):
                    if element:
                        print(element)
                        find = True
        if not find:
            print("Empty Grid!")

# grids = RoutingGrid(num_x=6, num_y=8, num_z=10, width_x=2, width_y=2, width_z=3)
# print(grids.get_grid_coor(Coordinate_3d(3,4,5)))
# grids.print_if_exist()