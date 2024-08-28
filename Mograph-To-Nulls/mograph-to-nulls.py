#www.lasselauch.com/lab/
#Use at your own risk
#Last-Modified: 07/11/2018

#Original Coffee-Script & Concept by Per Anders. (http://peranders.com/)

import c4d
if c4d.modules.CheckMoGraph():
    from c4d.modules import mograph as mo

def MographOrSelection(link):
    #Mograph, Matrix, Fracture, Voronoi Fracture
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
        nlname = """{name}_{i}""".format(**locals())
        nl.SetName(nlname)
        nltemp = nl

        if selection and c4d.GetC4DVersion() >= 18020:
            sel = mo.GeGetMoDataSelection(link.GetMain()).GetAll(count)
            if sel[i]:
                nlname = """{name}_Selection_{i}""".format(**locals())
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
        for i in xrange(len(marr)):
            if sel[i]:
                ma.append(marr[i])
                ca.append(carr[i])
        marr, carr = ma, ca

    checknulls(root, md, link, selection)
    children = root.GetChildren()

    if not children:
        return

    for i in range(len(marr)):
        #SET MATRIX
        if mograph:
            root.SetMg(link.GetMg())
        if selection:
            root.SetMg(link.GetMain().GetMg())
        children[i].SetMl(marr[i])

        #SET COLOR
        children[i][c4d.ID_BASEOBJECT_USECOLOR] = 0
        children[i][c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1,1,1)
        if op[c4d.ID_USERDATA,3]:
            children[i][c4d.ID_BASEOBJECT_USECOLOR] = 1
            children[i][c4d.ID_BASEOBJECT_COLOR] = carr[i]
            children[i][c4d.ID_BASELIST_ICON_COLOR] = carr[i]