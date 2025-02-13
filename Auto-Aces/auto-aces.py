import c4d
import redshift #type: ignore

# This is the plugin ID for the Redshift Post Effects node in Cinema 4D
REDSHIFT_VIDEOPOST_ID = 1036219

def get_redshift_render_settings(doc):
    render_settings = doc.GetActiveRenderData()
    
    if not render_settings:
        print("No render settings found.")
        return
    
     # Verify Redshift is active
    if render_settings[c4d.RDATA_RENDERENGINE] != c4d.RDATA_RENDERENGINE_REDSHIFT:
        print("Redshift is not the active renderer.")
        return
    
    # Loop over all Video Post effects in the active render setting
    # Get the Redshift render settings
    vp = render_settings.GetFirstVideoPost()
    while vp:
        if vp.GetType() == c4d.RDATA_RENDERENGINE_REDSHIFT:
            return vp
            # We found our Redshift node and handled it, so we can break
            break
        vp = vp.GetNext()
    return None

def PrintAOVs(vpRS):
    aovs = redshift.RendererGetAOVs(vpRS)
    for aov in aovs:
        print("-----------------------------------------------------------")
        print("Name                  :%s" % aov.GetParameter(c4d.REDSHIFT_AOV_NAME))
        print("Type                  :%d" % aov.GetParameter(c4d.REDSHIFT_AOV_TYPE))
        print("Enabled               :%s" % ("Yes" if aov.GetParameter(c4d.REDSHIFT_AOV_ENABLED) else "No"))
        print("Multi-Pass            :%s" % ("Yes" if aov.GetParameter(c4d.REDSHIFT_AOV_MULTIPASS_ENABLED) else "No"))
        print("Direct                :%s" % ("Yes" if aov.GetParameter(c4d.REDSHIFT_AOV_FILE_ENABLED) else "No"))
        print("Direct Path           :%s" % aov.GetParameter(c4d.REDSHIFT_AOV_FILE_PATH))
        #print("Direct Effective Path :%s" % aov.GetParameter(c4d.REDSHIFT_AOV_FILE_EFFECTIVE_PATH)) # Available from 2.6.44/3.0.05

def CreateBeautyAOV(rs_settings):
    aovs = redshift.RendererGetAOVs(rs_settings)
    for aov_ in aovs:
        if aov_.GetParameter(c4d.REDSHIFT_AOV_TYPE) == c4d.REDSHIFT_AOV_TYPE_BEAUTY:
            print("Beauty AOV already exists")
            return
    aov = redshift.RSAOV()
    aov.SetParameter(c4d.REDSHIFT_AOV_TYPE, c4d.REDSHIFT_AOV_TYPE_BEAUTY)
    aov.SetParameter(c4d.REDSHIFT_AOV_ENABLED, True)
    aov.SetParameter(c4d.REDSHIFT_AOV_NAME, "My Beauty")
    aov.SetParameter(c4d.REDSHIFT_AOV_MULTIPASS_ENABLED, True)
    aov.SetParameter(c4d.REDSHIFT_AOV_MULTIPASS_BIT_DEPTH, c4d.REDSHIFT_AOV_MULTIPASS_BIT_DEPTH_32)
    aovs.append(aov)
    # Set the aovs in the renderer
    redshift.RendererSetAOVs(rs_settings, aovs)
    print("Beauty AOV created")
    return

def main():
    doc = c4d.documents.GetActiveDocument()
    # Start an undo group
    doc.StartUndo()
    
    rs_settings = get_redshift_render_settings(doc)
    if not rs_settings:
        print("No render settings found.")
        return

    ocio_view = rs_settings[c4d.REDSHIFT_RENDERER_COLOR_MANAGEMENT_OCIO_VIEW]
    view_transform = rs_settings[c4d.REDSHIFT_RENDERER_COLOR_MANAGEMENT_COMPENSATE_VIEW_TRANSFORM]
    print(f"Current OCIO View: {ocio_view}, View Transform: {view_transform}")
    
    if ocio_view == "ACES 1.0 SDR-video":
        new_view = "Raw"
        new_view_transform = 0
        rs_settings[c4d.REDSHIFT_RENDERER_COLOR_MANAGEMENT_OCIO_VIEW] = new_view
        rs_settings[c4d.REDSHIFT_RENDERER_COLOR_MANAGEMENT_COMPENSATE_VIEW_TRANSFORM] = new_view_transform
        # Create the beauty AOV if the user has not created it yet
        CreateBeautyAOV(rs_settings)
    elif ocio_view == "Raw":
        new_view = "ACES 1.0 SDR-video"
        new_view_transform = 1
        rs_settings[c4d.REDSHIFT_RENDERER_COLOR_MANAGEMENT_OCIO_VIEW] = new_view
        rs_settings[c4d.REDSHIFT_RENDERER_COLOR_MANAGEMENT_COMPENSATE_VIEW_TRANSFORM] = new_view_transform
    print(f"New OCIO View set to: {new_view}, View Transform set to: {new_view_transform}")

    # c4d.gui.MessageDialog(f"New OCIO View set to: {new_view}, View Transform set to: {new_view_transform}")
    
    # PrintAOVs(rs_settings)
    # End an undo group
    doc.EndUndo()
    
    # Refresh Cinema 4D to reflect changes
    c4d.EventAdd()

if __name__ == "__main__":
    main()
