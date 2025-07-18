"""
Samplistic Simple Moves
Author: Delek Miller | Samplistic
Original Concept: Michael Rosen | Samplistic
Version: 1.0.5
Description: Interpolate PSR between objects in space

Written for Maxon Cinema 4D 2025.7.3
Python version 3.11.4
"""


import c4d # type: ignore


def CreateUserDataGroup(obj, name, columns=1, parentGroup=None):
    if obj is None: return False
    group = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    group[c4d.DESC_NAME] = name
    group[c4d.DESC_SHORT_NAME] = name
    group[c4d.DESC_TITLEBAR] = 1
    group[c4d.DESC_COLUMNS] = columns
    group[c4d.DESC_DEFAULT] = 1  # Expand the group by default
    group[c4d.DESC_PARENTGROUP] = parentGroup
    return obj.AddUserData(group)  # Returns the group ID to use as parent


def CreateUserDataCheckbox(obj, name, val=0, parentGroup=None):
    if obj is None: return False
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = val
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_ON
    # bc[c4d.DESC_UNIT] = unit
    bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_BOOL
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    element = obj.AddUserData(bc)
    if element:  # Ensure it was created successfully
        obj[element] = val
    return element


def CreateObjectList(obj, name, parentGroup=None):
    if obj is None: return False
    bc = c4d.GetCustomDatatypeDefault(c4d.CUSTOMDATATYPE_INEXCLUDE_LIST)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    element = obj.AddUserData(bc)
    if element:
        obj[element] = c4d.InExcludeData()
    return element


def CreateUserDataCycle(obj, name, val, parentGroup=None, unit=c4d.DESC_UNIT_LONG):
    if obj is None: return False
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_OFF
    # bc[c4d.DESC_UNIT] = unit
    bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_CYCLE
    bc[c4d.DESC_DEFAULT] = "Simple Moves"
    cycleBC = c4d.BaseContainer()
    items = val.split(',')
    for i, item in enumerate(items):
        cycleBC.SetString(i, item)
    bc[c4d.DESC_CYCLE] = cycleBC
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    element = obj.AddUserData(bc)
    return element


def CreateUserDataPercentSlider(obj, name, val=0, min=0, max=1, parentGroup=None, unit=c4d.DESC_UNIT_PERCENT):
    if obj is None: return False
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = val
    bc[c4d.DESC_ANIMATE] = c4d.DESC_ANIMATE_ON
    bc[c4d.DESC_UNIT] = unit
    bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_REALSLIDER
    bc[c4d.DESC_MIN] = min
    bc[c4d.DESC_MAX] = max
    bc[c4d.DESC_MINSLIDER] = 0
    bc[c4d.DESC_MAXSLIDER] = 10
    bc[c4d.DESC_STEP] = 0.01
    if parentGroup is not None:
        bc[c4d.DESC_PARENTGROUP] = parentGroup
    element = obj.AddUserData(bc)
    obj[element] = val
    return element

def getIconPath():
    scriptPath = __file__
    iconPath = scriptPath.rsplit('.', 1)[0] + ".tif"
    return iconPath

