import bpy

class UE_OT_ApplySubFolder(bpy.types.Operator):
    bl_idname = "object.ue_apply_sub_folder"
    bl_label = "Set Sub Folder For Selected Objects"

    def execute(self, context):
        activeObject = bpy.context.active_object
        selectedObjects = bpy.context.selected_objects

        print(f'Apply {activeObject.ue_sub_folder_path} to selected obejcts')

        for selectedObject in selectedObjects:
            selectedObject.ue_sub_folder_path = activeObject.ue_sub_folder_path

        return {'FINISHED'}