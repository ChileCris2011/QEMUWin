# v1.1.0  
**Second release of QEMUWin. All issues are solved, plus:**

- New app versioning: App version shows on 'About' page, log file and installer. Non-release versions have their own identifier.
- VM config files updated to V2. This process is automatic, and original files are saves in `<app_root>/vms/backup`.
- Device list updated! Please review if your device is still supported:  
    Removed devices: Audio: `intel-hda`, `ich9-intel-hda`, `hda-duplex`, `usb-audio`, `virtio-sound` (renamed to `virtio`). Video: `vga`.
- VM config file's names are normalized before being saved, preventing unallowed characters on file names.
- The QEMU executable's path now is used, and fallbacks to system PATH if not configured ([#12](https://github.com/ChileCris2011/QEMUWin/issues/12)).
- New VM restoring method: Started vms should restore their state if the app closes.
- VM now waits properly for QMP when using cpu type `host` (thanks to [dmnjess](https://github.com/dmnjess) for this change ([#16](https://github.com/ChileCris2011/QEMUWin/pull/16))).
- Better QMP handling in general.
- New pause/play buttons on UI to pause and resume the VM.
- Double-clicking the VM name now starts it.
- VM now automatically selects USB Tablet for absolute mouse movement if available.
- New graphical memory bar on creating and editing.
- Minimum assigned RAM changes to 1 MiB ([#14](https://github.com/ChileCris2011/QEMUWin/issues/14)).
- Moved QEMU Logs settings to a new 'Logging' page.
- Added a new setting to change the log level of the logging file.
- New logging messages for INFO and DEBUG levels.
- New 'Boot from...' setting, to select boot medium (Hard Drive, CD-ROM, Floppy).
- Error dialog now centers when un/expanded.
- New animation on About page (thanks to [dmnjess](https://github.com/dmnjess) for this change ([#16](https://github.com/ChileCris2011/QEMUWin/pull/16))).
- `QMPPortManager` class renamed to `PortManager`, as it will be used to manage general ports.
- `PortManager` saves used ports
- Major changes to QEMU command generation
- New media change funcion (unused, by now...)
- All media now has an identifier (Starting from 0, for every VM)

# v1.0.2 
**First version of QEMUWin! Most of the initial ideas are in this release**