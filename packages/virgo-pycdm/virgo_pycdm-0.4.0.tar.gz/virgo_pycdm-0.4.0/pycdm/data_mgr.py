import queue
import logging
from threading import Thread

import zmq.error

from .comm import ZmqAsyncConn

log = logging.getLogger(__name__)


class MsgReg(queue.Queue):

    def __init__(self, i):
        super().__init__()
        self._id = i

    def id_match(self, i: str):
        return self._id == i[0:len(self._id)]

    def add_msg(self, msg):
        self.put(msg)

    def get_msg(self):
        return self.get(block=True)[1]


class DataManager:

    def __init__(self, addr):
        self._cdm_async = ZmqAsyncConn(addr)

        self._thread = Thread(target=self._frame_reader)
        self._thread.start()

        self._msg_reg = []

    def close(self):
        log.info("Closing DataManager")
        self._cdm_async.disconnect()
        self._thread.join()

    def register(self, s):
        reg = MsgReg(s)
        self._msg_reg.append(reg)
        self._cdm_async.subscribe(s)
        return reg

    def _frame_reader(self):
        log.info("FRAME READER STARTED")
        try:
            while True:
                m = self._cdm_async.recv_msg()
                for i in self._msg_reg:
                    if i.id_match(m[0]):
                        i.add_msg(m)
        except zmq.error.ContextTerminated:
            log.warning("Exiting from frame reader")

