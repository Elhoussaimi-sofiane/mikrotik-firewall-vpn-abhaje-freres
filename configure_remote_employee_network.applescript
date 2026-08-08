set remoteVMID to "684845DD-970E-4164-9A56-49223FE15BDE"

tell application "UTM"
	set remoteVM to virtual machine id remoteVMID
	if status of remoteVM is not stopped then error "Remote-Employee-Test must be stopped before changing its network."

	update configuration remoteVM with {network interfaces:{{index:0, hardware:"virtio-net-pci", mode:shared, address:""}}}

	return (id of remoteVM) & tab & (name of remoteVM) & tab & (status of remoteVM as text)
end tell
