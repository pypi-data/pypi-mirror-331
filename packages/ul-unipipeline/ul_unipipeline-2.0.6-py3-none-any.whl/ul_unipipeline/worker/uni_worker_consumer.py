import math
import uuid
from typing import TypeVar, Generic, Optional, Type, Any, Union, Dict, TYPE_CHECKING, Callable

from ul_unipipeline.answer.uni_answer_message import UniAnswerMessage
from ul_unipipeline.definitions.uni_worker_definition import UniWorkerDefinition
from ul_unipipeline.errors import UniMessagePayloadParsingError, \
    UniAnswerMessagePayloadParsingError, UniSendingToUndefinedWorkerError, UniMessageRejectError
from ul_unipipeline.message.uni_message import UniMessage
from ul_unipipeline.message_meta.uni_message_meta import UniMessageMeta, UniMessageMetaErrTopic, UniAnswerParams
from ul_unipipeline.worker.uni_msg_params import UniGettingAnswerParams, UniSendingParams, TUniSendingMessagePayloadUnion, TUniSendingWorkerUnion
from ul_unipipeline.worker.uni_worker import UniWorker
from ul_unipipeline.worker.uni_worker_consumer_manager import UniWorkerConsumerManager
from ul_unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage

if TYPE_CHECKING:
    from ul_unipipeline.modules.uni_mediator import UniMediator

TInputMsgPayload = TypeVar('TInputMsgPayload', bound=UniMessage)
TAnswerMsgPayload = TypeVar('TAnswerMsgPayload', bound=Optional[UniMessage])


class UniWorkerConsumer(Generic[TInputMsgPayload, TAnswerMsgPayload]):
    def __init__(self, definition: UniWorkerDefinition, mediator: 'UniMediator', worker_type: Type[UniWorker[TInputMsgPayload, TAnswerMsgPayload]]) -> None:
        self._definition = definition
        self._mediator = mediator

        self._worker_manager = UniWorkerConsumerManager(self._send_to, self._get_answer_from)

        self._worker = worker_type(self._worker_manager)
        self._uni_echo = mediator.echo.mk_child(f'worker[{definition.name}]')

        self._input_message_type: Type[TInputMsgPayload] = mediator.get_message_type(self._definition.input_message.name)  # type: ignore
        self._answer_message_type: Optional[Type[TAnswerMsgPayload]] = mediator.get_message_type(self._definition.answer_message.name) if self._definition.answer_message is not None else None  # type: ignore

        self._current_meta: Optional[UniMessageMeta] = None

    def _get_answer_from(
        self,
        worker: TUniSendingWorkerUnion,
        data: TUniSendingMessagePayloadUnion,
        *,
        params: UniGettingAnswerParams,
    ) -> Optional[UniAnswerMessage[UniMessage]]:
        answer_params = UniAnswerParams(
            topic=self._definition.answer_topic,
            id=uuid.uuid4(),  # self._worker_manager.id
            ttl_s=math.ceil(params.answer_tll.total_seconds()),
        )
        return self._mediator.get_answer_from(worker, data, parent_meta=self._current_meta, answer_params=answer_params, params=params)

    def _send_to(
        self,
        worker: TUniSendingWorkerUnion,
        data: TUniSendingMessagePayloadUnion,
        *,
        params: UniSendingParams,
    ) -> None:
        wd = self._mediator.config.get_worker_definition(worker)
        if wd.name not in self._definition.output_workers:
            raise UniSendingToUndefinedWorkerError(f'worker {wd.name} is not defined in workers->{self._definition.name}->output_workers')
        self._mediator.send_to(wd.name, data, parent_meta=self._current_meta, params=params)

    def process_message(self, get_meta: Callable[[], UniMessageMeta]) -> None:
        self._current_meta = None

        self._uni_echo.log_debug('processing start')
        try:
            meta = get_meta()
            msg = UniWorkerConsumerMessage[TInputMsgPayload](self._input_message_type, meta)
        except Exception as e: # noqa
            self._uni_echo.log_error(str(e))
            return

        self._current_meta = meta
        self._uni_echo.log_debug(f'meta unpacked successfully {meta.id}')

        try:
            result: Optional[Union[TAnswerMsgPayload, Dict[str, Any]]] = self._worker.handle_message(msg)

        except UniAnswerMessagePayloadParsingError as e:
            self._uni_echo.log_warning(f'payload is invalid! message {meta.id} was skipped')
            self._mediator.move_to_error_topic(self._definition, meta, UniMessageMetaErrTopic.ANSWER_MESSAGE_PAYLOAD_ERR, e)
            self._current_meta = None
            return

        except UniMessagePayloadParsingError as e:
            self._uni_echo.log_warning(f'answer payload is invalid! message {meta.id} was skipped')
            self._mediator.move_to_error_topic(self._definition, meta, UniMessageMetaErrTopic.MESSAGE_PAYLOAD_ERR, e)
            self._current_meta = None
            return

        except UniMessageRejectError as e:
            self._uni_echo.log_warning(f'rejected message {meta.id}')
            if e.rejection_exception is not None:
                self._mediator.move_to_error_topic(self._definition, meta, UniMessageMetaErrTopic.USER_ERROR, e.rejection_exception)
                self._current_meta = None
                return  # JUST ACK
            else:
                self._current_meta = None
                raise

        self._uni_echo.log_debug(f'processing successfully done {meta.id}')
        if meta.need_answer and self._definition.need_answer:
            try:
                self._mediator.answer_to(self._definition.name, meta, result, unwrapped=self._definition.answer_unwrapped)
            except UniSendingToUndefinedWorkerError:
                pass

        self._current_meta = None
