import logging
import os
import subprocess
import threading
import time
import traceback

from PyQt6.QtCore import QSettings

from backend.qmp_client import QMPClient
from backend.vm_meta import VMMetadata
from backend.vm_state import VMState
from gui.error_dialog import ErrorDialog


class VMProcess:
    AUDIO_BACKEND_ID = "qemuwin_audio"
    AUDIO_DEVICE_ARGS = {
        "ac97": ["-device", "AC97,audiodev={backend_id}"],
        "adlib": ["-device", "adlib,audiodev={backend_id}"],
        "cs4231a": ["-device", "cs4231a,audiodev={backend_id}"],
        "es1370": ["-device", "ES1370,audiodev={backend_id}"],
        "gus": ["-device", "gus,audiodev={backend_id}"],
        "hda": ["-device", "intel-hda", "-device", "hda-duplex,audiodev={backend_id}"],
        "sb16": ["-device", "sb16,audiodev={backend_id}"],
        "virtio": ["-device", "virtio-sound-pci,audiodev={backend_id}"],
    }

    def __init__(self, name, config, qmp_port, vnc_port=None):
        self.name = name
        self.config = config
        self.qmp_port = qmp_port
        self.vnc_port = vnc_port

        self.process = None
        self.state = VMState.STOPPED
        self.qmp = None

        self.metadata = VMMetadata("meta")

        self.killed = False

        self.on_state_changed = None
        self.on_stopped = None

    def _set_state(self, state):
        self.state = state

        if self.on_state_changed:
            self.on_state_changed(self.name, state)

    def start(self):
        if self.state != VMState.STOPPED:
            return

        self._set_state(VMState.STARTING)

        try:
            cmd = self._build_command()

            self.process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.qmp = QMPClient("127.0.0.1", self.qmp_port)

            # Wait for QMP while also checking whether QEMU exited.
            deadline = time.time() + 15

            while time.time() < deadline:
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()

                    message = (
                        f"QEMU exited before QMP became available.\n"
                        f"Exit code: {self.process.returncode}"
                    )

                    logging.error(message)
                    raise RuntimeError(message)

                try:
                    if self.qmp._wait_for_qmp(port=self.qmp_port):
                        break
                except (ConnectionRefusedError, ConnectionResetError, OSError):
                    pass

                time.sleep(0.25)
            else:
                raise TimeoutError("Timed out waiting for VM QMP")

            self.qmp.connect()

            logging.info("VM Running")
            self._set_state(VMState.RUNNING)

            self.qmp.add_event_listener(self._handle_qmp_event)

            self.metadata.save(
                {
                    "name": self.name,
                    "qmp_port": self.qmp_port,
                    "vnc_port": self.vnc_port,
                    "pid": self.process.pid,
                    "started_by_manager": True,
                    "last_state": "RUNNING"
                },
                self.name
            )

            # Start monitoring only after startup succeeds.
            threading.Thread(
                target=self._monitor,
                daemon=True
            ).start()

        except ConnectionRefusedError as error:
            logging.error("Error connecting to VM's QMP")
            self._set_state(VMState.ERROR)
            self._terminate_failed_start()

            dialog = ErrorDialog(
                "Error Connecting to VM's QMP",
                "".join(traceback.format_exception(error))
            )
            dialog.exec()

            raise

        except Exception:
            self._set_state(VMState.ERROR)
            self._terminate_failed_start()
            raise

    def _build_command(self):
        settings = QSettings("QEMUWin", "QEMUWin")
        qemu_path = settings.value("qemu/path")

        if qemu_path:
            executable = os.path.join(
                str(qemu_path),
                "qemu-system-x86_64.exe"
            )
        else:
            executable = "qemu-system-x86_64.exe"
            logging.debug("Using QEMU from environment PATH")

        cmd = [executable]

        machine = self.config.get("machine")
        if machine == "pc-i440fx":
            machine = "pc"

        cmd += [
            "-m",
            str(self.config.get("memory")),
            "-machine",
            str(machine),
            "-qmp",
            f"tcp:127.0.0.1:{self.qmp_port},server,nowait"
        ]

        cpu_type = self.config.get("cpu") or {}
        cpu_model = cpu_type.get("model", "qemu64")
        cpu_cores = cpu_type.get("cores", 1)

        # Host CPU requires hardware acceleration.
        use_whpx = (
            cpu_model == "host"
            or bool(self.config.get("enable_whpx"))
        )

        if use_whpx:
            cmd += ["-accel", "whpx"]

        cmd += [
            "-cpu",
            str(cpu_model),
            "-smp",
            str(cpu_cores)
        ]

        controllers = set()

        for disk in self.config.get("storage") or []:
            disk_path = os.path.normpath(str(disk.get("path", "")))

            if not disk_path or not os.path.exists(disk_path):
                raise FileNotFoundError(
                    f"Storage path does not exist: {disk_path}"
                )

            disk_bus = disk.get("bus")
            disk_id = disk.get("id")

            if disk_bus == "virtio":
                if "virtio-scsi" not in controllers:
                    cmd += [
                        "-device",
                        "virtio-scsi-pci,id=virtio_scsi"
                    ]
                    controllers.add("virtio-scsi")

                cmd += [
                    "-drive",
                    f"file={disk_path},if=none,id=disk{disk_id}",
                    "-device",
                    (
                        f"scsi-hd,drive=disk{disk_id},"
                        f"bus=virtio_scsi.0"
                    )
                ]

            elif disk_bus == "scsi":
                if "lsi-scsi" not in controllers:
                    cmd += [
                        "-device",
                        "lsi53c895a,id=lsi_scsi"
                    ]
                    controllers.add("lsi-scsi")

                cmd += [
                    "-drive",
                    f"file={disk_path},if=none,id=disk{disk_id}",
                    "-device",
                    (
                        f"scsi-hd,drive=disk{disk_id},"
                        f"bus=lsi_scsi.0"
                    )
                ]

            elif disk_bus == "ide":
                cmd += [
                    "-drive",
                    f"file={disk_path},if=ide"
                ]

            elif disk_bus == "sata":
                if "ahci" not in controllers:
                    cmd += [
                        "-device",
                        "ich9-ahci,id=ahci"
                    ]
                    controllers.add("ahci")

                cmd += [
                    "-drive",
                    f"file={disk_path},if=none,id=disk{disk_id}",
                    "-device",
                    (
                        f"ide-hd,drive=disk{disk_id},"
                        f"bus=ahci.{disk_id}"
                    )
                ]

            else:
                raise ValueError(
                    f"Unsupported storage bus: {disk_bus}"
                )

        empty_values = {"Empty", "", " ", "empty", None}

        for media in self.config.get("media") or []:
            media_type = media.get("type")
            media_path = media.get("path")
            media_id = media.get("id")

            if media_type == "CD-ROM":
                if media_path not in empty_values:
                    media_path = os.path.normpath(str(media_path))

                    if not os.path.exists(media_path):
                        raise FileNotFoundError(
                            f"CD-ROM path does not exist: {media_path}"
                        )

                    cmd += [
                        "-drive",
                        (
                            f"media=cdrom,file={media_path},"
                            f"if=ide,id=cdrom{media_id}"
                        )
                    ]
                else:
                    cmd += [
                        "-drive",
                        f"media=cdrom,if=ide,id=cdrom{media_id}"
                    ]

            elif media_type == "Floppy":
                if media_path not in empty_values:
                    media_path = os.path.normpath(str(media_path))

                    if not os.path.exists(media_path):
                        raise FileNotFoundError(
                            f"Floppy path does not exist: {media_path}"
                        )

                    cmd += [
                        "-drive",
                        (
                            f"file={media_path},"
                            f"if=floppy,id=floppy{media_id}"
                        )
                    ]
                else:
                    cmd += [
                        "-drive",
                        f"if=floppy,id=floppy{media_id}"
                    ]

        video = self.config.get("video") or {}
        video_model = video.get("model", "std")

        cmd += ["-vga", str(video_model)]

        if video.get("connection") == "VNC":
            if self.vnc_port is None:
                raise ValueError(
                    "A VNC port was not assigned to the VM"
                )

            if self.vnc_port < 5900:
                raise ValueError(
                    "VNC port must be 5900 or greater"
                )

            cmd += [
                "-vnc",
                f":{self.vnc_port - 5900}"
            ]

        self._add_audio_args(cmd)

        #if audio and audio != "None":
        #    cmd += [
        #        "-audio",
        #        f"driver=dsound,model={audio}"
        #    ]

        # Modern replacement for the removed/deprecated -usbdevice tablet.
        cmd += [
            "-device",
            "qemu-xhci,id=usb",
            "-device",
            "usb-tablet,bus=usb.0"
        ]

        boot_order = self.config.get("boot")
        if boot_order:
            cmd += ["-boot", str(boot_order)]

        extra_args = self.config.get("qargs")
        if extra_args:
            if isinstance(extra_args, list):
                cmd += [str(arg) for arg in extra_args]
            else:
                logging.warning(
                    "Ignoring qargs because it is not a list"
                )

        logging.debug(
            "Command generated: %s",
            subprocess.list2cmdline(cmd)
        )

        return cmd

    def _add_audio_args(self, cmd):
        audio_model = self.config.get("audio")
        if not audio_model or audio_model == "None":
            return

        audio_model = audio_model.lower()
        device_args = self.AUDIO_DEVICE_ARGS.get(audio_model)

        if not device_args:
            raise ValueError(f"Unsupported audio device: {audio_model}")

        cmd += ["-audiodev", f"dsound,id={self.AUDIO_BACKEND_ID}"]
        cmd += [
            arg.format(backend_id=self.AUDIO_BACKEND_ID)
            for arg in device_args
        ]

    def _detect_format(self, path):
        try:
            settings = QSettings("QEMUWin", "QEMUWin")
            qemu_path = settings.value("qemu/path")

            if qemu_path:
                qemu_img = os.path.join(
                    str(qemu_path),
                    "qemu-img.exe"
                )
            else:
                qemu_img = "qemu-img.exe"

            result = subprocess.run(
                [qemu_img, "info", path],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                check=False
            )

            for line in result.stdout.splitlines():
                if "file format" in line:
                    return line.split(":", 1)[1].strip()

        except Exception:
            logging.exception(
                "Failed to detect disk format for %s",
                path
            )

        return "raw"

    def _handle_qmp_event(self, event):
        event_name = event.get("event")
        logging.debug("Received QMP event: %s", event_name)

        if event_name == "SHUTDOWN":
            self._set_state(VMState.STOPPED)

        elif event_name == "STOP":
            self._set_state(VMState.PAUSED)

        elif event_name == "RESUME":
            self._set_state(VMState.RUNNING)

    def restore_vm(self):
        data = self.metadata.load(self.name)

        if not data:
            self._set_state(VMState.STOPPED)
            return None

        try:
            qmp_port = data["qmp_port"]
            logging.debug("Connecting to QMP:%s", qmp_port)

            qmp = QMPClient("127.0.0.1", qmp_port)
            qmp.connect()

            status = qmp.execute("query-status")
            run_state = status["return"]["status"]

            self.qmp = qmp
            self.qmp_port = qmp_port

            if run_state == "running":
                self._set_state(VMState.RUNNING)
                active_state = "running"

            elif run_state == "paused":
                self._set_state(VMState.PAUSED)
                active_state = "paused"

            else:
                self._set_state(VMState.STOPPED)
                active_state = "stopped"

            self.qmp.add_event_listener(self._handle_qmp_event)

            return {
                "name": data["name"],
                "state": active_state
            }

        except Exception:
            logging.exception(
                "Failed to restore VM %s",
                self.name
            )

        self.metadata.delete(self.name)
        self._set_state(VMState.STOPPED)

        return None

    def _monitor(self):
        if not self.process:
            return

        stdout, stderr = self.process.communicate()
        code = self.process.returncode

        time.sleep(2)

        if self.state not in (
            VMState.STOPPING,
            VMState.STOPPED
        ):
            if code == 0:
                if self.killed:
                    self._set_state(VMState.KILLED)
                    self.killed = False
                else:
                    self._set_state(VMState.STOPPED)
            else:
                self._set_state(VMState.ERROR)

        self.metadata.delete(self.name)

        if self.on_stopped:
            self.on_stopped(self.name)

        if stdout:
            logging.debug("QEMU stdout:\n%s", stdout)

        if code != 0:
            logging.error(
                "QEMU exited with code %s\n%s",
                code,
                stderr
            )
        elif stderr:
            logging.warning("QEMU stderr:\n%s", stderr)

    def _terminate_failed_start(self):
        if self.qmp:
            try:
                self.qmp.close()
            except Exception:
                logging.exception(
                    "Failed to close QMP connection"
                )

            self.qmp = None

        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                logging.exception(
                    "Failed to terminate QEMU process"
                )

    def pause(self):
        if self.qmp:
            try:
                self.qmp.pause()
            except Exception as error:
                raise RuntimeError(
                    "Failed to pause VM"
                ) from error

    def resume(self):
        if self.qmp:
            try:
                self.qmp.resume()
            except Exception as error:
                raise RuntimeError(
                    "Failed to resume VM"
                ) from error

    def change_media(self, media):
        if not self.qmp:
            return

        try:
            media_type = media.get("type")
            media_id = media.get("id")
            path = media.get("path")

            if media_type == "CD-ROM":
                device = f"cdrom{media_id}"

            elif media_type == "Floppy":
                device = f"floppy{media_id}"

            else:
                raise ValueError(
                    f"Unsupported removable media type: {media_type}"
                )

            response = self.qmp.change_medium(device, path)

            if "error" in response:
                description = response["error"].get(
                    "desc",
                    "Unknown QMP error"
                )
                raise RuntimeError(description)

        except Exception as error:
            raise RuntimeError(
                "Failed to change VM media"
            ) from error

        from backend.config_manager import ConfigManager

        config_manager = ConfigManager()
        new_media = []

        for existing_media in self.config["media"]:
            if (
                existing_media["type"] == media_type
                and int(existing_media["id"]) == int(media_id)
            ):
                existing_media["path"] = path

            new_media.append(existing_media)

        self.config["media"] = new_media
        config_manager.save_vm(self.name, self.config)

    def stop(self):
        if self.qmp:
            try:
                self.qmp.shutdown()
            except Exception as error:
                raise RuntimeError(
                    "Failed to send shutdown signal to VM"
                ) from error

    def quit(self):
        if self.qmp:
            try:
                self.killed = True
                self.qmp.quit()
            except Exception as error:
                raise RuntimeError(
                    "Failed to end VM process"
                ) from error
