import base64
import logging
from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class DcodeManager:
    def str_to_bynary(self, context: str) -> base64.b64encode:
        """
        https://docs.djangoproject.com/en/5.2/topics/serialization/#serializing-data
        This is function is works with string
        :param srt context:
        :return: base64.b64encode
        """
        if not context or not isinstance(context, str):
            raise TypeError(
                "[%s.%s]: 'context' must be a string",
                self.__class__.__name__,
                self.str_to_bynary.__name__,
            )
        try:
            return base64.b64encode(context.encode("utf-8"))

        except Exception as e:
            test_error = "[%s.%s]: ERROR => %s" % (
                self.__class__.__name__,
                self.str_to_bynary.__name__,
                e.args[0],
            )
            log.error(test_error)
            raise test_error


    def bynary_to_str(self, context: str) -> str:
        """
        This is function is works with string
        :param context: this is string from string of 'base64.b64encode'
        :return: str
        """
        if not context or not isinstance(context, str):
            raise TypeError(
                "[%s.%s]: 'context' must be a string",
                self.__class__.__name__,
                self.bynary_to_str.__name__,
            )
        try:
            return base64.b64decode(context.encode("utf-8")).decode("utf-8")
        except Exception as e:
            test_error = "[%s.%s]: ERROR => %s" % (
                self.__class__.__name__,
                self.bynary_to_str.__name__,
                e.args[0],
            )
            log.error(test_error)
            raise test_error
