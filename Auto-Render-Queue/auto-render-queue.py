"""
Script: Auto Render Queue
Author: Delek Miller, Samplistic
Version: 1.0.0
Description: 
    This script will automatically add the current document to the render queue and set the render paths to the absolute paths.

Usage:
1. Save your Cinema 4D document
2. Run the script
3. The script will:
   - Add the current document to the render queue
   - Convert any relative render paths to absolute paths
   - Create output directories if they don't exist
   - Open the render queue window
4. If you do not have a render path set, the script will use the document path as the output path for only the beauty pass.

Dependencies:
    This script uses Python's built-in `webbrowser` module.
"""


import c4d
import os

doc: c4d.documents.BaseDocument  # The currently active document.
op: c4d.BaseObject | None  # The primary selected object in `doc`. Can be `None`.


# Convert paths to absolute paths if they are relative
def convert_to_absolute_path(path, base_path):
    """Converts a relative path to an absolute path."""
    if not path:
        return None
    if not os.path.isabs(path):
        return os.path.abspath(os.path.join(base_path, path))
    return path


def directory_exists(path):
    """Ensures that the specified directory exists. If it doesn't, creates it."""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Directory created: {path}")
        except Exception as e:
            print(f"Failed to create directory {path}: {e}")
            return False
    else:
        print(f"Directory already exists: {path}")
    return True


def check_directory(path):
    output_dir = os.path.dirname(path) + os.sep
    if not directory_exists(output_dir):
        c4d.gui.MessageDialog("Failed to create output directory.")
        return


def get_info():
    try:
        # Get the current document path
        doc_path = doc.GetDocumentPath()
        if not doc_path:
            c4d.gui.MessageDialog("Document is not saved. Save the document before rendering.")
            return
        
        file_name = doc.GetDocumentName()
        if not file_name:
            c4d.gui.MessageDialog("No file name found.")
            return

        # Get the active render settings
        render_settings = doc.GetActiveRenderData()
        if not render_settings:
            c4d.gui.MessageDialog("No active render settings found.")
            return
        return doc_path, file_name, render_settings
    except ValueError as e:
        c4d.gui.MessageDialog(str(e))
        return None, None, None


def get_output_paths(render_settings):
    output_path = render_settings[c4d.RDATA_PATH] or ""
    multipass_output_path = render_settings[c4d.RDATA_MULTIPASS_FILENAME] or ""
    return output_path, multipass_output_path


def set_output_paths(render_settings, output_path, multipass_output_path):
    render_settings[c4d.RDATA_PATH] = output_path or ""
    render_settings[c4d.RDATA_MULTIPASS_FILENAME] = multipass_output_path or ""


def save_document(doc, file_name, doc_path):
    if not c4d.documents.SaveDocument(doc, os.path.join(doc_path, file_name), c4d.SAVEDOCUMENTFLAGS_0, c4d.FORMAT_C4DEXPORT):
        c4d.gui.MessageDialog("Failed to save the document.")
        return


def main() -> None:
    try:
        # Get the current document
        doc = c4d.documents.GetActiveDocument()
        
        # Start an undo group
        doc.StartUndo()
        
        doc_path, file_name, render_settings = get_info()

        # Get output paths
        output_path, multipass_output_path = get_output_paths(render_settings)

        output_path_abs = convert_to_absolute_path(output_path, doc_path)
        multipass_output_path_abs = convert_to_absolute_path(multipass_output_path, doc_path)

        if output_path_abs:
            check_directory(output_path_abs) 
        if multipass_output_path_abs:
            check_directory(multipass_output_path_abs)

        if not output_path_abs:
            output_path_abs = doc_path + os.sep

        # Update the render settings with absolute paths
        set_output_paths(render_settings, output_path_abs, multipass_output_path_abs)

        # Save the document to ensure paths are saved
        save_document(doc, file_name, doc_path)

        # Access the BatchRender object
        batch_render = c4d.documents.GetBatchRender()
        if batch_render is None:
            c4d.gui.MessageDialog("Render Queue is not available.")
            return

        # Add the current document to the render queue
        file = os.path.join(doc_path, file_name)
        job = batch_render.AddFile(file, batch_render.GetElementCount())
        if job is None:
            c4d.gui.MessageDialog("Failed to add the job to the render queue.")
            return
        
        # Reset the render settings to the original values
        set_output_paths(render_settings, output_path, multipass_output_path)
        
        # Save the document to reflect changes
        save_document(doc, file_name, doc_path)
        
        # End the undo group
        doc.EndUndo()
        
        # Refresh Cinema 4D to reflect changes
        c4d.EventAdd()
        
        # Open the Batch Render
        batch_render.Open()
    except Exception as e:
        c4d.gui.MessageDialog(f"An error occurred: {e}")

if __name__ == '__main__':
    main()

# ../c4d_outputs/$prj_$frame
# ../c4d_outputs/aov/aov-$prj_$frame
