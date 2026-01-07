# python-fast-api-template

**document**
<https://fastapi.tiangolo.com/learn/>

python3 -m venv env
source env/bin/activate

**Install python packages requirements**:\
pip3 install -r requirements.txt

**Start app**
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Allow external devices to access

**Automatically create file 'requirements.txt'**
pip freeze > requirements.txt

window:

Tạo môi trường ảo
python -m venv venv
Kích hoạt môi trường ảo
venv\Scripts\activate

# Run test

pytest
