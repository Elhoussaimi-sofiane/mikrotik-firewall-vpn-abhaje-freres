set vmID to "6115A353-81D6-4275-8CDD-1901FD0B44B8"
set sourcePath to "/Users/sofiane/Desktop/VELORA noire/chr-7.22.1-arm64.img"

set sourceFile to POSIX file sourcePath
set sourceInfo to info for sourceFile
if (size of sourceInfo) is 0 then error "Replacement source image is Zero KB; refusing to change the VM."

tell application "UTM"
	set targetVM to virtual machine id vmID
	update configuration targetVM with {drives:{{removable:false, interface:VirtIO, source:sourceFile}}}
	return (id of targetVM) & tab & (name of targetVM)
end tell
