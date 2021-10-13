from contextlib import contextmanager
from typing import IO, Optional

import practipy.logs as logs


@contextmanager
def redirect_logs(file: Optional[IO] = None):
    import absl

    with logs.redirect_logs(
        logger=absl.logging.get_absl_logger(),
        handler=absl.logging.get_absl_handler(),
        file=file,
    ):
        yield
