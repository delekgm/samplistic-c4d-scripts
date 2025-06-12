import c4d # type: ignore

def move_axis_to_center(obj):
    """ Move the axis of the object to the geometric center of its points. """
    if not obj:
        return

    points = obj.GetAllPoints()
    if not points:
        return
    
    # Calculate the center of all points
    center = sum((c4d.Vector(p) for p in points), c4d.Vector(0, 0, 0)) / len(points)
    
    # Move all points so the object's axis is at the calculated center
    matrix = c4d.Matrix()
    matrix.off = center
    obj.SetMg(matrix)
    for i, point in enumerate(points):
        obj.SetPoint(i, point - center)
    
    obj.Message(c4d.MSG_UPDATE)

def split_object_by_selection_tags(object, doc):
    if not object:
        print("No valid object provided.")
        return []
    if not object.GetTags():
        print("No tags on the provided object.")
        return []

    selection_tags = [tag for tag in object.GetTags() if isinstance(tag, c4d.SelectionTag)]
    if not selection_tags:
        print("No selection tags found on the object.")
        return []

    new_objects = []
    for tag in selection_tags:
        # Clone the original object
        new_object = object.GetClone()
        new_object.SetName(f"{object.GetName()}_{tag.GetName()}")

        # Clear any existing polygon selections on the clone
        poly_selection = new_object.GetPolygonS()
        poly_selection.DeselectAll()

        # Set the selection from the tag onto the clone
        selection = tag.GetBaseSelect()
        for i in range(object.GetPolygonCount()):
            if selection.IsSelected(i):
                poly_selection.Select(i)

        # Insert the cloned object into the document for operations
        doc.InsertObject(new_object)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, new_object)
        c4d.EventAdd()

        # Perform the split operation
        c4d.utils.SendModelingCommand(
            command=c4d.MCOMMAND_SPLIT,
            list=[new_object],
            mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
            bc=c4d.BaseContainer(),
            doc=doc,
            flags=c4d.MODELINGCOMMANDFLAGS_CREATEUNDO
        )

        # The SPLIT command should create a new object in the document; find it
        split_object = new_object.GetNext()
        if split_object:
            move_axis_to_center(split_object)  # Adjust the axis of the new object
            new_objects.append(split_object)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, split_object)

        # Remove the temporary object
        new_object.Remove()
        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, new_object)
        c4d.EventAdd()

    return new_objects

def main():
    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()

    active_object = doc.GetActiveObject()
    if not active_object:
        print("No active object selected.")
        return

    new_objects = split_object_by_selection_tags(active_object, doc)

    doc.EndUndo()
    c4d.EventAdd()

if __name__ == '__main__':
    main()