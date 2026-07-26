<#
.SYNOPSIS
    Levanta, recarga y detiene el entorno de desarrollo de VYNTIA (Django + Vite).

.DESCRIPTION
    Un solo punto de entrada para el ciclo de desarrollo local. Se encarga de los
    pasos que hay que recordar cada vez y que, si se olvidan, fallan de forma poco
    obvia:

      * Carga `apps/api/.env` en el entorno del proceso. Los settings leen las
        credenciales con `os.environ.get("DB_PASSWORD", "postgres")` y nada carga
        el .env automaticamente, asi que sin este paso Django usa la contrasena
        por defecto, la autenticacion falla, y PostgreSQL responde en locale
        espanol (Spanish_Peru.1252) con un mensaje que psycopg2 no logra decodificar
        como UTF-8. El sintoma es un `UnicodeDecodeError` que no menciona la
        contrasena por ningun lado.
      * Crea `apps/api/logs/` si falta (su ausencia rompe el dictConfig de logging
        al arrancar, con un `ValueError: Unable to configure handler 'file'`).
      * Recuerda que arranco cada servidor, de modo que `stop` solo mata lo suyo y
        nunca un proceso ajeno que este ocupando el mismo puerto.

.NOTES
    LIMITACION CONOCIDA - no redirijas la salida de 'start':

        dev.cmd start > salida.log     # no retorna hasta que mueran los servidores
        dev.cmd start | Out-Null       # idem

    Los procesos que se lanzan heredan un duplicado del handle de escritura de la
    tuberia, asi que esta no se cierra al terminar el script y quien lee se queda
    esperando. Redirigirles stdin/stdout/stderr a archivos no lo evita. Las demas
    acciones (stop, status, logs, reload) se pueden redirigir sin problema.

    Uso normal: 'dev.cmd start' de forma interactiva y despues 'dev.cmd logs'.

.PARAMETER Action
    start    Levanta backend y frontend (por defecto).
    reload   Reinicia solo lo que este corriendo. Alias: restart.
    stop     Detiene lo que este script levanto.
    status   Muestra que hay arriba y responde.
    logs     Muestra los logs (usar -Follow para seguirlos en vivo).
    seed     Carga los datos demo (seed_demo_pro) con el .env ya exportado.

.EXAMPLE
    .\dev.cmd
    Levanta todo y deja las URLs en pantalla.

.EXAMPLE
    .\dev.cmd reload
    Reinicia los servidores tras un cambio que Django o Vite no recargaron solos.

.EXAMPLE
    .\dev.cmd start -NoWeb
    Solo el backend, para trabajar contra la API con curl o pytest.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'reload', 'restart', 'stop', 'status', 'logs', 'seed')]
    [string]$Action = 'start',

    # El proxy de Vite apunta fijo a 127.0.0.1:8000 (apps/web/vite.config.ts), asi
    # que cambiar este puerto deja al frontend sin API salvo que se ajuste alli.
    [int]$ApiPort = 8000,
    [int]$WebPort = 5173,

    # Toma el puerto de la API aunque lo ocupe un proceso que no arranco este script.
    [switch]$Force,
    [switch]$NoApi,
    [switch]$NoWeb,
    [switch]$Open,
    [switch]$Follow
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Rutas ────────────────────────────────────────────────────────────────────

$Root    = Split-Path -Parent $PSScriptRoot
$ApiDir  = Join-Path $Root 'apps\api'
$WebDir  = Join-Path $Root 'apps\web'
$DevDir  = Join-Path $Root '.dev'
$LogDir  = Join-Path $DevDir 'logs'
$StateFile = Join-Path $DevDir 'state.json'

# El venv y el .env no se versionan, asi que en un git worktree no existen. Se
# localiza el checkout principal para reutilizar los suyos en vez de obligar a
# duplicarlos en cada worktree.
function Get-MainCheckout {
    try {
        $common = & git -C $Root rev-parse --git-common-dir 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $common) { return $null }
        $resolved = Resolve-Path -LiteralPath (Join-Path $Root $common) -ErrorAction SilentlyContinue
        if (-not $resolved) { $resolved = Resolve-Path -LiteralPath $common -ErrorAction SilentlyContinue }
        if (-not $resolved) { return $null }
        $main = Split-Path -Parent $resolved.Path
        if ($main -and $main -ne $Root) { return $main }
        return $null
    } catch { return $null }
}

