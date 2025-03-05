import logging
import sys

log = logging
log.basicConfig(
    level=log.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="[%d.%m.%Y %H:%M:%S]",
    handlers=[log.StreamHandler(sys.stdout)]
)
