from ul_unipipeline.message.uni_message import UniMessage


class EnderAfterCronInputMessage(UniMessage):
    value: str
    count: int
