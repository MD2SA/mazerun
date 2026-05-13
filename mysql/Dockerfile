FROM php:8.3-apache

RUN docker-php-ext-install mysqli pdo pdo_mysql && docker-php-ext-enable mysqli pdo pdo_mysql

RUN chown -R www-data:www-data /var/www/html
