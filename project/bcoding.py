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

    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NjU4NjYwLCJpYXQiOjE3NjQ1NzIyNjAsImp0aSI6IjdmODFkOWU3YTlkMzQ4YmY5ZjJiODM1MWYyZmM4Y2Q0IiwiZW1haWwiOiJnS1VAbWFpbC5ydSJ9.9FxcnAQh97LU54hOjUgPMjjZ8vFgI1XkcXk6LnvlzTw'
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

    # def django_object_to_binary(self, request: Request,
    #                             serializers: PersonSerializerList) -> bytes | None:
    #
    #     # ===== CHECK DJANGO's MODEL
    #     if isinstance(element, Model):
    #         serializers = serializers(element)
    #         model_json = json.dumps(element).encode("utf-8")
    #         return base64.b64encode(model_json)
    #     return None

    # def binary_to_django_object(self, element: bytes) -> TypeUserModel | None:

    # def object_to_binary(self, element) -> bytes:
    #     """
    #     Thi is uses the pickle library for working with a BINARY and JSON data.
    #     Converting an object to binary data.
    #     :param dict | json element:
    #     :return: bytes
    #     """
    #     text_error = "[%s.%s]: pickle.ERROR => " % (
    #         self.__class__.__name__,
    #         self.object_to_binary.__name__,
    #     )
    #     try:
    #         return pickle.dumps(element)
    #     except (pickle.PickleError, pickle.UnpicklingError) as e:
    #         log.error(f"{text_error} %s", (str(e),))
    #         raise f"{text_error} %s" % str(e)
    #     except json.JSONDecodeError as e:
    #         log.error(f"{text_error} %s", (str(e),))
    #         raise f"{text_error} %s" % str(e)
    #     except Exception as e:
    #         log.error(f"{text_error} %s", (str(e),))
    #         raise f"{text_error} %s" % str(e)
    #
    # def binary_to_(self, binary_data: bytes) -> dict | Optional[json]:
    #     """
    #     Read a description to the "self.object_to_binary". Only one. This converts bytes to the object/json.
    #     :param bytes binary_data:
    #     :return: dict | json
    #     """
    #     text_error = "[%s.%s]: pickle.ERROR => " % (
    #         self.__class__.__name__,
    #         self.binary_to_.__name__,
    #     )
    #     try:
    #         return pickle.loads(binary_data, errors="")
    #     except (pickle.PickleError, pickle.UnpicklingError) as e:
    #         log.error(f"{text_error} %s", (str(e),))
    #         raise f"{text_error} %s" % str(e)
    #     except json.JSONDecodeError as e:
    #         log.error(f"{text_error} %s", (str(e),))
    #         raise f"{text_error} %s" % str(e)
    #     except Exception as e:
    #         log.error(f"{text_error} %s", (str(e),))
    #         raise f"{text_error} %s" % str(e)
