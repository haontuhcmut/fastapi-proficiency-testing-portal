#generate random numbers
openssl rand hex-32

#migration
alembic revision --autogernerate -m "somthing..."

alembic upgrade head --sql

alembic upgrade head

#redis
redis-server

#celery
celery -A app.celery_task.c_app worker -l info
