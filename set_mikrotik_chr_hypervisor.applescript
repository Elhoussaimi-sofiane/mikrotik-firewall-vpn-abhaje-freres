set vmID to "6115A353-81D6-4275-8CDD-1901FD0B44B8"

tell application "UTM"
	set targetVM to virtual machine id vmID
	update configuration targetVM with {hypervisor:false}
	return (id of targetVM) & tab & (name of targetVM)
end tell
