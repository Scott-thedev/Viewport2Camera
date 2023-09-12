bl_info = {
    "name": "Viewport2Camera",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import mathutils

class VIEW3D_PT_ViewportCamera(bpy.types.Panel):
    bl_label = "Viewport2Camera"
    bl_idname = "VIEW3D_PT_Viewport2Camera"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        
        # Get the active camera
        active_camera = context.scene.camera
        
        # List all cameras with options to rename and enable/disable
        cameras = [obj for obj in bpy.context.scene.objects if obj.type == 'CAMERA']
        for camera in cameras:
            row = layout.row()
            if camera == active_camera:
                row.label(text=camera.name, icon='RADIOBUT_ON')
            else:
                row.label(text=camera.name)
            row.prop(camera, "name", text="")
            row.prop(camera, "hide_viewport", text="Enable")

        layout.separator()
        
        # Buttons to create viewport camera and set the latest camera active
        layout.operator("object.create_viewport_camera", text="Create Viewport Camera")
        layout.operator("object.set_latest_camera_active", text="Set Latest Camera Active")

class OBJECT_OT_CreateViewportCamera(bpy.types.Operator):
    bl_idname = "object.create_viewport_camera"
    bl_label = "Create Viewport Camera"
    
    def execute(self, context):
        # Get the current 3D view matrix
        view_matrix = context.space_data.region_3d.view_matrix.inverted()
        location = view_matrix.translation
        rotation = view_matrix.to_euler()
        
        # Clear the "is_latest_camera" property for all cameras in the scene
        for obj in bpy.context.scene.objects:
            if obj.type == 'CAMERA':
                obj["is_latest_camera"] = False
        
        # Create a new camera
        bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=location)
        new_camera = context.object
        
        # Set the camera's rotation to match the viewport
        new_camera.rotation_euler = rotation
        
        # Set the "is_latest_camera" property to true for the new camera
        new_camera["is_latest_camera"] = True
        
        return {'FINISHED'}

class OBJECT_OT_SetLatestCameraActive(bpy.types.Operator):
    bl_idname = "object.set_latest_camera_active"
    bl_label = "Set Latest Camera Active"
    
    def execute(self, context):
        # Set the most recently created camera with the custom property as the active camera
        for obj in bpy.context.scene.objects:
            if obj.type == 'CAMERA' and obj.get("is_latest_camera"):
                bpy.context.scene.camera = obj
                break
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(VIEW3D_PT_ViewportCamera)
    bpy.utils.register_class(OBJECT_OT_CreateViewportCamera)
    bpy.utils.register_class(OBJECT_OT_SetLatestCameraActive)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_ViewportCamera)
    bpy.utils.unregister_class(OBJECT_OT_CreateViewportCamera)
    bpy.utils.unregister_class(OBJECT_OT_SetLatestCameraActive)

if __name__ == "__main__":
    register()