def CreatePythonTag(obj):
    pyTag = c4d.BaseTag(1022749)
    pyTag.SetName("Simple Moves")
    
    # Get icon
    pyTag[c4d.ID_BASELIST_ICON_FILE] = getIconPath()
    
    obj.InsertTag(pyTag)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, pyTag) # type: ignore
    
    # General Settings
    groupIDSettings = CreateUserDataGroup(pyTag, "Settings")
    CreateUserDataCycle(pyTag, "Mode", "Simple Moves, Total", groupIDSettings)
    CreateUserDataPercentSlider(pyTag, "Simple Moves", 0, 0, 2147483647, groupIDSettings)
    CreateUserDataPercentSlider(pyTag, "Total", 0, 0, 1, groupIDSettings)
    CreateObjectList(pyTag, "Targets", groupIDSettings)
    
    # Transform Settings
    groupIDMatrix = CreateUserDataGroup(obj=pyTag, name="Matrix", columns=3, parentGroup=groupIDSettings)
    CreateUserDataCheckbox(pyTag, "Position", 1, groupIDMatrix)
    CreateUserDataCheckbox(pyTag, "Scale", 0, groupIDMatrix)
    CreateUserDataCheckbox(pyTag, "Rotation", 1, groupIDMatrix)
    CreateUserDataCheckbox(pyTag, "Use Shortest Path Rotation", 0, groupIDMatrix)
    
    # Softness Settings
    CreateUserDataCycle(pyTag, "Interpolation", "Linear, Soft", groupIDSettings)
    CreateUserDataPercentSlider(pyTag, "Softness", 0.5, 0, 1, groupIDSettings)
    

    # Python tag code
    # ---------------------------------------------------------------------
    pyTag[c4d.TPYTHON_CODE] = (
        "import c4d\n"
        "from c4d import utils as u\n"
        "import math\n"
        "import logging\n"
        "from logging import traceback\n"
        "\n"
        "\n"
        "# Functions\n"
        "def setMoveMode():\n"
        "    udc = op.GetUserDataContainer()\n"
        "    for descId, bc in udc:\n"
        "        if descId[1].id == 3:\n"
        "            if op[c4d.ID_USERDATA,2] == 0:\n"
        "                bc[c4d.DESC_HIDE] = False\n"
        "                op.SetUserDataContainer(descId, bc)\n"
        "            else:\n"
        "                bc[c4d.DESC_HIDE] = True\n"
        "                op.SetUserDataContainer(descId, bc)\n"
        "        if descId[1].id == 4:\n"
        "            if op[c4d.ID_USERDATA,2] == 1:\n"
        "                bc[c4d.DESC_HIDE] = False\n"
        "                op.SetUserDataContainer(descId, bc)\n"
        "            else:\n"
        "                bc[c4d.DESC_HIDE] = True\n"
        "                op.SetUserDataContainer(descId, bc)\n"
        "        if descId[1].id == 12:\n"
        "           if op[c4d.ID_USERDATA, 11] == 1:\n"
        "               bc[c4d.DESC_HIDE] = False\n"
        "           else:\n"
        "               bc[c4d.DESC_HIDE] = True\n"
        "           op.SetUserDataContainer(descId, bc)\n"
        "\n"
        "\n"
        "def SetGlobalPosition(obj, mat1, mat2, factor):\n"
        "    p1 = mat1.off # Get 1's position\n"
        "    p2 = mat2.off # Get 2's position\n"
        "\n"
        "    off = u.MixVec(p1, p2, factor) # Mix position\n"
        "\n"
        "    m = obj.GetMg() # Get global matrix\n"
        "    m.off = off # Set offset vector\n"
        "    obj.SetMg(m) # Set matrix\n"
        "\n"
        "\n"
        "def SetGlobalScale(obj, mat1, mat2, factor):\n"
        "    s1 = c4d.Vector(mat1.v1.GetLength(),mat1.v2.GetLength(),mat1.v3.GetLength())\n"
        "    s2 = c4d.Vector(mat2.v1.GetLength(),mat2.v2.GetLength(),mat2.v3.GetLength())\n"
        "    \n"
        "    scale = u.MixVec(s1, s2, factor) # Mix scale\n"
            "\n"
        "    m = obj.GetMg() # Get matrix\n"
        "    m.v1 = m.v1.GetNormalized() * scale.x # Set scale\n"
        "    m.v2 = m.v2.GetNormalized() * scale.y\n"
        "    m.v3 = m.v3.GetNormalized() * scale.z\n"
        "    obj.SetMg(m) # Set matrix\n"
        "\n"
        "\n"
        "def SetGlobalRotation(obj, mat1, mat2, factor):\n"
        "    r1 = u.MatrixToHPB(mat1) # Get A's rotation\n"
        "    r2 = u.MatrixToHPB(mat2) # Get B's rotation\n"
        "    oa = u.GetOptimalAngle(r1, r2, c4d.ROTATIONORDER_DEFAULT) # Get optimal angle\n"
            "\n"
        "    rot = u.MixVec(r1, oa, factor) # Mix rotation\n"
            "\n"
        "    m = obj.GetMg() # Get global matrix\n"
        "    pos = m.off # Get offset vector\n"
        "    scale = c4d.Vector( m.v1.GetLength(), m.v2.GetLength(), m.v3.GetLength()) # Get scale\n"
        "    m = u.HPBToMatrix(rot) # Set rotation\n"
        "    m.off = pos # Set offset vector\n"
        "    m.v1 = m.v1.GetNormalized() * scale.x # Set scale\n"
        "    m.v2 = m.v2.GetNormalized() * scale.y\n"
        "    m.v3 = m.v3.GetNormalized() * scale.z\n"
        "    obj.SetMg(m) # Set matrix\n"
        "\n"
        "\n"
        "def lerp(start, end, t):\n"
        "    return (1 - t) * start + t * end # Custom lerp function\n"
        "\n"
        "\n"
        "def SetBasicRotation(target, obj1, obj2, factor):\n"
        "    rot1 = obj1.GetRelRot() # Get rotation of current interpolation object\n"
        "    rot2 = obj2.GetRelRot( )# Get rotation of next interpolation object\n"
            "\n"
        "    mixH = lerp(rot1[0], rot2[0], factor) # Get y-axis rotation\n"
        "    mixP = lerp(rot1[1], rot2[1], factor) # Get x-axis rotation\n"
        "    mixB = lerp(rot1[2], rot2[2], factor) # Get z-axis rotation\n"
            "\n"
        "    target.SetRelRot(c4d.Vector(mixH, mixP, mixB)) # Set rotation on target object\n"
        "\n"
        "\n"
        "def clean_inexclude_userdata(op, userdata_id):\n"
        "    data = op[userdata_id]\n"
        "    if not isinstance(data, c4d.InExcludeData):\n"
        "        raise TypeError('User data at ID {} is not an InExcludeData'.format(userdata_id))\n"
        "\n"
        "    valid_objects = []\n"
        "    for i in range(data.GetObjectCount()):\n"
        "        obj = data.ObjectFromIndex(doc, i)\n"
        "        if obj is not None:\n"
        "            flags = data.GetFlags(i)\n"
        "            valid_objects.append(obj)\n"
        "\n"
        "    missing = []\n"
        "    for i in range(data.GetObjectCount()):\n"
        "        if data.ObjectFromIndex(doc, i) is None:\n"
        "            missing.append(i)\n"
        "    if not missing:\n"
        "        return valid_objects\n"
        "    for i in reversed(missing):\n"
        "        data.DeleteObject(i)\n"
        "\n"
        "    return valid_objects\n"
        "\n"
        "\n"
        "def catmull_pos(p0, p1, p2, p3, t, tension):\n"
        "    t2, t3 = t*t, t*t*t\n"
        "    m1 = (1.0 - tension) * (p2 - p0) * 0.5\n"
        "    m2 = (1.0 - tension) * (p3 - p1) * 0.5\n"
        "    h1 = 2*t3 - 3*t2 + 1\n"
        "    h2 = -2*t3 + 3*t2\n"
        "    h3 = t3 - 2*t2 + t\n"
        "    h4 = t3 - t2\n"
        "    return p1 * h1 + p2 * h2 + m1 * h3 + m2 * h4\n"
        "\n"
        "\n"
        "def main():\n"
        "    try:\n"
        "        # Read in user data\n"
        "        mode = op[c4d.ID_USERDATA,2] # User Data: Mode\n"
        "        mixA = op[c4d.ID_USERDATA,3] # User Data: Mix(SimpleMoves)\n"
        "        mixB = op[c4d.ID_USERDATA,4] # User Data: Mix(Total)\n"
        "        pos = op[c4d.ID_USERDATA,7] # User Data: Position\n"
        "        scl = op[c4d.ID_USERDATA,8] # User Data: Scale\n"
        "        rot = op[c4d.ID_USERDATA,9] # User Data: Rotation\n"
        "        rotMode = op[c4d.ID_USERDATA, 10] # User Data: Rotation Mode\n"
        "        user_data_id = c4d.ID_USERDATA, 5\n"
        "        objects = clean_inexclude_userdata(op, user_data_id) # User Data: Target list\n"
        "        interp = op[c4d.ID_USERDATA, 11] # linear or soft\n"
        "        soft = 1.0 - op[c4d.ID_USERDATA, 12]# Softness 0-1\n"
        "\n"
        "        # Set mode to Simple Moves or Total\n"
        "        setMoveMode()\n"
        "        # Driver code\n"
        "        obj = op.GetObject() # Get object\n"
        "        array = objects # Initialize a list for targets\n"
        "        cnt = len(array) # Get targets count\n"
        "        if cnt > 0:\n"
        "            if mode == 0: # If 'Mode' is 'SimpleMoves'\n"
        "               data = mixA\n"
        "            else: # If Mode is Total\n"
        "               data = u.RangeMap(mixB, 0, 1, 0, cnt-1, True)\n"
        "            i = int(math.floor(data)) # Calculate current target id\n"
        "            if i < cnt-1: # If target id is less than targets count\n"
        "                mat_a = array[i].GetMg() # Get A target's global matrix\n"
        "                mat_b = array[i+1].GetMg() # Get B target's global matrix\n"
        "\n"
        "                obj1_ = array[i] # Get object for basic rotation\n"
        "                obj2_ = array[i + 1]\n"
        "            else: # Otherwise\n"
        "                mat_a = array[-1].GetMg() # A target is the last target, get global matrix\n"
        "                mat_b = array[-1].GetMg() # B target is the last target, get global matrix\n"
        "\n"
        "                obj1_ = array[-1] # Get object for basic rotation\n"
        "                obj2_ = array[-1]\n"
        "            mix = data % 1 # Calculate mix value\n"
        "\n"
        "            if pos == True:\n"
        "                if interp == 0:\n"
        "                   SetGlobalPosition(obj, mat_a, mat_b, mix) # Set position\n"
        "                else:\n"
        "                    i_soft = min(i, cnt-1)\n"
        "                    t_soft = mix if i < cnt-1 else 0.0\n"
        "                    p0 = array[max(i_soft-1, 0  )].GetMg().off\n"
        "                    p1 = array[i_soft            ].GetMg().off\n"
        "                    p2 = array[min(i_soft+1,cnt-1)].GetMg().off\n"
        "                    p3 = array[min(i_soft+2,cnt-1)].GetMg().off\n"
        "\n"
        "                    pos_v = catmull_pos(p0, p1, p2, p3, t_soft, soft)\n"
        "\n"
        "                    m = obj.GetMg()\n"
        "                    m.off = pos_v\n"
        "                    obj.SetMg(m)\n"
        "\n"
        "                    # update soft interpolation for scale and rotation\n"
        "                    mix = t_soft\n"
        "                    mat_a = array[i_soft].GetMg()\n"
        "                    mat_b = array[min(i_soft+1, cnt-1)].GetMg()\n"
        "                    obj1_ = array[i_soft]\n"
        "                    obj2_ = array[min(i_soft+1, cnt-1)]\n"
        "            if scl == True:\n"
        "                SetGlobalScale(obj, mat_a, mat_b, mix) # Set scale\n"
        "            if rot == True:\n"
        "                if rotMode == True:\n"
        "                    SetGlobalRotation(obj, mat_a, mat_b, mix) # Set rotation\n"
        "                else:\n"
        "                    SetBasicRotation(obj, obj1_, obj2_, mix)\n"
        "    except Exception:\n"
        "        logging.error(traceback.format_exc())\n"
        "\n"
    )
    # Python tag code end
    # ---------------------------------------------------------------------
    pyTag[c4d.ID_USERDATA,2] == 0
    return True


def main():
    doc.StartUndo()
    selection = doc.GetActiveObject()
    if not selection:
        new_null = c4d.BaseObject(c4d.Onull)
        new_null.SetName("Simple Moves Null")
        new_null[c4d.ID_BASELIST_ICON_FILE] = getIconPath()

        doc.InsertObject(new_null)

        doc.SetActiveObject(new_null, c4d.SELECTION_NEW)
        # print("No active object, please select an object first")
        
        selection = new_null
        # doc.EndUndo()
        # return
    CreatePythonTag(selection)
    doc.EndUndo()
    c4d.EventAdd()

# Execute script
if __name__ == '__main__':
    main()
