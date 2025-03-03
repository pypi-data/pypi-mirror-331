from enum import Enum


class UniMessageMetaErrTopic(Enum):
    SYSTEM_ERR = 'error_system'
    MESSAGE_PAYLOAD_ERR = 'error_message_payload'
    ANSWER_MESSAGE_PAYLOAD_ERR = 'error_answer_message_payload'
    HANDLE_MESSAGE_ERR = 'error_message_handling'
    ERROR_HANDLING_ERR = 'error_handling'
    USER_ERROR = 'user_error'
