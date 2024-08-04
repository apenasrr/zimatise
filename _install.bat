call python -m venv ..\.venv
call ..\.venv\Scripts\activate
python -m pip install --upgrade pip
printf "call .venv\scripts\\activate\ncd %p%\npython -m pip install --upgrade pip\ncmd /k\n" > ..\activate_venv.bat
printf "call .venv\scripts\\activate\ncd %p%\npython -m pip install --upgrade pip\npip install -r requirements.txt --upgrade\ncmd /k\n" > ..\activate_venv_update.bat
pip install -r requirements.txt --upgrade
cmd /k