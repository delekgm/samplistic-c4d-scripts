"""
Samplistic Mograph to Nulls
Author: Delek Miller | Samplistic
Version: 1.0.0
Description: Create nulls dynamically from a MoObject

Written for Maxon Cinema 4D 2024.4.1
Python version 3.11.4

Fork of the script by www.lasselauch.com/lab/
Original Coffee-Script & Concept by Per Anders. (http://peranders.com/)
Change log:
1.0.0
"""

import c4d # type: ignore
# from c4d import utils as u # type: ignore
# from c4d import gui # type: ignore
from c4d.modules import mograph as mo # type: ignore


def CreateUserDataGroup(obj, name, columns=1, parentGroup=None):
    if obj is None: 
        return False
    group = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    group[c4d.DESC_NAME] = name
    group[c4d.DESC_SHORT_NAME] = name
    group[c4d.DESC_TITLEBAR] = 1
    group[c4d.DESC_COLUMNS] = columns
    group[c4d.DESC_DEFAULT] = 1  # Expand the group by default
    group[c4d.DESC_PARENTGROUP] = parentGroup
    return obj.AddUserData(group)  # Returns the group ID to use as parent


def CreateUserDataCheckbox(obj, name, val=1, parentGroup=None):
    if obj is None: 
        return False
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = val
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_ON
    bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_BOOL
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    element = obj.AddUserData(bc)
    if element:  # Ensure it was created successfully
        obj[element] = val
    return element


def CreateUserDataLink(obj, name, link=None, parentGroup=None, shortname=None):
    if obj is None:
        return False
    if shortname is None: 
        shortname = name
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BASELISTLINK) # init user data
    bc[c4d.DESC_NAME] = name # Set user data name
    bc[c4d.DESC_SHORT_NAME] = shortname # Set userdata short name
    bc[c4d.DESC_DEFAULT] = link # Set default value
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_ON
    bc[c4d.DESC_SHADERLINKFLAG] = True
    bc[c4d.DESC_PARENTGROUP] = parentGroup # Set parent group
    element = obj.AddUserData(bc)
    if element:
        obj[element] = link
    return element


def CreatePythonTag(obj, link_object=None):
    pyTag = c4d.BaseTag(1022749)
    pyTag.SetName("Mograph to Nulls")
    
    # # Get icon
    scriptPath = __file__
    iconPath = scriptPath.rsplit('.', 1)[0]+".tif"
    pyTag[c4d.ID_BASELIST_ICON_FILE] = iconPath
    
    # Insert tag to active object
    obj.InsertTag(pyTag)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, pyTag) # type: ignore
    
    # General Settings
    groupIDSettings = CreateUserDataGroup(pyTag, "Settings") # ID 1
    CreateUserDataLink(pyTag, "Mograph Data", link_object, groupIDSettings) # ID 2
    CreateUserDataCheckbox(pyTag, "Use Color", 1, groupIDSettings) # ID 3

    # Python tag code
    # ---------------------------------------------------------------------    
    pyTag[c4d.TPYTHON_CODE] = """
import c4d
if c4d.modules.CheckMoGraph():
    from c4d.modules import mograph as mo

def MographOrSelection(link):
    # Mograph, Matrix, Fracture, Voronoi Fracture
    molist = [1018544, 1018545, 1018791, 1036557]

    mograph = False
    selection = False

    if link.GetType() in molist:
        mograph = True

    if link.GetType() == 1021338:
        selection = True

    return mograph, selection

def checknulls(root, md, link, selection):
    if not md: return

    count = md.GetCount()
    if not root: return

    nl = root.GetDown()
    if not nl:
        nl = c4d.BaseObject(c4d.Onull)
        nl[c4d.ID_BASELIST_ICON_COLORIZE_MODE] = c4d.ID_BASELIST_ICON_COLORIZE_MODE_CUSTOM
        nl.InsertUnder(root)

    name = link.GetName()
    if selection:
        name = link.GetMain().GetName()

    nltemp = nl
    nlroot = nl

    for i in range(count):
        nlname = \"\"\"{name}_{i}\"\"\".format(**locals())
        nl.SetName(nlname)
        nltemp = nl

        if selection and c4d.GetC4DVersion() >= 18020:
            sel = mo.GeGetMoDataSelection(link.GetMain()).GetAll(count)
            if sel[i]:
                nlname = \"\"\"{name}_Selection_{i}\"\"\".format(**locals())
                nl.SetName(nlname)
                nl = nl.GetNext()
        else:
            nl = nl.GetNext()

        if not nl:
            nl = nltemp.GetClone(c4d.CL_NO_HIERARCHY)
            nl.InsertAfter(nltemp)

    if count == 0:
        nl = nl.GetNext()

    while nl:
        nl2 = nl
        nl = nl.GetNext()
        nl2.Remove()

def main():
    link = op[c4d.ID_USERDATA,2]
    if link is None:
        return

    mograph, selection = MographOrSelection(link)
    if mograph:
        md = mo.GeGetMoData(link)
    if selection:
        md = mo.GeGetMoData(link.GetMain())
    count = md.GetCount()

    if count == 0:
        return

    root = op.GetObject()

    if root is None:
        return

    if md is None:
        return

    marr = md.GetArray(c4d.MODATA_MATRIX)
    carr = md.GetArray(c4d.MODATA_COLOR)

    if selection and c4d.GetC4DVersion() >= 18020:
        ma, ca = list(), list()
        sel = mo.GeGetMoDataSelection(link.GetMain()).GetAll(count)
        for i in range(len(marr)):
            if sel[i]:
                ma.append(marr[i])
                ca.append(carr[i])
        marr, carr = ma, ca

    checknulls(root, md, link, selection)
    children = root.GetChildren()

    if not children:
        return

    for i in range(len(marr)):
        # SET MATRIX
        if mograph:
            root.SetMg(link.GetMg())
        if selection:
            root.SetMg(link.GetMain().GetMg())
        children[i].SetMl(marr[i])

        # SET COLOR
        children[i][c4d.ID_BASEOBJECT_USECOLOR] = 0
        children[i][c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1,1,1)
        if op[c4d.ID_USERDATA,3]:
            children[i][c4d.ID_BASEOBJECT_USECOLOR] = 1
            children[i][c4d.ID_BASEOBJECT_COLOR] = carr[i]
            children[i][c4d.ID_BASELIST_ICON_COLOR] = carr[i]
"""
    # Python tag code end
    # ---------------------------------------------------------------------
    return True

def make_null():
        new_null = c4d.BaseObject(c4d.Onull)
        new_null.SetName("Mograph to Nulls Null")

        doc.InsertObject(new_null) # type: ignore

        doc.SetActiveObject(new_null, c4d.SELECTION_NEW) # type: ignore
        return new_null

def check_mo_data(obj):
    md = mo.GeGetMoData(obj)
    if md is None:
        return False

    # Check the count of MoGraph elements
    count = md.GetCount()
    if count == 0:
        return False

    return True
    
def main():
    molist = [1018544, 1018545, 1018791, 1036557]
    
    doc.StartUndo() # type: ignore
    selection = doc.GetActiveObject() # type: ignore
    if not selection:
        selection = make_null()
        CreatePythonTag(selection)

    elif selection.GetType() in molist:
        link_object = selection
        if check_mo_data(link_object):
            selection = make_null()
            CreatePythonTag(selection, link_object)
        else:
            c4d.gui.MessageDialog("No MoGraph data found in the object. Please add MoGraph data to the object first.")
            
    else:
        CreatePythonTag(selection)
    doc.EndUndo() # type: ignore
    c4d.EventAdd()

if __name__ == '__main__':
    main()