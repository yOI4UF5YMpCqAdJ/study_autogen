@echo off
echo Starting deployment...

rem 创建必要的目录
mkdir "deployment\akShare\db" 2>nul
mkdir "deployment\akShare\db\pre" 2>nul
mkdir "deployment\akShare\db\report" 2>nul
mkdir "deployment\akShare\log" 2>nul

rem 复制主要执行文件
copy /Y "akShare\xxlJobRun.py" "deployment\akShare\"

rem 复制数据库相关文件
copy /Y "akShare\db\.env" "deployment\akShare\db\"
copy /Y "akShare\db\db_manager.py" "deployment\akShare\db\"
copy /Y "akShare\db\pre\*.py" "deployment\akShare\db\pre\"
copy /Y "akShare\db\report\*.py" "deployment\akShare\db\report\"

rem 复制日志相关文件
copy /Y "akShare\log\logger.py" "deployment\akShare\log\"

echo Deployment completed successfully!
