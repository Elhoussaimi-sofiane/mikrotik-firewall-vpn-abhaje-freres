set sourceVMID to "6115A353-81D6-4275-8CDD-1901FD0B44B8"
set newVMName to "R2-Branch"

tell application "UTM"
	set existingNames to name of virtual machines
	if newVMName is in existingNames then error "A UTM virtual machine named '" & newVMName & "' already exists; refusing to modify it."

	set sourceVM to virtual machine id sourceVMID
	if status of sourceVM is not stopped then error "R1-HQ must be stopped before duplication."

	duplicate sourceVM with properties {configuration:{name:newVMName, notes:"Independent MikroTik branch router for site-to-site VPN testing"}}

	repeat 120 times
		if newVMName is in (name of virtual machines) then exit repeat
		delay 1
	end repeat
	if newVMName is not in (name of virtual machines) then error "UTM did not finish creating R2-Branch."

	set copiedVM to first virtual machine whose name is newVMName
	return (id of copiedVM) & tab & (name of copiedVM) & tab & (status of copiedVM as text)
end tell
