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
            row = layout.row(align=True)
            if camera == active_camera:
                row.label(text=camera.name, icon='RADIOBUT_ON')
            else:
                row.label(text=camera.name)
            row.prop(camera, "name", text="", emboss=False, icon='CAMERA_DATA')
            row.prop(camera, "hide_viewport", text="Enable")
            
            # Button to set this camera as the active camera
            row.operator("object.set_active_camera", text="Set Active").camera_name = camera.name

        layout.separator()
        
        # Camera Type Selector
        layout.prop(context.scene, "viewport2camera_camera_type", expand=True)

        layout.operator("object.create_viewport_camera")

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Active Camera: " + context.scene.camera.name)

class OBJECT_OT_CreateViewportCamera(bpy.types.Operator):
    bl_idname = "object.create_viewport_camera"
    bl_label = "Create Viewport Camera"
    
    camera_type: bpy.props.EnumProperty(
        name="Camera Type",
        items=[
            ("PERSPECTIVE", "Perspective", "Perspective Camera"),
            ("ORTHOGRAPHIC", "Orthographic", "Orthographic Camera"),
            ("PANORAMIC", "Panoramic", "Panoramic Camera"),
        ],
        default="PERSPECTIVE"
    )
    
    focal_length: bpy.props.FloatProperty(
        name="Focal Length",
        default=50.0,
        min=1.0,
        unit='NONE',  # Use 'NONE' as unit subtype
    )
    
    sensor_width: bpy.props.FloatProperty(
        name="Sensor Width",
        default=36.0,
        min=1.0,
        unit='LENGTH',
    )
    
    use_dof: bpy.props.BoolProperty(
        name="Use Depth of Field",
        default=False
    )
    
    def execute(self, context):
        try:
            # Get the current 3D view matrix
            view_matrix = context.space_data.region_3d.view_matrix.inverted()
            location = view_matrix.translation
            rotation = view_matrix.to_euler()
            
            # Check if we are in edit mode, and switch to object mode if necessary
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Create a new camera based on the selected camera type
            camera_type = context.scene.viewport2camera_camera_type
            if camera_type == "PERSPECTIVE":
                bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=location)
                new_camera = context.object
            elif camera_type == "ORTHOGRAPHIC":
                bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=location)
                new_camera = context.object
                new_camera.data.type = 'ORTHO'
            elif camera_type == "PANORAMIC":
                bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=location)
                new_camera = context.object
                new_camera.data.type = 'PANO'
            
            # Set camera properties
            new_camera.data.lens = self.focal_length
            new_camera.data.sensor_width = self.sensor_width
            
            if self.use_dof:
                # Enable Depth of Field
                new_camera.data.dof.use_dof = True
                # You can set additional depth of field settings here if needed
            
            # Set the camera's rotation to match the viewport
            new_camera.rotation_euler = rotation
            
            # Switch back to edit mode if we were not in object mode initially
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='EDIT')
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create camera: {str(e)}")
            return {'CANCELLED'}

class OBJECT_OT_SetActiveCamera(bpy.types.Operator):
    bl_idname = "object.set_active_camera"
    bl_label = "Set Active Camera"
    
    camera_name: bpy.props.StringProperty()
    
    def execute(self, context):
        # Set the selected camera as the active camera
        camera = bpy.context.scene.objects.get(self.camera_name)
        if camera and camera.type == 'CAMERA':
            bpy.context.scene.camera = camera
        
        return {'FINISHED'}

# Function to update the panel header when the active camera changes
def update_panel_header(scene):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

def register():
    bpy.types.Scene.viewport2camera_camera_type = bpy.props.EnumProperty(
        name="Camera Type",
        items=[
            ("PERSPECTIVE", "Perspective", "Perspective Camera"),
            ("ORTHOGRAPHIC", "Orthographic", "Orthographic Camera"),
            ("PANORAMIC", "Panoramic", "Panoramic Camera"),
        ],
        default="PERSPECTIVE"
    )
    
    bpy.utils.register_class(VIEW3D_PT_ViewportCamera)
    bpy.utils.register_class(OBJECT_OT_CreateViewportCamera)
    bpy.utils.register_class(OBJECT_OT_SetActiveCamera)
    bpy.app.handlers.depsgraph_update_post.append(update_panel_header)

def unregister():
    del bpy.types.Scene.viewport2camera_camera_type
    
    bpy.utils.unregister_class(VIEW3D_PT_ViewportCamera)
    bpy.utils.unregister_class(OBJECT_OT_CreateViewportCamera)
    bpy.utils.unregister_class(OBJECT_OT_SetActiveCamera)
    bpy.app.handlers.depsgraph_update_post.remove(update_panel_header)

if __name__ == "__main__":
    register()
# END SCRIPT
