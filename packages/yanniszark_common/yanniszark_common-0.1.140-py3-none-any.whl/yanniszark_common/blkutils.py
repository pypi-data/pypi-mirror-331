from subprocess import check_output, CalledProcessError


def has_filesystem(blkdev_path: str):
    """Returns True if the given block device has a filesystem on it."""
    blkdev_details = blkid(blkdev_path)
    return blkdev_details.get("USAGE") == "filesystem"


def blkid(path):
    """Returns a dictionary of the output of blkid for the given path."""
    blkdev_details = {}
    try:
        blkid_res = check_output(["sudo", "blkid", "-p", "--output", "export",
                                  path], encoding="utf-8")
    except CalledProcessError as e:
        # A return code of 2 means that blkid couldn't get any info on the
        # device.
        if e.returncode == 2:
            blkid_res = ""
    for line in blkid_res.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("=", 1)
        blkdev_details[parts[0]] = parts[1]
    return blkdev_details
