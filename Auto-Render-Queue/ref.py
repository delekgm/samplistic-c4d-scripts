"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Adds all Cinema 4D files from a selected folder to the render queue.

Class/method highlighted:
    - c4d.documents.BatchRender
    - c4d.documents.GetBatchRender()
    - BatchRender.AddFile()

"""
import c4d
import os


def main():
    # Retrieves a directory
    directory = c4d.storage.LoadDialog(flags=c4d.FILESELECT_DIRECTORY)
    if directory is None:
        return True

    # Retrieves a list of all Cinema 4D files of this directory
    # os.listdir base its encoding on the passed encoding of the directory
    # so it's important to pass an unicode string.
    c4dFiles = list()
    for file in os.listdir(directory):
        if file.endswith(".c4d"):
            c4dFiles.append(os.path.join(directory, file))

    if not c4dFiles:
        raise RuntimeError("There is no Cinema 4D file in this directory.")

    # Retrieves the batch render instance
    br = c4d.documents.GetBatchRender()
    if br is None:
        raise RuntimeError("Failed to retrieve the batch render instance.")

    # Iterates the list of Cinema 4D paths and adds them in the BatchRender
    for file in c4dFiles:
        print(file)
        br.AddFile(file, br.GetElementCount())

    # Opens the Batch Render
    br.Open()


if __name__ == "__main__":
    main()
    
# # Print render settings info
# print(f"Output Path: {output_path} -> {output_path_abs}")
# print(f"Multipass Output Path: {multipass_output_path} -> {multipass_output_path_abs}")