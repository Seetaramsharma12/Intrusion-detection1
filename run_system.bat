@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Training ML Model...
python backend/train_model.py

echo Starting Backend Server...
start "IDS Backend" python backend/app.py

echo Opening Frontend...
start frontend/index.html

echo System is running!
pause
