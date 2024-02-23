import threading

from typing import Dict, List

from gpt_code_ui.kernel_program.kernel import Kernel  # noqa: E402
from gpt_code_ui.kernel_program import config  # noqa: E402


class KernelManager:
    def __init__(self):
        self._logger = config.get_logger("Kernel Manager")
        self._kernels: Dict[str, Kernel] = {}
        self._kernels_lock = threading.Lock()

        self._logger.info("Creating Kernel Manager")

    def purge_kernels(self, session_ids: List[str]):
        self._kernels_lock.acquire()
        try:
            for session_id in session_ids:
                if (kernel := self._kernels.get(session_id, None)) is not None:
                    self._logger.info(f"Purging kernel for session {session_id}.")
                    kernel.terminate()
                    del self._kernels[session_id]
        finally:
            self._kernels_lock.release()

    def items(self):
        return self._kernels.items()

    def get(self, session_id: str, force_recreate: bool = False) -> Kernel:
        if force_recreate:
            self._logger.info(f"Removing kernel {session_id} to force recreation.")

            self._kernels_lock.acquire()
            try:
                self._kernels[session_id].terminate()
                del self._kernels[session_id]
            finally:
                self._kernels_lock.release()

        if session_id not in self._kernels:
            self._kernels_lock.acquire()
            try:
                # while waiting for the lock, the object already might have been created --> check again inside the lock
                if session_id not in self._kernels:
                    self._logger.info(f"Kernel {session_id} does not exist. Creating it.")
                    self._kernels[session_id] = Kernel(session_id)
            finally:
                self._kernels_lock.release()

        return self._kernels[session_id]

    def terminate(self):
        self._logger.info("Termination of kernel manager requested...")
        all_sessions = list(self._kernels.keys())
        self.purge_kernels(all_sessions)
        self._logger.info("Kernel manager terminated.")
