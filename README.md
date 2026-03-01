# QEMUWin
### A simple GUI for QEMU in Windows based in Python
   
QEMU is known for its versatility in creating virtual machines, especially on Linux. However, it's also a viable option on Windows for creating virtual machines with specific hardware.   

On Linux, [virt-manager](https://github.com/virt-manager/virt-manager) is the most popular option for managing VMs, offering an intuitive and easy-to-use GUI. However, Windows lacks this feature, making QEMU primarily an option for advanced users... until now.   
   
QEMUWin is a new, simple-to-use Python-based interface for Windows that promises to bring virt-manager features to Windows.   

This is still a work in progress. See [How to support](#how-to-support) to support the project
   
---
   
## GUI v1:

This is finally the first version of the project. Most of the initial ideas are in this release

## How to use:  

Download the application through the [releases](https://github.com/ChileCris2011/QEMUWin/releases) tab, install it and execute it!

### First use: 

When you open the program for the first time, it will ask for the QEMU path. This is the directory that contains at least `qemu-system-x86_64.exe` and `qemu-img.exe`, and all the executables for the other architectures.   

If you installed QEMU through MSYS2 using UCRT64 (as described in the QEMU for Windows installation guide), the default path (for x64) is `C:\msys64\ucrt64\bin`, which also contains all the programs installed by UCRT64.   

If you don't specify a directory, it will try to find the program in the system PATH. By default, this should result in an error since the installation is not automatically added to the system PATH.

### Creating a virtual machine:

Pressing the "New" button will launch the VM creation wizard. There, you can assign a name, hardware, and devices. The configuration is saved to a JSON file in the application root directory.

### Running a virtual machine:

To start your virtual machine, press "Start". For now, the program only launches the VM and uses the QEMU interface, monitoring it via QMP (QEMU Machine Protocol). You can specify an external viewer using the [additional QEMU flags](#qemu-flags) (advanced).

### Editing a virtual machine:

You can edit a VM by pressing the "Edit" button in the interface. There, you can modify the hardware, change disks and media, add more devices, and modify QEMU flags.

### QEMU Flags

For more advanced use of your VM, you can use QEMU flags. These are commands that are added to the end of the VM startup command. You can find a list of these flags in the [official QEMU documentation.](https://www.qemu.org/docs/master/system/invocation.html)   
   
---

## How to support

If you know QEMU/Python and want to support this project, you can [create a new branch](https://github.com/ChileCris2011/QEMUWin/branches), make all the changes you deem necessary, and create a pull request.   

You can also [open an Issue](https://github.com/ChileCris2011/QEMUWin/issues/new?template=feature_request.md) with your suggested feature and I will review it as soon as posible!

## Issues and bugs

This is still a work in progress, and with only me working on it, there might be a bug or two. If you find one, you can [open an Issue](https://github.com/ChileCris2011/QEMUWin/issues/new?template=bug_report.md) and I'll work on it!