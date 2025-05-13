import c4d
from c4d import utils as u
import math
import logging
from logging import traceback

# Functions
def setMoveMode():
    udc = op.GetUserDataContainer()
    for descId, bc in udc:
        if descId[1].id == 3:
            if op[c4d.ID_USERDATA,2] == 0:
                bc[c4d.DESC_HIDE] = False
                op.SetUserDataContainer(descId, bc)
            else:
                bc[c4d.DESC_HIDE] = True
                op.SetUserDataContainer(descId, bc)
        if descId[1].id == 4:
            if op[c4d.ID_USERDATA,2] == 1:
                bc[c4d.DESC_HIDE] = False
                op.SetUserDataContainer(descId, bc)
            else:
                bc[c4d.DESC_HIDE] = True
                op.SetUserDataContainer(descId, bc)

def SetGlobalPosition(obj, mat1, mat2, factor):
    p1 = mat1.off # Get 1's position
    p2 = mat2.off # Get 2's position

    off = u.MixVec(p1, p2, factor) # Mix position

    m = obj.GetMg() # Get global matrix
    m.off = off # Set offset vector
    obj.SetMg(m) # Set matrix

def SetGlobalScale(obj, mat1, mat2, factor):
    s1 = c4d.Vector(mat1.v1.GetLength(),mat1.v2.GetLength(),mat1.v3.GetLength())
    s2 = c4d.Vector(mat2.v1.GetLength(),mat2.v2.GetLength(),mat2.v3.GetLength())

    scale = u.MixVec(s1, s2, factor) # Mix scale

    m = obj.GetMg() # Get matrix
    m.v1 = m.v1.GetNormalized() * scale.x # Set scale
    m.v2 = m.v2.GetNormalized() * scale.y
    m.v3 = m.v3.GetNormalized() * scale.z
    obj.SetMg(m) # Set matrix

def SetGlobalRotation(obj, mat1, mat2, factor):
    r1 = u.MatrixToHPB(mat1) # Get A's rotation
    r2 = u.MatrixToHPB(mat2) # Get B's rotation
    oa = u.GetOptimalAngle(r1, r2, c4d.ROTATIONORDER_DEFAULT) # Get optimal angle

    rot = u.MixVec(r1, oa, factor) # Mix rotation

    m = obj.GetMg() # Get global matrix
    pos = m.off # Get offset vector
    scale = c4d.Vector( m.v1.GetLength(), m.v2.GetLength(), m.v3.GetLength()) # Get scale
    m = u.HPBToMatrix(rot) # Set rotation
    m.off = pos # Set offset vector
    m.v1 = m.v1.GetNormalized() * scale.x # Set scale
    m.v2 = m.v2.GetNormalized() * scale.y
    m.v3 = m.v3.GetNormalized() * scale.z
    obj.SetMg(m) # Set matrix

def lerp(start, end, t):
    return (1 - t) * start + t * end # Custom lerp function

def SetBasicRotation(target, obj1, obj2, factor):
    rot1 = obj1.GetRelRot() # Get rotation of current interpolation object
    rot2 = obj2.GetRelRot( )# Get rotation of next interpolation object

    mixH = lerp(rot1[0], rot2[0], factor) # Get y-axis rotation
    mixP = lerp(rot1[1], rot2[1], factor) # Get x-axis rotation
    mixB = lerp(rot1[2], rot2[2], factor) # Get z-axis rotation

    target.SetRelRot(c4d.Vector(mixH, mixP, mixB)) # Set rotation on target object

def clean_inexclude_userdata(op, userdata_id):
    """
    Cleans an InExcludeData user data field by removing deleted (None) objects.

    Parameters:
        op (c4d.BaseTag or BaseObject): The object with the User Data.
        userdata_id (int): The ID of the User Data field (the InExcludeData field).

    Returns:
        list: A list of valid (non-None) objects from the cleaned InExcludeData.
    """
    doc = c4d.documents.GetActiveDocument()
    excl_data = op[userdata_id]

    if not isinstance(excl_data, c4d.InExcludeData):
        raise TypeError("User data at ID {} is not an InExcludeData".format(userdata_id))

    clean_data = c4d.InExcludeData()
    valid_objects = []

    for i in range(excl_data.GetObjectCount()):
        obj = excl_data.ObjectFromIndex(doc, i)
        if obj is not None:
            flags = excl_data.GetFlags(i)
            clean_data.InsertObject(obj, flags)
            valid_objects.append(obj)

    if clean_data.GetObjectCount() != excl_data.GetObjectCount():
        op[userdata_id] = clean_data
        c4d.EventAdd()  # Update the UI and scene

    return valid_objects


def main():
    try:
        # Read in user data
        mode = op[c4d.ID_USERDATA,2] # User Data: Mode
        mixA = op[c4d.ID_USERDATA,3] # User Data: Mix(SimpleMoves)
        mixB = op[c4d.ID_USERDATA,4] # User Data: Mix(Total)
        pos = op[c4d.ID_USERDATA,7] # User Data: Position
        scl = op[c4d.ID_USERDATA,8] # User Data: Scale
        rot = op[c4d.ID_USERDATA,9] # User Data: Rotation
        rotMode = op[c4d.ID_USERDATA, 10] # User Data: Rotation Mode
        user_data_id = c4d.ID_USERDATA, 5
        objects = clean_inexclude_userdata(op, user_data_id) # User Data: Target list

        # Set mode to Simple Moves or Total
        setMoveMode()
        # Driver code
        obj = op.GetObject() # Get object
        array = objects # Initialize a list for targets
        cnt = len(array) # Get targets count

        if cnt > 0:
            if mode == 0: # If 'Mode' is 'SimpleMoves'
                data = mixA
            else: # If Mode is Total
                data = u.RangeMap(mixB, 0, 1, 0, cnt-1, True)
            i = int(math.floor(data)) # Calculate current target id
            if i < cnt-1: # If target id is less than targets count
                mat_a = array[i].GetMg() # Get A target's global matrix
                mat_b = array[i+1].GetMg() # Get B target's global matrix

                obj1_ = array[i] # Get object for basic rotation
                obj2_ = array[i + 1]
            else: # Otherwise
                mat_a = array[-1].GetMg() # A target is the last target, get global matrix
                mat_b = array[-1].GetMg() # B target is the last target, get global matrix

                obj1_ = array[-1] # Get object for basic rotation
                obj2_ = array[-1]
            mix = data % 1 # Calculate mix value

            if pos == True:
                SetGlobalPosition(obj, mat_a, mat_b, mix) # Set position
            if scl == True:
                SetGlobalScale(obj, mat_a, mat_b, mix) # Set scale
            if rot == True:
                if rotMode == True:
                    SetGlobalRotation(obj, mat_a, mat_b, mix) # Set rotation
                else:
                    SetBasicRotation(obj, obj1_, obj2_, mix)
    except Exception:
        logging.error(traceback.format_exc())