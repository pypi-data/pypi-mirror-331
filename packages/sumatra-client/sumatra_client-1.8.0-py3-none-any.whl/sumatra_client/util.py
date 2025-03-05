import os


def humanize_status(status: str):
    """
    Translate server-side status to human-readable, standardized identifier
    """
    standardize = {
        "New": "Processing",
        "Running": "Processing",
        "Offline": "Processing",
        "Online": "Ready",
    }
    if status in standardize:
        return standardize[status]
    return status.title()


def splitext(path: str):
    fullext = ""
    while True:
        path, ext = os.path.splitext(path)
        if ext:
            fullext = ext + fullext
        else:
            break
    return os.path.basename(path), fullext
