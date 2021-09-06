# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Unreal Engine Export",
    "author" : "Michael Wahlhuetter",
    "description" : "A simple addon for a better workflow for UE",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > UI > Unreal Export",
    "warning" : "",
    "category" : "Import-Export"
}

import bpy
import mathutils
import os
from .ui import ue_view3d_ui

if "bpy" in locals():
    import importlib
    if "ue_view3d_ui" in locals():
        importlib.reload(ue_view3d_ui)

def register():
    ue_view3d_ui.register()

def unregister():
    ue_view3d_ui.unregister()

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()