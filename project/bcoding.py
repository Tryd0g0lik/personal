import base64


class DcodeManager:
    def str_to_bcode(self, context: str) -> base64.b64encode:
        """
        This is function is works with string
        :param srt context:
        :return: base64.b64encode
        """
        if not context or not isinstance(context, str):
            raise TypeError("[%s.%s]: 'context' must be a string", self.__class__.__name__, self.str_to_bcode.__name__)
        return base64.b64encode(context.encode('utf-8'))

    def bcode_to_str(self, context: str) -> str:
        """
        This is function is works with string
        :param context: this is string from string of 'base64.b64encode'
        :return: str
        """
        if not context or not isinstance(context, str):
            raise TypeError("[%s.%s]: 'context' must be a string", self.__class__.__name__, self.bcode_to_str.__name__)
        return base64.b64decode(context.encode('utf-8')).decode('utf-8')


