from senderstats.common.utils import parse_email_details, convert_srs, remove_prvs
from senderstats.data.message_data import MessageData
from senderstats.interfaces.transform import Transform


class RPathTransform(Transform[MessageData, MessageData]):
    def __init__(self, decode_srs: bool = False, remove_prvs: bool = False):
        super().__init__()
        self.__decode_srs = decode_srs
        self.__remove_prvs = remove_prvs

    def transform(self, data: MessageData) -> MessageData:
        # If sender is not empty, we will extract parts of the email
        rpath_parts = parse_email_details(data.rpath)
        rpath = rpath_parts['email_address']

        if self.__decode_srs:
            rpath = convert_srs(rpath)

        if self.__remove_prvs:
            rpath = remove_prvs(rpath)

        data.rpath = rpath
        return data
