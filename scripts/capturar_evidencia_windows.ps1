# Saca las capturas de evidencia de las Partes 1 y 4 (equipo, compilación, amdahl y gustafson)
# en Windows nativo. Cada comando corre en una ventana de consola visible y, al terminar,
# se guarda una captura de esa ventana en evidencia/nina/ con el nombre que espera
# scripts/armar_evidencia_lab12.py.
#
# Uso (PowerShell, desde la raíz del repo):
#     powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia_windows.ps1
#
# No sobrescribe nada de results/: las corridas solo se muestran en pantalla.
# Antes: laptop conectada, apps cerradas y no usar la compu mientras corre (~3-5 min).
param(
  [string]$Exe = 'build\lab12.exe',
  [int]$Pmax = 8,
  [string]$Salida = 'evidencia\nina'
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
New-Item -ItemType Directory -Force $Salida | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class Ventana {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  public struct RECT { public int L, T, R, B; }
}
"@
# Con la pantalla escalada (125 %, 150 %...) sin esto la captura sale recortada.
[Ventana]::SetProcessDPIAware() | Out-Null

function Capturar([string]$Nombre, [string[]]$Comandos, [int]$Lineas = 30, [int]$Columnas = 100) {
  $titulo = 'Lab12 evidencia ' + [guid]::NewGuid().ToString('N').Substring(0, 8)
  $marca = Join-Path $env:TEMP ($titulo -replace ' ', '_')
  # Cada comando se muestra con un prompt y luego se ejecuta.
  $cuerpo = ($Comandos | ForEach-Object {
      $c = $_ -replace "'", "''"
      "Write-Host -NoNewline -ForegroundColor Green 'PS> '; Write-Host '$c'; $_"
    }) -join "`n"
  $script = @"
`$Host.UI.RawUI.WindowTitle = '$titulo'
Set-Location '$Root'
try {
  `$raw = `$Host.UI.RawUI
  `$raw.BufferSize = New-Object Management.Automation.Host.Size($Columnas, 3000)
  `$max = `$raw.MaxPhysicalWindowSize
  `$raw.WindowSize = New-Object Management.Automation.Host.Size([Math]::Min($Columnas, `$max.Width), [Math]::Min($Lineas, `$max.Height))
} catch {}
$cuerpo
New-Item -ItemType File '$marca' | Out-Null
Start-Sleep -Seconds 100000
"@
  $ps1 = "$marca.ps1"
  [IO.File]::WriteAllText($ps1, $script, [Text.Encoding]::UTF8)
  $p = Start-Process conhost.exe -PassThru -ArgumentList "cmd.exe /c mode con: cols=$Columnas lines=$Lineas & powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$ps1`""
  $t0 = Get-Date
  while (-not (Test-Path $marca)) {
    if (((Get-Date) - $t0).TotalMinutes -gt 20) { throw "La ventana de $Nombre no terminó en 20 minutos" }
    Start-Sleep -Milliseconds 500
  }
  Start-Sleep -Milliseconds 800
  $w = Get-Process | Where-Object { $_.MainWindowTitle -like "$titulo*" } | Select-Object -First 1
  if (-not $w) { throw "No encontré la ventana de $Nombre" }
  $r = New-Object Ventana+RECT
  [Ventana]::GetWindowRect($w.MainWindowHandle, [ref]$r) | Out-Null
  $bmp = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
  $g = [Drawing.Graphics]::FromImage($bmp); $hdc = $g.GetHdc()
  [Ventana]::PrintWindow($w.MainWindowHandle, $hdc, 2) | Out-Null
  $g.ReleaseHdc($hdc); $g.Dispose()
  $png = Join-Path $Salida "$Nombre.png"
  $bmp.Save($png, [Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  Stop-Process -Id $w.Id -Force -ErrorAction SilentlyContinue
  Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
  Remove-Item $marca, $ps1 -ErrorAction SilentlyContinue
  Write-Host ("  -> {0}  ({1:N0} s)" -f $png, ((Get-Date) - $t0).TotalSeconds)
}

Write-Host '1/4 Datos del equipo'
Capturar 'nina_01_equipo' @(
  'Get-CimInstance Win32_Processor | Format-List Name,NumberOfCores,NumberOfLogicalProcessors',
  '(Get-CimInstance Win32_Battery).BatteryStatus  # 2 = conectada a la corriente'
) 18 100

Write-Host '2/4 Compilación'
Capturar 'nina_02_make' @(
  'gcc --version | Select-Object -First 1',
  "gcc -O2 -std=c11 -Wall -Wextra -Werror -fopenmp lab12_speedup.c -o $Exe -lm",
  "Get-Item $Exe | Format-Table Name,Length,LastWriteTime"
) 16 100

Write-Host '3/4 amdahl (5 fracciones)'
foreach ($fp in '1.00', '0.95', '0.90', '0.75', '0.50') {
  $tag = [int]([double]$fp * 100)
  Capturar "nina_03_amdahl_fp$tag" @("& .\$Exe amdahl 400000 $fp $Pmax 2>`$null") ($Pmax + 8) 100
}

Write-Host '4/4 gustafson'
Capturar 'nina_04_gustafson' @("& .\$Exe gustafson 100000 20000 $Pmax 2>`$null") ($Pmax + 8) 100

Write-Host "Listo. Ahora: python scripts\armar_entrega.py"
