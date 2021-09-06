import bpy
import os
from ..export import ue_export_sm
from ..utils import ue_operators

if "bpy" in locals():
    import importlib
    if "ue_export_sm" in locals():
        importlib.reload(ue_export_sm)
    if "ue_operators" in locals():
        importlib.reload(ue_operators)

class UE_PT_Global_Properties(bpy.types.Panel):
    bl_label = "Global Properties"
    bl_category = "Unreal Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bpy.types.Scene.ue_export_prefix = bpy.props.StringProperty(
        name="Prefix",
        maxlen=64,
        default="SM_")

    bpy.types.Scene.ue_output_path = bpy.props.StringProperty(
        name = "Export Dir",
        maxlen = 1024,
        default = "//",
        subtype = 'DIR_PATH')

    bpy.types.Scene.ue_overwrite = bpy.props.BoolProperty(
        name="Override Existing",
        description=(''),
        default=True
        )

    bpy.types.Scene.ue_export_tangents = bpy.props.BoolProperty(
        name="Export Tangents",
        default=True
        )

    bpy.types.Scene.ue_smoothing_type = bpy.props.EnumProperty(
        name="Smoothing",
        items=[
            ('OFF', "Normals Only", "", 0),
            ('FACE', "Face", "", 1),
            ],
        default="FACE"
        )

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        overwrite = layout.row(align=True)
        overwrite.prop(scene, 'ue_overwrite')

        overwrite = layout.row()
        overwrite.prop(scene, 'ue_export_tangents')

        smoothingType = layout.row()
        smoothingType.prop(scene, 'ue_smoothing_type')

        filePath = layout.column()
        filePath.prop(scene, 'ue_export_prefix')
        filePath.prop(scene, 'ue_output_path')

        export = layout.row()
        export.scale_y = 1.5
        export.operator("object.ue_export", icon = "EXPORT")

class UE_PT_Object_Properties(bpy.types.Panel):
    bl_label = "Object Properties"
    bl_category = "Unreal Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bpy.types.Object.ue_sub_folder_path = bpy.props.StringProperty(
        name="Sub Folder",
        maxlen=1024,
        default="",
        subtype='NONE'
        )

    bpy.types.Scene.ue_selected_meshes_expanded = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        activeObject = context.active_object
        selectedObjects = context.selected_objects

        objCount = len(selectedObjects)

        if objCount == 0:
            layout.row().label(text='Selection Empty')
            return

        subFolder = layout.row()
        subFolder.prop(activeObject, 'ue_sub_folder_path', icon="FILE_FOLDER")

        if objCount == 1:
            assetType = layout.row()
            assetType.prop(activeObject, 'name', text="", icon='OBJECT_DATA')
            return

        if objCount > 1:
            applySubFolder = layout.row()
            applySubFolder.operator("object.ue_apply_sub_folder", icon = "CHECKMARK")
            
            section_icon = "TRIA_DOWN" if scene.ue_selected_meshes_expanded else "TRIA_RIGHT"
            layout.row().prop(
                scene,
                'ue_selected_meshes_expanded',
                icon=section_icon,
                text=f'{objCount} Objects Selected',
                emboss=False
            )

            if scene.ue_selected_meshes_expanded:
                selectedObjectsBox = layout.box()
                for selectedObject in selectedObjects:
                    meshInfo = selectedObjectsBox.row()
                    meshInfo.label(text=selectedObject.name)
                    meshInfo.label(text=selectedObject.ue_sub_folder_path)

def register():
    bpy.utils.register_class(ue_export_sm.UE_OT_ExportStaticMesh)
    bpy.utils.register_class(ue_operators.UE_OT_ApplySubFolder)
    bpy.utils.register_class(UE_PT_Global_Properties)
    bpy.utils.register_class(UE_PT_Object_Properties)

def unregister():
    bpy.utils.unregister_class(UE_PT_Object_Properties)
    bpy.utils.unregister_class(UE_PT_Global_Properties)
    bpy.utils.unregister_class(ue_operators.UE_OT_ApplySubFolder)
    bpy.utils.unregister_class(ue_export_sm.UE_OT_ExportStaticMesh)