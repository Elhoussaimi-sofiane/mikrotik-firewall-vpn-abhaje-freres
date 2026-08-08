set sourceVMID to "BAF1C90D-0FF6-4299-AC3B-A6015945D8F2"
set newVMName to "Remote-Employee-Test"

tell application "UTM"
	set existingNames to name of virtual machines
	if newVMName is in existingNames then error "A UTM virtual machine named '" & newVMName & "' already exists; refusing to modify it."

	set sourceVM to virtual machine id sourceVMID
	if status of sourceVM is not stopped then error "Source VM must be stopped before duplication."

	duplicate sourceVM with properties {configuration:{name:newVMName, notes:"External/WAN-side Ubuntu employee used only for WireGuard and firewall testing"}}

	repeat 120 times
		if newVMName is in (name of virtual machines) then exit repeat
		delay 1
	end repeat
	if newVMName is not in (name of virtual machines) then error "UTM did not finish creating the duplicate."
	set copiedVM to first virtual machine whose name is newVMName

	update configuration copiedVM with {network interfaces:{{index:0, hardware:"virtio-net-pci", mode:shared, address:""}}}

	return (id of copiedVM) & tab & (name of copiedVM) & tab & (status of copiedVM as text)
end tell
