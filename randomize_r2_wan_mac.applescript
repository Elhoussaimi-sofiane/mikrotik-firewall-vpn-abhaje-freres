set r2VMID to "793F2353-DD98-4970-9AF9-B436A69C5CA3"

tell application "UTM"
	set r2VM to virtual machine id r2VMID
	if status of r2VM is not stopped then error "R2-Branch must be stopped before changing its WAN MAC address."

	update configuration r2VM with {network interfaces:{{index:0, hardware:"virtio-net-pci", mode:shared, address:""}}}

	return (id of r2VM) & tab & (name of r2VM) & tab & (status of r2VM as text)
end tell
