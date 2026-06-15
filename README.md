# 1 установить файлы
#2 написать в cmd 
pip install fastapi uvicorn sqlalchemy bcrypt starlette-session itsdangerous jinja2
#3
uvicorn app.main:app --reload
#4 перейти по 
http://127.0.0.1:8000/register

#пример пользователя:Email: test@example.com,пароль: 123456
