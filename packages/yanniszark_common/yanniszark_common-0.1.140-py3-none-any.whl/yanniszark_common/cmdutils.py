import logging
import subprocess
from typing import List, Union
from subprocess import TimeoutExpired, CalledProcessError


log = logging.getLogger(__name__)


def run(*args, **kwargs):
    """Run commands idiomatically.

    Differences from default subprocess.run:
    - Errors raise an exception instead of having to check.
    """
    if "check" not in kwargs:
        kwargs["check"] = True
    return subprocess.run(*args, **kwargs)


def check_output(*args, **kwargs):
    """Run commands idiomatically.

    Differences from default subprocess.check_output:
    - Output is returned as a string instead of bytes.
    """
    if "text" not in kwargs:
        kwargs["text"] = True
    return subprocess.check_output(*args, **kwargs)


def remote_check_output(
    hostname: str,
    cmd: Union[str, List[str]],
    timeout=None,
    retries=0,
) -> str:
    if isinstance(cmd, str):
        cmd = [cmd]
    while retries >= 0:
        retries -= 1
        try:
            ssh_prefix = ["ssh", "-A"]
            if timeout:
                ssh_prefix += ["-o", "ConnectTimeout=%s" % timeout]
            ssh_prefix += [hostname]
            process = run(
                ssh_prefix + cmd,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
            return process.stdout
        except TimeoutExpired as e:
            log.debug("Command timed out: %s" % " ".join(e.cmd))
            raise e
        except CalledProcessError as e:
            log.error("Command failed: %s" % " ".join(e.cmd))
            log.error("Return code: %s" % e.returncode)
            log.error("Stdout: %s" % e.stdout)
            log.error("Stderr: %s" % e.stderr)
            raise e
