### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

bl_info = {
    "name": "Snap_Utilities_Line",
    "author": "Germano Cavalcante",
    "version": (5, 9, 00),
    "blender": (2, 80, 0),
    "location": "View3D > TOOLS > Line Tool",
    "description": "Extends Blender Snap controls",
    #"wiki_url" : "http://blenderartists.org/forum/showthread.php?363859-Addon-CAD-Snap-Utilities",
    "category": "Mesh"}

if "bpy" in locals():
    import importlib
    importlib.reload(common_classes)
    importlib.reload(preferences)
    importlib.reload(ops_line)
else:
    from . import common_classes
    from . import preferences
    from . import ops_line

import bpy
from bpy.utils.toolsystem import ToolDef

if not __package__:
    __package__ = "mesh_snap_utilities_line"

@ToolDef.from_fn
def tool_line():
    import os
    def draw_settings(context, layout, tool):
        addon_prefs = context.preferences.addons[__package__].preferences

        layout.prop(addon_prefs, "incremental")
        layout.prop(addon_prefs, "increments_grid")
        layout.prop(addon_prefs, "intersect")
        layout.prop(addon_prefs, "create_face")
        if context.mode == 'EDIT_MESH':
            layout.prop(addon_prefs, "outer_verts")
        #props = tool.operator_properties("mesh.snap_utilities_line")
        #layout.prop(props, "radius")

    icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    return dict(
        text="Make Line",
        description=(
            "Make Lines\n"
            "Connect them to split faces"
        ),
        icon=os.path.join(icons_dir, "ops.mesh.snap_utilities_line"),
        widget="MESH_GGT_snap_point",
        #operator="mesh.snap_utilities_line",
        keymap="3D View Tool: Edit Mesh, Make Line",
        draw_settings=draw_settings,
    )


# -----------------------------------------------------------------------------
# Tool Registraion

def km_3d_view_snap_tools(tool_mouse = 'LEFTMOUSE'):
    return [(
        tool_line.keymap[0],
        {"space_type": 'VIEW_3D', "region_type": 'WINDOW'},
        {"items": [
            ("mesh.snap_utilities_line", {"type": tool_mouse, "value": 'CLICK'},
             {"properties": [("wait_for_input", False)]}),
        ]},
    )]


def get_tool_list(space_type, context_mode):
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    return cls._tools[context_mode]


def register_snap_tools():
    tools = get_tool_list('VIEW_3D', 'EDIT_MESH')

    for index, tool in enumerate(tools, 1):
        if isinstance(tool, ToolDef) and tool.text == "Measure":
            break

    tools[:index] += None, tool_line

    del tools

    keyconfigs = bpy.context.window_manager.keyconfigs
    kc_defaultconf = keyconfigs.get("blender")
    kc_addonconf   = keyconfigs.get("blender addon")

    keyconfig_data = km_3d_view_snap_tools()

    # TODO: find the user defined tool_mouse.
    from bl_keymap_utils.io import keyconfig_init_from_data
    keyconfig_init_from_data(kc_defaultconf, keyconfig_data)
    keyconfig_init_from_data(kc_addonconf, keyconfig_data)


def unregister_snap_tools():
    tools = get_tool_list('VIEW_3D', 'EDIT_MESH')

    index = tools.index(tool_line) - 1 #None
    tools.pop(index)
    tools.remove(tool_line)

    del tools
    del index

    keyconfigs = bpy.context.window_manager.keyconfigs
    defaultmap = keyconfigs.get("blender").keymaps
    addonmap   = keyconfigs.get("blender addon").keymaps

    for keyconfig_data in km_3d_view_snap_tools():
        km_name, km_args, km_content = keyconfig_data

        addonmap.remove(addonmap.find(km_name, **km_args))
        defaultmap.remove(defaultmap.find(km_name, **km_args))


# -----------------------------------------------------------------------------
# Addon Registraion

classes = (
    preferences.SnapUtilitiesLinePreferences,
    ops_line.SnapUtilitiesLine,
    common_classes.VIEW3D_OT_rotate_custom_pivot,
    common_classes.VIEW3D_OT_zoom_custom_target,
    common_classes.SnapPointWidget,
    common_classes.SnapPointWidgetGroup,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    register_snap_tools()


def unregister():
    unregister_snap_tools()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
