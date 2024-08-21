# Libraries
import c4d
import math
from c4d import utils as u
import logging
from logging import traceback

# Functions
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
    scale = c4d.Vector( m.v1.GetLength(), # Get scale
                        m.v2.GetLength(),
                        m.v3.GetLength())
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

def main():
    try: # Try to execute following sctipt
        op.SetName("Simple Moves")
        mode = op[c4d.ID_USERDATA,8] # User Data: Mode
        mixA = op[c4d.ID_USERDATA,1] # User Data: Mix(SimpleMoves)
        mixB = op[c4d.ID_USERDATA,9] # User Data: Mix(Total)
        pos = op[c4d.ID_USERDATA,4] # User Data: Position
        scl = op[c4d.ID_USERDATA,5] # User Data: Scale
        rot = op[c4d.ID_USERDATA,6]
        rotMode = op[c4d.ID_USERDATA, 11] # User Data: Rotation
        objects = op[c4d.ID_USERDATA,2] # User Data: Target list

        # Handling the User Data
        udc = op.GetUserDataContainer() # Get user data container
        for descId, bc in udc:
            # Single line
            if descId[1].id == 1:
                if op[c4d.ID_USERDATA,8] == 0:
                    bc[c4d.DESC_HIDE] = False
                    op.SetUserDataContainer(descId, bc)
                else:
                    bc[c4d.DESC_HIDE] = True
                    op.SetUserDataContainer(descId, bc)
            if descId[1].id == 9:
                if op[c4d.ID_USERDATA,8] == 1:
                    bc[c4d.DESC_HIDE] = False
                    op.SetUserDataContainer(descId, bc)
                else:
                    bc[c4d.DESC_HIDE] = True
                    op.SetUserDataContainer(descId, bc)

        obj = op.GetObject() # Get object
        array = [] # Initialize a list for targets
        cnt = objects.GetObjectCount() # Get targets count
        for i in range(0, cnt): # Iterate through targets
            array.append(objects.ObjectFromIndex(doc, i)) # Add target to the list
        if mode == 0: # If 'Mode' is 'SimpleMoves'
            data = mixA
        else: # If 'Mode' is 'Total'
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
