import c4d

def remove_unused_tags(obj):
    if not obj or not obj.CheckType(c4d.Opolygon):  # Ensure object is a polygon object
        return
    
    doc = c4d.documents.GetActiveDocument()
    polygon_count = obj.GetPolygonCount()
    point_count = obj.GetPointCount()

    # Handle texture tags and material usage
    texture_tags = [tag for tag in obj.GetTags() if isinstance(tag, c4d.TextureTag)]
    selection_tags = [tag for tag in obj.GetTags() if isinstance(tag, c4d.SelectionTag)]
    used_materials = set()

    for ttag in texture_tags:
        selection = ttag[c4d.TEXTURETAG_RESTRICTION]
        if selection:
            sel_tag = next((tag for tag in selection_tags if tag.GetName() == selection), None)
            if sel_tag:
                bs = sel_tag.GetBaseSelect()
                if any(bs.IsSelected(i) for i in range(max(point_count, polygon_count))):
                    used_materials.add(ttag.GetMaterial())
            continue
        used_materials.add(ttag.GetMaterial())

    for ttag in texture_tags:
        if ttag.GetMaterial() not in used_materials:
            doc.AddUndo(c4d.UNDOTYPE_DELETE, ttag)
            ttag.Remove()

    # Handle selection tags
    for sel_tag in selection_tags:
        bs = sel_tag.GetBaseSelect()
        if not any(bs.IsSelected(i) for i in range(max(point_count, polygon_count))):
            doc.AddUndo(c4d.UNDOTYPE_DELETE, sel_tag)
            sel_tag.Remove()

    c4d.EventAdd()

def main():
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        print("No active document.")
        return
    
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)
    
    if not selected_objects:
        print("No objects selected.")
        return

    doc.StartUndo()
    for obj in selected_objects:
        if obj.CheckType(c4d.Opolygon):
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, obj)
            remove_unused_tags(obj)
    doc.EndUndo()
    c4d.EventAdd()
    print("Unused material and selection tags removed from selected objects.")

if __name__=="__main__":
    main()
