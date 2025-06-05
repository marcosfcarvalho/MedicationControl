@echo off
setlocal

:: Pega a data no formato YYYY-MM-DD
for /f %%i in ('powershell -command "Get-Date -Format yyyy-MM-dd"') do set "data=%%i"

:: Caminho do arquivo original
set "origem=D:\programas em python\Projeto Clara\controle_medicamentos.db"

:: Caminho do arquivo temporário com a data no nome
set "arquivo_temp=D:\programas em python\Projeto Clara\controle_medicamentos_%data%.db"

:: Copia o arquivo com o novo nome
copy "%origem%" "%arquivo_temp%" >nul

:: Envia o arquivo renomeado para o Google Drive (substitua 'gdrive_enf' se necessário)
rclone copy --progress "%arquivo_temp%" "gdrive_enf:" --exclude="/.tmp.driveupload**"

:: Apaga o arquivo temporário depois do upload
del "%arquivo_temp%"

echo Backup finalizado com data: %data%
