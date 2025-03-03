from random import random

from example.messages.ender_after_cron_answer_message import EnderAfterCronAnswerMessage
from example.messages.ender_after_cron_input_message import EnderAfterCronInputMessage
from ul_unipipeline.answer.uni_answer_message import UniAnswerMessage
from ul_unipipeline.message.uni_cron_message import UniCronMessage
from ul_unipipeline.worker.uni_worker import UniWorker
from ul_unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage


class MySuperCronWorker(UniWorker[UniCronMessage, None]):
    def handle_message(self, msg: UniWorkerConsumerMessage[UniCronMessage]) -> None:
        print(f'!!!!! MySuperCronWorker MESSAGE {msg.payload}')  # noqa
        some = int(random() * 10000)
        answ: UniAnswerMessage[EnderAfterCronAnswerMessage] = self.manager.get_answer_from('ender_after_cron_worker', EnderAfterCronInputMessage(value=f'cron>>>{msg.payload.task_name}', count=some))
        assert answ.payload.result == some * 3
        print('>>>>>>', some, answ.payload.value)  # noqa
