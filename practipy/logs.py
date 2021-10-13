import logging
from typing import IO, Optional


class redirect_logs:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        handler: Optional[logging.Handler] = None,
        file: Optional[IO] = None,
    ):
        # Either use the specfied logger or use the default python logger
        self.logger = logger or logging.root

        # Either use the specified handler or use the default python handler
        if handler:
            self.handler = handler
        else:
            # Try getting a handler from the logger
            if len(self.logger.handlers) > 0:
                self.handler = self.logger.handlers[0]
            # Or just use the default handler from python loggng
            else:
                self.handler = logging.lastResort

        self.file = file

    def __enter__(self, *args, **kwargs):
        self._original_handle_func = self.logger.handle

        def redirect_handle(record):
            # Format the log like it normally would be and write it to the redirect file.
            if self.file:
                self.file.write(self.handler.format(record))

        self.logger.handle = redirect_handle

    def __exit__(self, *args, **kwargs):
        self.logger.handle = self._original_handle_func
