from typing import NamedTuple, Callable

from ul_unipipeline.message_meta.uni_message_meta import UniMessageMeta


class UniBrokerConsumer(NamedTuple):
    topic: str
    id: str
    group_id: str
    unwrapped: bool
    prefetch_count: int
    message_handler: Callable[[Callable[[], UniMessageMeta]], None]
