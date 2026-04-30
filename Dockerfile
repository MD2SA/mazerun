
FROM php:8.3-apache

RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli

RUN chown -R www-data:www-data /var/www/html
