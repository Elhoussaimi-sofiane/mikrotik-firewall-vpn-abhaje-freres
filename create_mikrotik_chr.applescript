set vmName to "MikroTik CHR Automated"
set sourcePath to "/Users/sofiane/Desktop/chr-7.22.1-arm64.qcow2"

set sourceFile to POSIX file sourcePath
set sourceInfo to info for sourceFile
if (size of sourceInfo) is 0 then error "Source image is Zero KB; refusing to create a VM."

tell application "UTM"
	set existingNames to name of virtual machines
	if vmName is in existingNames then error "A UTM virtual machine named '" & vmName & "' already exists; refusing to modify it."

	set vmConfig to {name:vmName, architecture:"aarch64", machine:"virt", memory:2048, cpu cores:2, hypervisor:true, uefi:true, drives:{{removable:false, interface:VirtIO, source:sourceFile}}}
	set newVM to make new virtual machine with properties {backend:qemu, configuration:vmConfig}
	return (id of newVM) & tab & (name of newVM) & tab & (status of newVM as text)
end tell
