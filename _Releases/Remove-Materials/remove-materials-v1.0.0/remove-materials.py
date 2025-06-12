import c4d # type: ignore

def RemoveMaterialsFromObject(obj):
    # Loop through each tag in the object
    tag = obj.GetFirstTag()
    while tag:
        next_tag = tag.GetNext()  # Cache the next tag before removing
        # If the tag is a material tag, remove it
        if isinstance(tag, c4d.TextureTag):
            doc.AddUndo(c4d.UNDOTYPE_DELETE, tag)
            tag.Remove()
        tag = next_tag

    # Recursively remove materials from child objects
    child = obj.GetDown()
    while child:
        RemoveMaterialsFromObject(child)
        child = child.GetNext()

def main():
    # Get the currently active object
    obj = doc.GetActiveObject()

    if obj is None:
        print("No active object selected.")
        return

    # Start an undo action
    doc.StartUndo()

    # Remove materials from the active object and all its children
    RemoveMaterialsFromObject(obj)

    # End the undo action
    doc.EndUndo()

    # Update the scene
    c4d.EventAdd()

# Execute the script
if __name__ == '__main__':
    main()
