. "$(dirname "$0")/_comun.sh"
cmd "powershell.exe -NoProfile -Command 'Get-CimInstance Win32_Processor | Format-List Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,L2CacheSize,L3CacheSize' | tr -d '\r' | sed '/^\$/d'"
