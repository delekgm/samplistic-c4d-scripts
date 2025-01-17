import c4d
import c4d.gui

class RenderOptionsDialog(c4d.gui.GeDialog):
    def __init__(self):
        super().__init__()
        self.render_beauty = False  # Initial state for the "Render Beauty Pass" checkbox
        self.render_multipass = False  # Initial state for the "Render Multipass" checkbox
    
    def CreateLayout(self):
        """Defines the layout of the dialog."""
        self.SetTitle("Render Options")  # Dialog title
        
        # Add a title text
        self.GroupBegin(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1, title="")
        self.AddStaticText(2000, c4d.BFH_CENTER, name="Select Render Options:")
        self.GroupEnd()
        
        # Add checkboxes
        self.GroupBegin(1001, c4d.BFH_CENTER | c4d.BFV_CENTER, cols=1, title="Options")
        self.AddCheckbox(3000, c4d.BFH_LEFT, 0, 0, "Render Beauty Pass")
        self.AddCheckbox(3001, c4d.BFH_LEFT, 0, 0, "Render Multipass")
        self.GroupEnd()
        
        # Add OK and Cancel buttons
        self.GroupBegin(1002, c4d.BFH_CENTER, cols=2, title="")
        self.AddButton(c4d.DLG_OK, c4d.BFH_SCALE, name="OK")
        self.AddButton(c4d.DLG_CANCEL, c4d.BFH_SCALE, name="Cancel")
        self.GroupEnd()
        
        return True

    def Command(self, id, msg):
        """Handles user interactions with the dialog."""
        if id == c4d.DLG_OK:  # OK button
            # Retrieve the checkbox values
            self.render_beauty = self.GetBool(3000)
            self.render_multipass = self.GetBool(3001)
            
            # Print the results
            print("User clicked OK")
            print(f"Render Beauty Pass: {self.render_beauty}")
            print(f"Render Multipass: {self.render_multipass}")
            
            # Close the dialog
            self.Close()
        
        elif id == c4d.DLG_CANCEL:  # Cancel button
            print("User clicked Cancel")
            self.Close()
        
        return True

# Run the dialog
def main():
    dialog = RenderOptionsDialog()
    dialog.Open(c4d.DLG_TYPE_MODAL)

if __name__ == "__main__":
    main()
