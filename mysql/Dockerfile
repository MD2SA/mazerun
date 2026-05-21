FROM php:8.3-apache

# Install runtime dependencies
RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y wine wine32:i386 \
    && rm -rf /var/lib/apt/lists/*

# Install MySQL extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql && docker-php-ext-enable mysqli pdo pdo_mysql

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Configure Apache to allow .htaccess and pass Authorization header
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

RUN chown -R www-data:www-data /var/www/html
