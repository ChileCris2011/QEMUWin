# QEMUWin
### A simple GUI for QEMU in Windows based in Python
   
QEMU is known for its versatility in creating virtual machines, especially on Linux. However, it's also a viable option on Windows for creating virtual machines with specific hardware.   

On Linux, [virt-manager](https://github.com/virt-manager/virt-manager) is the most popular option for managing VMs, offering an intuitive and easy-to-use GUI. However, Windows lacks this feature, making QEMU primarily an option for advanced users... until now.   
   
QEMUWin *will be* a new, simple-to-use Python-based interface for Windows that promises to bring virt-manager features to Windows.   
   
---
   
### Initial release:
This first release only includes the foundation of the project: A simple Python program to run and monitor a QEMU VMs.   
   
You still need to manually configure the virtual machine via a JSON file, and it only supports the x86_64 architecture.   
   
#### How to use:
This first release is still not meant to general use, but here are the steps to configure a QEMU VM:   

1. Create a JSON file in `data/vms`.
   This file must contain at least:  
    - VM name
    - RAM Memory (in MB)
    - CPU cores
    - Virtual Disk Path   

   Optionally, it can contain:
    - Machine type (defaults to 'pc')
    - Enable WHPX (defaults to False)
    - ISO Path
    - QMP port (defaults to localhost:4444)
    - VNC port (defaults to localhost:5900)
    - Custom QEMU flags

   Here's an example of a config file:
   ```json
   {
        "name": "TestVM",
        "memory_mb": 512,
        "cpu_cores": 1,
        "disk_path": ".\\virt\\disk.qcow2",
        "iso_path": ".\\virt\\install.iso",
        "machine_type": "pc",
        "enable_whpx": false,
        "custom_flags": [
            "-boot",
            "order=dc"
        ]
    }
    ```
2. Execute `main.py`   

   As long as the configuration file(s) are in `data/vms`, the program will detect the configuration and ask the user which one to use. Enter the number of the VM and that's it!