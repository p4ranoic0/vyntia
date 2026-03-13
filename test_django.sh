#!/bin/bash
cd /d/INTRANET/back
python manage.py check
echo "Django check completed"
timeout 10 python manage.py runserver 8000 2>&1 | head -20 &
sleep 3
curl -s http://127.0.0.1:8000/api/v1/auth/token/ || echo "Server not responding yet"
