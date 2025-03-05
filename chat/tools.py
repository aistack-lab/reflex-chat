from __future__ import annotations

import reflex as rx


def save_file(path: str, data: str):
    """Save a file to the upload directory.

    Args:
        path: The filename of the file to create.
        data: The data to save.
    """
    outfile = rx.get_upload_dir() / path

    # Save the file.
    with outfile.open("wt") as file_object:
        file_object.write(data)
