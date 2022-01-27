"""Component Manager for Multi Device."""
import time
import tango

from ska_tango_base.base.component_manager import TaskExecutorComponentManager
from ska_tango_base.executor import TaskStatus


class MultiDeviceComponentManager(TaskExecutorComponentManager):
    """Component Manager for Multi Device."""

    def non_aborting_lrc(self, argin, task_callback=None):
        """Take a long time to complete.

        :param argin: How long to sleep per iteration
        :type argin: int
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        """

        def noop(logger, argin, task_callback=None, task_abort_event=None):
            retries = 45
            while retries > 0:
                retries -= 1
                time.sleep(argin)  # This command takes long
                logger.info(
                    "In NonAbortingTask repeating %s",
                    retries,
                )
            task_callback(status=TaskStatus.COMPLETED, result="non_aborting_lrc OK")

        task_status, response = self.submit_task(
            noop, args=[self.logger, argin], task_callback=task_callback
        )
        return task_status, response

    def aborting_lrc(self, argin, task_callback=None):
        """Abort a task in progress.

        :param argin: How long to sleep per iteration
        :type argin: int
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        """

        def noop_abort(logger, argin, task_callback=None, task_abort_event=None):
            retries = 45
            while (not task_abort_event.is_set()) and retries > 0:
                retries -= 1
                time.sleep(argin)  # This command takes long
                logger.info("In NonAbortingTask repeating %s", retries)

            if retries == 0:  # Normal finish
                task_callback(
                    status=TaskStatus.COMPLETED,
                    result=f"NonAbortingTask completed {argin}",
                )
            else:  # Aborted finish
                task_callback(
                    status=TaskStatus.ABORTED, result=f"NonAbortingTask Aborted {argin}"
                )

        task_status, response = self.submit_task(
            noop_abort, args=[self.logger, argin], task_callback=task_callback
        )
        return task_status, response

    def throw_exc(self, task_callback=None):
        """Illustrate exceptions.

        :param task_callback: Update task status
        :type task_callback: Callable
        """

        def noop_exc(logger, task_callback=None, task_abort_event=None):
            try:
                logger.info("About to raise an error")
                raise RuntimeError("Something went wrong")
            except RuntimeError as err:
                task_callback(status=TaskStatus.FAILED, result=f"{err}")

        task_status, response = self.submit_task(
            noop_exc, args=[self.logger], task_callback=task_callback
        )
        return task_status, response

    def show_progress(self, argin, task_callback=None):
        """Illustrate progress.

        :param argin: Time to sleep between each progress update
        :type argin: float
        :param task_callback: Update task status
        :type task_callback: Callable
        """

        def noop_progress(logger, argin, task_callback=None, task_abort_event=None):
            task_callback(status=TaskStatus.IN_PROGRESS)
            for progress in [1, 25, 50, 74, 100]:
                task_callback(progress=progress)
                logger.info("Progress %s", progress)
                time.sleep(argin)
            task_callback(status=TaskStatus.COMPLETED, result="Progress completed")

        task_status, response = self.submit_task(
            noop_progress, args=[self.logger, argin], task_callback=task_callback
        )
        return task_status, response

    def call_children(self, argin, client_devices, task_callback=None):
        """Call child devices.

        :param argin: Time to sleep if this device does not have children.
        :type argin: float
        :param client_devices: List of client devices
        :type client_devices: List
        :param task_callback: Update task status
        :type task_callback: Callable
        """

        def call_lower_level_devices(
            logger, argin, client_devices, task_callback=None, task_abort_event=None
        ):
            if client_devices:
                for device in client_devices:
                    logger.info("Calling child %s", device)
                    proxy = tango.DeviceProxy(device)
                    proxy.CallChildren(argin)
                task_callback(
                    status=TaskStatus.COMPLETED,
                    result=f"Called children {client_devices}",
                )
            else:
                task_callback(status=TaskStatus.IN_PROGRESS)
                logger.info("Waiting in leaf device %s", argin)
                time.sleep(argin)
                task_callback(status=TaskStatus.COMPLETED, result="Finished leaf node")

        task_status, response = self.submit_task(
            call_lower_level_devices,
            args=[self.logger, argin, client_devices],
            task_callback=task_callback,
        )
        return task_status, response
