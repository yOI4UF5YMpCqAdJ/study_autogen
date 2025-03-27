# 日志目录
$logDirectory = "C:/Publish/python-kksStock/Logs"
$logFile = "$logDirectory/log.txt"

# 确保日志目录存在
if (-not (Test-Path $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory | Out-Null
}

# 日志记录函数
function Write-Log {
    param ([string]$message)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $logMessage = "$timestamp - $message"
    Add-Content -Path $logFile -Value $logMessage
}

# 虚拟环境路径
$venvPath = "C:/Publish/python-kksStock/kksStock"
$activateScript = "$venvPath/Scripts/Activate.ps1"
$pythonScript = "C:/Publish/python-kksStock/akShare/xxlJobRun.py"

try {
    # 1. 激活虚拟环境
    Write-Log "开始激活虚拟环境"
    
    # 使用完整路径确保正确执行
    $pythonExe = "$venvPath\Scripts\python.exe"
    
    # 激活虚拟环境
    . $activateScript
    Write-Log "虚拟环境激活成功"

    # 2. 运行Python脚本
    Write-Log "开始运行Python脚本"
    
    # 使用完整Python解释器路径执行脚本
    $process = Start-Process -FilePath $pythonExe -ArgumentList $pythonScript -PassThru -Wait -NoNewWindow
    
    # 检查退出码
    if ($process.ExitCode -eq 0) {
        Write-Log "Python脚本运行成功"
    } else {
        Write-Log "Python脚本运行失败，退出码：$($process.ExitCode)"
        exit 1
    }
}
catch {
    Write-Log "发生错误: $_"
    exit 1
}
finally {
    # 3. 关闭虚拟环境
    if (Get-Command -Name deactivate -ErrorAction SilentlyContinue) {
        Write-Log "关闭虚拟环境"
        deactivate
        Write-Log "虚拟环境关闭成功"
    }
}

exit 0