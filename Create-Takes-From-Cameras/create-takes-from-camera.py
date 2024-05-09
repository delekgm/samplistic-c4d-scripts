# 1057516 is type for RS camera
import c4d

def create_takes_for_cameras():
    # Access the active document
    doc = c4d.documents.GetActiveDocument()

    # Start an undo group
    doc.StartUndo()

    # Access the takes system
    take_data = doc.GetTakeData()
    if not take_data:
        return

    # Get the main (base) take
    base_take = take_data.GetMainTake()
    
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    # doc.GetObjects() gets all objects in the doc
    # Iterate through all objects in the document
    for obj in selected_objects:
        # Check if the object is a Redshift camera
        if obj.GetType() == 1057516:  # Redshift Camera
            # Create a new take for each Redshift camera
            take_name = obj.GetName()
            new_take = take_data.AddTake(name=take_name, parent=base_take, cloneFrom=None)
            take_data.SetCurrentTake(new_take)
            
            new_take.SetCamera(take_data, obj)

            # Update the active render settings to use the new camera
            render_data = doc.GetActiveRenderData()

            # Register an undo for adding the take
            doc.AddUndo(c4d.UNDOTYPE_NEW, new_take)

    # End the undo group
    doc.EndUndo()

    # Update the document
    c4d.EventAdd()

if __name__=="__main__":
    create_takes_for_cameras()
