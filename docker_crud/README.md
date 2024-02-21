# Запуск контейнера с проектом "CRUD: Склады и запасы"

## 1. Сборка Docker-образа

```bash
docker build -t docker_crud .
```

## 2. Запуск контейнера

```bash
docker run -p 8000:8000 docker_crud
```

## 3. После запуска контейнера вы можете проверить его работоспособность, перейдя по адресу [http://localhost:8000/](http://localhost:8000/)