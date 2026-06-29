FROM nginx:1.25-alpine

# Удаляем дефолтный конфиг сборки
RUN rm /etc/nginx/conf.d/default.conf

# Копируем ваш конфиг внутрь образа (имя файла укажите ваше, например default.conf)
COPY default.conf /etc/nginx/conf.d/default.conf