$MainRoot = Get-MainCheckout

# Devuelve la primera ruta que exista: primero la local, luego la del checkout
# principal. $null si no hay ninguna.
function Resolve-Shared([string]$Relative) {
    $local = Join-Path $Root $Relative
    if (Test-Path $local) { return $local }
    if ($MainRoot) {
        $shared = Join-Path $MainRoot $Relative
        if (Test-Path $shared) { return $shared }
    }
    return $null
}

$EnvFile = Join-Path $ApiDir '.env'

# ─── Salida ───────────────────────────────────────────────────────────────────

function Write-Step($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Warn2($msg){ Write-Host "  !   $msg" -ForegroundColor Yellow }
function Write-Err2($msg) { Write-Host "  X   $msg" -ForegroundColor Red }
function Write-Title($msg) {
    Write-Host ''
    Write-Host "VYNTIA dev - $msg" -ForegroundColor White
    Write-Host ('-' * 62) -ForegroundColor DarkGray
}

# ─── Utilidades ───────────────────────────────────────────────────────────────

# Se prueban ambas familias: Vite escucha en ::1 (localhost IPv6) y Django en
# 127.0.0.1, asi que sondear una sola da falsos negativos.
function Test-Port([int]$Port) {
    foreach ($addr in @('127.0.0.1', '::1')) {
        $client = [System.Net.Sockets.TcpClient]::new()
        try {
            $task = $client.ConnectAsync($addr, $Port)
            if ($task.Wait(400) -and $client.Connected) { return $true }
        } catch { }
        finally { $client.Dispose() }
    }
    return $false
}

function Get-PortOwner([int]$Port) {
    $conn = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
            Select-Object -First 1
    if (-not $conn) { return $null }
    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
    [pscustomobject]@{
        Pid  = $conn.OwningProcess
        Name = if ($proc) { $proc.ProcessName } else { 'desconocido' }
    }
}

function Get-FreePort([int]$Start, [int]$Tries = 15) {
    for ($p = $Start; $p -lt $Start + $Tries; $p++) {
        if (-not (Test-Port $p)) { return $p }
    }
    throw "No se encontro un puerto libre entre $Start y $($Start + $Tries)."
}

# Django con autoreload y Vite lanzan procesos hijos; matar solo al padre los deja
# huerfanos reteniendo el puerto.
function Stop-Tree([int]$ProcId) {
    if (-not $ProcId) { return $false }
    if (-not (Get-Process -Id $ProcId -ErrorAction SilentlyContinue)) { return $false }
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcId" -ErrorAction SilentlyContinue
    foreach ($c in $children) { Stop-Tree ([int]$c.ProcessId) | Out-Null }
    try { Stop-Process -Id $ProcId -Force -ErrorAction Stop } catch { }
    Start-Sleep -Milliseconds 250
    # El exito se mide por ausencia, no por que nuestro Stop-Process no fallara:
    # matar a un hijo suele tumbar al padre, y entonces el kill del padre lanza
    # "proceso no encontrado" pese a que el arbol si quedo abajo.
    return -not (Get-Process -Id $ProcId -ErrorAction SilentlyContinue)
}

function Import-DotEnv([string]$Path) {
    if (-not (Test-Path $Path)) {
        Write-Warn2 "No existe $Path - Django usara los valores por defecto y probablemente falle al conectar."
        return 0
    }
    $count = 0
    foreach ($raw in Get-Content -LiteralPath $Path -Encoding utf8) {
        $line = $raw.TrimEnd("`r").Trim()
        if (-not $line -or $line.StartsWith('#')) { continue }
        if ($line.StartsWith('export ')) { $line = $line.Substring(7).Trim() }
        $i = $line.IndexOf('=')
        if ($i -lt 1) { continue }
        $key = $line.Substring(0, $i).Trim()
        $val = $line.Substring($i + 1).Trim()
        # Solo se quitan las comillas si envuelven todo el valor.
        if ($val.Length -ge 2 -and (
                ($val.StartsWith('"')  -and $val.EndsWith('"')) -or
                ($val.StartsWith("'")  -and $val.EndsWith("'")))) {
            $val = $val.Substring(1, $val.Length - 2)
        }
        Set-Item -Path "Env:$key" -Value $val
        $count++
    }
    return $count
}

function Get-Python {
    $venv = Resolve-Shared '.venv\Scripts\python.exe'
    if ($venv) {
        if ($venv -notlike "$Root*") { Write-Step "venv del checkout principal: $venv" }
        return $venv
    }
    $sys = Get-Command python -ErrorAction SilentlyContinue
    if ($sys) {
        Write-Warn2 "No se encontro un venv - se usara el python del PATH ($($sys.Source))."
        return $sys.Source
    }
    throw "No se encontro Python. Crea el venv:  python -m venv .venv  y luego  pip install -e `"apps/api[dev]`""
}

function Read-State {
    if (-not (Test-Path $StateFile)) { return $null }
    try { Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json } catch { $null }
}

function Save-State($state) {
    New-Item -ItemType Directory -Force -Path $DevDir | Out-Null
    $state | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StateFile -Encoding utf8
}

function Clear-State { if (Test-Path $StateFile) { Remove-Item -LiteralPath $StateFile -Force } }

# Se les da un archivo vacio como stdin para que no consuman la entrada de la
# consola. No se usa 'NUL' porque Start-Process lo resuelve como ruta relativa
# al working directory y falla.
function Get-NullInput {
    New-Item -ItemType Directory -Force -Path $DevDir | Out-Null
    $f = Join-Path $DevDir 'null.in'
    if (-not (Test-Path $f)) { Set-Content -LiteralPath $f -Value '' -NoNewline }
    return $f
}

# Un PID guardado solo cuenta si sigue vivo Y es del ejecutable que esperamos: los
# PID se reciclan, y matar a ciegas el numero guardado puede acabar con otra cosa.
function Test-TrackedProcess($ProcId, [string]$ExpectedName) {
    if (-not $ProcId) { return $false }
    $proc = Get-Process -Id $ProcId -ErrorAction SilentlyContinue
    if (-not $proc) { return $false }
    return $proc.ProcessName -like $ExpectedName
}

function Wait-Port([int]$Port, [int]$TimeoutSec = 45) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port $Port) { return $true }
        Start-Sleep -Milliseconds 400
    }
    return $false
}

# ─── Acciones ─────────────────────────────────────────────────────────────────

function Invoke-Stop {
    $state = Read-State
    if (-not $state) { Write-Step 'No hay nada registrado por este script.'; return }

    $stopped = 0
    foreach ($svc in @(
        @{ Key = 'apiPid'; Name = 'python'; Label = 'backend' },
        @{ Key = 'webPid'; Name = 'node';   Label = 'frontend' })) {

        $procId = if ($state.PSObject.Properties.Name -contains $svc.Key) { $state.($svc.Key) } else { $null }
        if (Test-TrackedProcess $procId $svc.Name) {
            if (Stop-Tree $procId) { Write-Ok "$($svc.Label) detenido (PID $procId)"; $stopped++ }
            else { Write-Warn2 "No se pudo detener el $($svc.Label) (PID $procId)" }
        } elseif ($procId) {
            Write-Step "El $($svc.Label) (PID $procId) ya no estaba corriendo."
        }
    }
    Clear-State
    if ($stopped -eq 0) { Write-Step 'Nada que detener.' }
}

function Invoke-Start {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $state = Read-State
    $newState = [ordered]@{ apiPid = $null; webPid = $null; apiPort = $ApiPort; webPort = $WebPort }

    # ── Backend ──────────────────────────────────────────────────────────────
    if (-not $NoApi) {
        $owner = Get-PortOwner $ApiPort
        $ourApi = $state -and (Test-TrackedProcess ($state.apiPid) 'python')

        if ($owner -and $ourApi -and $owner.Pid -eq $state.apiPid) {
            Write-Ok "backend ya corriendo en :$ApiPort (PID $($owner.Pid)) - se reutiliza"
            $newState.apiPid = $state.apiPid
        }
        elseif ($owner -and -not $Force) {
            Write-Err2 "El puerto $ApiPort lo ocupa '$($owner.Name)' (PID $($owner.Pid)), que no arranco este script."
            Write-Host  "      El proxy de Vite apunta fijo a 127.0.0.1:8000, asi que no se puede mover el backend." -ForegroundColor DarkGray
            Write-Host  "      Usa -Force para tomarlo, o deten ese proceso a mano." -ForegroundColor DarkGray
            Write-Host ''
            # Salida limpia: un stack trace de PowerShell aqui solo tapa el mensaje
            # anterior, que es el que explica que hacer.
            exit 1
        }
        else {
            if ($owner -and $Force) {
                Write-Warn2 "-Force: deteniendo '$($owner.Name)' (PID $($owner.Pid)) que ocupaba :$ApiPort"
                Stop-Tree $owner.Pid | Out-Null
                Start-Sleep -Milliseconds 800
            }

            $python = Get-Python
            $envPath = Resolve-Shared 'apps\api\.env'
            if (-not $envPath) { $envPath = $EnvFile }
            $n = Import-DotEnv $envPath
            if ($n) { Write-Step "$n variables cargadas desde $envPath" }

            # Sin este directorio el dictConfig de logging revienta al arrancar.
            New-Item -ItemType Directory -Force -Path (Join-Path $ApiDir 'logs') | Out-Null

            Write-Step "arrancando backend en :$ApiPort ..."
            $proc = Start-Process -FilePath $python `
                -ArgumentList @('manage.py', 'runserver', "127.0.0.1:$ApiPort",
                                '--settings=vyntia.settings.development') `
                -WorkingDirectory $ApiDir -WindowStyle Hidden -PassThru `
                -RedirectStandardInput (Get-NullInput) `
                -RedirectStandardOutput (Join-Path $LogDir 'api.out.log') `
                -RedirectStandardError  (Join-Path $LogDir 'api.err.log')
            $newState.apiPid = $proc.Id

            if (Wait-Port $ApiPort 60) { Write-Ok "backend arriba - http://127.0.0.1:$ApiPort/api/docs/" }
            else {
                Write-Err2 "El backend no respondio en :$ApiPort. Ultimas lineas de .dev/logs/api.err.log:"
                Get-Content (Join-Path $LogDir 'api.err.log') -Tail 15 -ErrorAction SilentlyContinue |
                    ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }
            }
        }
    }

    # ── Frontend ─────────────────────────────────────────────────────────────
    if (-not $NoWeb) {
        $vite = Join-Path $WebDir 'node_modules\vite\bin\vite.js'
        if (-not (Test-Path $vite)) {
            Write-Err2 "Falta node_modules en apps/web. Ejecuta:  cd apps/web  &&  npm install"
        }
        else {
            $ourWeb = $state -and (Test-TrackedProcess ($state.webPid) 'node')
            $ownerWeb = Get-PortOwner $WebPort

            if ($ownerWeb -and $ourWeb -and $ownerWeb.Pid -eq $state.webPid) {
                Write-Ok "frontend ya corriendo en :$WebPort (PID $($ownerWeb.Pid)) - se reutiliza"
                $newState.webPid = $state.webPid
            }
            else {
                # A diferencia del backend, nada apunta a un puerto fijo del frontend,
                # asi que si esta ocupado simplemente se toma el siguiente libre.
                $port = Get-FreePort $WebPort
                if ($port -ne $WebPort) { Write-Warn2 ":$WebPort ocupado - se usara :$port" }
                $newState.webPort = $port

                Write-Step "arrancando frontend en :$port ..."
                $proc = Start-Process -FilePath 'node' `
                    -ArgumentList @($vite, '--port', $port, '--strictPort') `
                    -WorkingDirectory $WebDir -WindowStyle Hidden -PassThru `
                    -RedirectStandardInput (Get-NullInput) `
                    -RedirectStandardOutput (Join-Path $LogDir 'web.out.log') `
                    -RedirectStandardError  (Join-Path $LogDir 'web.err.log')
                $newState.webPid = $proc.Id

                if (Wait-Port $port 60) { Write-Ok "frontend arriba - http://localhost:$port/" }
                else {
                    Write-Err2 "Vite no respondio en :$port. Ultimas lineas de .dev/logs/web.err.log:"
                    Get-Content (Join-Path $LogDir 'web.err.log') -Tail 15 -ErrorAction SilentlyContinue |
                        ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }
                }
            }
        }
    }

    Save-State $newState

    Write-Host ''
    if ($newState.webPid) { Write-Host "  Frontend  http://localhost:$($newState.webPort)/" -ForegroundColor White }
    if ($newState.apiPid) { Write-Host "  API docs  http://127.0.0.1:$($newState.apiPort)/api/docs/" -ForegroundColor White }
    Write-Host "  Logs      .dev\logs\    (dev.cmd logs -Follow)" -ForegroundColor DarkGray
    Write-Host "  Detener   dev.cmd stop" -ForegroundColor DarkGray

    if ($Open -and $newState.webPid) { Start-Process "http://localhost:$($newState.webPort)/" }
}

function Invoke-Status {
    $state = Read-State
    if (-not $state) { Write-Step 'Sin registro de arranque (usa: dev.cmd start).' }

    foreach ($svc in @(
        @{ Key = 'apiPid'; PortKey = 'apiPort'; Name = 'python'; Label = 'backend ' },
        @{ Key = 'webPid'; PortKey = 'webPort'; Name = 'node';   Label = 'frontend' })) {

        $procId = if ($state -and $state.PSObject.Properties.Name -contains $svc.Key) { $state.($svc.Key) } else { $null }
        $port   = if ($state -and $state.PSObject.Properties.Name -contains $svc.PortKey) { $state.($svc.PortKey) } else { $null }
        $alive  = Test-TrackedProcess $procId $svc.Name
        $listen = if ($port) { Test-Port $port } else { $false }

        if ($alive -and $listen) { Write-Ok    "$($svc.Label) PID $procId escuchando en :$port" }
        elseif ($alive)          { Write-Warn2 "$($svc.Label) PID $procId vivo pero :$port no responde" }
        elseif ($listen)         { Write-Warn2 "$($svc.Label) :$port ocupado por otro proceso ($((Get-PortOwner $port).Name))" }
        else                     { Write-Step  "$($svc.Label) detenido" }
    }
}

function Invoke-Logs {
    if (-not (Test-Path $LogDir)) { Write-Step 'Todavia no hay logs.'; return }
    $files = Get-ChildItem $LogDir -Filter *.log | Sort-Object Name
    if (-not $files) { Write-Step 'Todavia no hay logs.'; return }

    if ($Follow) {
        # runserver escribe su salida por stderr, asi que ese es el archivo util.
        $target = $files | Where-Object Name -eq 'api.err.log' | Select-Object -First 1
        if (-not $target) { $target = $files[0] }
        Write-Step "siguiendo $($target.Name) (Ctrl+C para salir)"
        Write-Host "      Los demas estan en $LogDir" -ForegroundColor DarkGray
        Get-Content $target.FullName -Tail 30 -Wait
        return
    }

    foreach ($f in $files) {
        # No se filtra por $f.Length: mientras el servidor mantiene el archivo
        # abierto, Windows deja el tamano de la entrada de directorio en 0 y los
        # logs en vivo quedarian ocultos. Se lee y se decide por el contenido.
        $tail = Get-Content $f.FullName -Tail 25 -ErrorAction SilentlyContinue
        Write-Host ''
        Write-Host "--- $($f.Name) ---" -ForegroundColor DarkGray
        if ($tail) { $tail } else { Write-Host '      (vacio)' -ForegroundColor DarkGray }
    }
}

function Invoke-Seed {
    $python = Get-Python
    $envPath = Resolve-Shared 'apps\api\.env'
    if (-not $envPath) { $envPath = $EnvFile }
    $n = Import-DotEnv $envPath
    if ($n) { Write-Step "$n variables cargadas desde $envPath" }
    New-Item -ItemType Directory -Force -Path (Join-Path $ApiDir 'logs') | Out-Null
    Write-Step 'ejecutando seed_demo_pro ...'
    Push-Location $ApiDir
    try { & $python manage.py seed_demo_pro --settings=vyntia.settings.development }
    finally { Pop-Location }
}

# ─── Despacho ─────────────────────────────────────────────────────────────────

try {
    switch ($Action) {
        'start'  { Write-Title 'start';  Invoke-Start }
        'stop'   { Write-Title 'stop';   Invoke-Stop }
        'reload' { Write-Title 'reload'; Invoke-Stop; Start-Sleep -Milliseconds 900; Invoke-Start }
        'restart'{ Write-Title 'reload'; Invoke-Stop; Start-Sleep -Milliseconds 900; Invoke-Start }
        'status' { Write-Title 'status'; Invoke-Status }
        'logs'   { Write-Title 'logs';   Invoke-Logs }
        'seed'   { Write-Title 'seed';   Invoke-Seed }
    }
} catch {
    # Un stack trace de PowerShell no le dice nada util a quien solo queria
    # levantar la app; se muestra el mensaje y se sale con codigo de error.
    Write-Host ''
    Write-Err2 $_.Exception.Message
    Write-Host ''
    exit 1
}

Write-Host ''
