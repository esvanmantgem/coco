# Copyright (c) 2022, Eline van Mantgem
#
# This file is part of Coco.
#
# Coco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Coco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Coco. If not, see <http://www.gnu.org/licenses/>.
import constant as c

class FeatureMap:

    def __init__(self, fid, pu, min_val, max_val, x, y, geotransform, projection, no_data):
        self.fid = fid
        self.pu = pu
        self.min_val = min_val
        self.max_val = max_val
        self.x_length = x
        self.y_length = y
        self.geotransform = geotransform
        self.projection = projection
        self.no_data = no_data
