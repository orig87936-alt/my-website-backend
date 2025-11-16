# pgvector 安装脚本 for Windows
# 需要 Visual Studio Build Tools

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "pgvector 安装脚本" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否有 Git
Write-Host "检查 Git..." -ForegroundColor Yellow
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "❌ 未找到 Git。请先安装 Git for Windows。" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Git 已安装" -ForegroundColor Green

# 检查是否有 Visual Studio Build Tools
Write-Host ""
Write-Host "检查 Visual Studio Build Tools..." -ForegroundColor Yellow
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    Write-Host "✅ Visual Studio Build Tools 已安装" -ForegroundColor Green
} else {
    Write-Host "❌ 未找到 Visual Studio Build Tools" -ForegroundColor Red
    Write-Host ""
    Write-Host "需要安装 Visual Studio Build Tools:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://visualstudio.microsoft.com/downloads/" -ForegroundColor Yellow
    Write-Host "2. 下载 'Build Tools for Visual Studio 2022'" -ForegroundColor Yellow
    Write-Host "3. 安装时选择 'Desktop development with C++'" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "是否继续尝试安装？(y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# PostgreSQL 路径
$pgPath = "D:\PostgreSQL"
$pgBin = "$pgPath\bin"
$pgLib = "$pgPath\lib"
$pgShare = "$pgPath\share\extension"

Write-Host ""
Write-Host "PostgreSQL 路径: $pgPath" -ForegroundColor Cyan
Write-Host ""

# 克隆 pgvector
$tempDir = "$env:TEMP\pgvector"
if (Test-Path $tempDir) {
    Write-Host "删除旧的临时目录..." -ForegroundColor Yellow
    Remove-Item -Path $tempDir -Recurse -Force
}

Write-Host "克隆 pgvector 仓库..." -ForegroundColor Yellow
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git $tempDir

if (-not $?) {
    Write-Host "❌ 克隆失败" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 克隆成功" -ForegroundColor Green

# 编译
Write-Host ""
Write-Host "开始编译..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟..." -ForegroundColor Yellow
Write-Host ""

Set-Location $tempDir

# 使用 nmake 编译
$env:PATH = "$pgBin;$env:PATH"

Write-Host "运行 nmake..." -ForegroundColor Yellow
nmake /F Makefile.win

if (-not $?) {
    Write-Host ""
    Write-Host "❌ 编译失败" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "1. 未安装 Visual Studio Build Tools" -ForegroundColor Yellow
    Write-Host "2. 未配置 C++ 编译环境" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "建议: 使用预编译的二进制文件或暂时跳过 pgvector" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 编译成功" -ForegroundColor Green

# 安装
Write-Host ""
Write-Host "安装 pgvector..." -ForegroundColor Yellow

nmake /F Makefile.win install

if (-not $?) {
    Write-Host "❌ 安装失败" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 安装成功" -ForegroundColor Green

# 清理
Write-Host ""
Write-Host "清理临时文件..." -ForegroundColor Yellow
Set-Location $env:TEMP
Remove-Item -Path $tempDir -Recurse -Force

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "✅ pgvector 安装完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步: 在数据库中启用扩展" -ForegroundColor Cyan
Write-Host 'psql -U postgres -d newsdb -c "CREATE EXTENSION vector;"' -ForegroundColor Yellow
Write-Host ""

