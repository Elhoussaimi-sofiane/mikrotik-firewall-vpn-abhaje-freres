set vmID to "6115A353-81D6-4275-8CDD-1901FD0B44B8"
set driveID to "90658DD9-AA4D-4871-95FD-3206E272C2E3"

tell application "UTM"
	set targetVM to virtual machine id vmID
	update configuration targetVM with {drives:{{id:driveID, interface:VirtIO}}}
	return (id of targetVM) & tab & (name of targetVM)
end tell
