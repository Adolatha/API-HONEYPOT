## Setting up the web environment

### Install NGINX Webserver
Install the necessary prerequisites:

```bash
sudo apt update
sudo apt install curl gnupg2 ca-certificates lsb-release debian-archive-keyring gi
```

Import an official nginx signing key with fetch:
```bash
curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
```
Verify that the downloaded file contains the proper key

```bash
gpg --dry-run --quiet --no-keyring --import --import-options import-show /usr/share/keyrings/nginx-archive-keyring.gpg

```
Set up the apt repository for stable nginx packages:
```bash
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/debian lsb_release -cs nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
```
Run update and upgrade first before installing the webserver:
```bash
sudo apt update 
sudo apt upgrade
```
Run the following command to install NGINX:
```bash
sudo apt install nginx
```
Check the version of NGINX:
```bash
nginx -v
```
Response => ``nginx version: nginx/1.28.0``

Add user nginx to the www-data-group:
```bash
sudo usermod -aG www-data nginx
```
Configuration of the NGINX web server is described further in the document

1. CONFIGURE NGINX

   Edited the Nginx configuration file to apply secure configurations 
   1. Change new document root with servername "Honeypot"
   2. Install and configure HTTPS to ensure encrypted web traffic for security and prevent man in the middle eavesdropping:
         ````command to install certificates:
         sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
      ````
   3. Allow HTTPS in nginx configuration:
      ````nginx
            server {
            listen 443 ssl;
            server_name HoneyPot;

            ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
            ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
            ssl_protocols TLSv1.3;
            ssl_ciphers HIGH:!aNULL:!MD5;
      ````
      ``sudo systemctl restart nginx``
      
   4. Redirect the HTTP site to HTTPS so that all unencrypted traffic is avoided to secure the web server:
      ````nginx
            server {
            listen 80;
            server_name HoneyPot;
      
            return 301 https://$host$request_uri;
        }
      ````
   5. Add the security headers in NGINX
      X-Frame-Options "DENY" :To prevent the website from being embedded in an iframe on any page.
      X-Content-Type-Options nosniff: To instruct the browsers not to guess ("sniff") the MIME type of files, and instead trust the declared Content-Type
      Strict-Transport-Security "max-age=172800; includeSubDomains": To enable HTTP Strict Transport Security (HSTS) only on the site.
      ````nginx
        add_header X-Frame-Options "deny";
        add_header X-Contenty-Type-Options nosniff;
        add_header Strict-Transport-Security 'max-age=172800; includeSubDomains';
      ````
   6. Stop nginx version printing
      ````nginx
         server_tokens off;
      ````
   7. Restrict HTTP methods to only POST and GET 
      ````nginx
         limit_except GET POST { deny all; }
      ````
   8. Added HTTP/2 for faster, more efficient, and encrypted connections.
      ````nginx
         server {
         listen 443 ssl;
         server_name HoneyPot;

         http2 on;
      ````
   9. Tested the Nginx configuration and all was successful
      ``nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
       nginx: configuration file /etc/nginx/nginx.conf test is successful
       ``
   10. Test the Application
    Accessed the application via the browser at:
      ```arduino
      https://web-server/
      ```

### Deploying and Configuring Filebeat

This document outlines the steps I followed to deploy and configure Filebeat to collect logs and forward them to an Elasticsearch instance.

#### Steps to Deploy Filebeat

1. Install Filebeat
   Downloaded and installed Filebeat on the server:

```bash
sudo apt install gnupg

wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg

sudo apt-get install apt-transport-https

echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

sudo apt update

sudo apt install filebeat
```

2. Configure the filebeat.yml File
   Edited the main Filebeat configuration file:

```bash
sudo nano /etc/filebeat/filebeat.yml
```
Updated the `filebeat.yml` file with the following settings:

#### Filebeat Inputs:

```yaml
filebeat.inputs:
  - type: filestream
    enabled: false
    paths:
      - /var/log/*.log
```

#### Modules Configuration:

```yaml
filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: false
```

#### Elasticsearch Output:

```yaml
output.elasticsearch:
   # Array of hosts to connect to.
   hosts: ["192.168.40.128:9200"]

   # Performance preset - one of "balanced", "throughput", "scale",
   # "latency", or "custom".
   #preset: balanced

   # Protocol - either `http` (default) or `https`.
   protocol: "https"

   # Authentication credentials - either API key or username/password.
   #api_key: "id:api_key"
   username: "elastic"
   password: 

   ssl:
      enabled: true
      ca_trusted_fingerprint: "CB969A57892F8E314A441A6A8B1E2C8338446E308F8E3474F70D9D8C34908ECA"

```

3. Enable the Nginx Module
   Enabled the built-in Nginx module:

```bash
sudo filebeat modules enable nginx
```
Edited the Nginx module configuration file to enable access and error logs:

```bash
sudo nano /etc/filebeat/modules.d/nginx.yml
```
Updated the configuration as follows:

```yaml
# Module: nginx
# Docs: https://www.elastic.co/guide/en/beats/filebeat/8.18/filebeat-module-nginx.html

- module: nginx
   # Access logs
  access:
     enabled: true

     # Set custom paths for the log files. If left empty,
     # Filebeat will choose the paths depending on your OS.
     #var.paths:

   # Error logs
  error:
     enabled: true

     # Set custom paths for the log files. If left empty,
     # Filebeat will choose the paths depending on your OS.
     #var.paths:
```

4. Validate Filebeat Configuration
   Tested the configuration to ensure it was valid:

```bash
sudo filebeat test config
```
Output:

```bash
Config OK
```

5. Restart Filebeat
   Restarted the Filebeat service to apply the configuration changes:

```bash
sudo systemctl restart filebeat
```

### Steps to Install and configure WAF

#### Install packages
```bash
sudo apt-get update
sudo apt-get install git g++ apt-utils autoconf automake build-essential \
    libcurl4-openssl-dev libgeoip-dev liblmdb-dev libpcre2-dev libtool \
    libxml2-dev libyajl-dev pkgconf zlib1g-dev libssl-dev
```
#### Get & Build ModSecurity (Library)
Clone the OWASP ModSecurity project and compile it:
```bash
git clone --recursive https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity/
git submodule init
git submodule update
./build.sh
./configure --with-pcre2
make
sudo make install
```

#### Get the ModSecurity Nginx Connector
Clone the ModSecurity connector (bridge between ModSecurity and Nginx):
```bash
sudo mkdir -p /usr/local/src/cpg
cd /usr/local/src/cpg
sudo git clone https://github.com/SpiderLabs/ModSecurity-nginx
```
#### Download Nginx Source
```bash
wget http://nginx.org/download/nginx-1.28.0.tar.gz
tar -xvzf nginx-1.28.0.tar.gz
cd nginx-1.28.0/
```
#### Build the Dynamic Module
Configure Nginx with the ModSecurity module:
```bash
sudo ./configure --with-compat \
    --add-dynamic-module=/usr/local/src/cpg/ModSecurity-nginx
sudo make modules
```

Copying the compiled ModSecurity dynamic module to NGINX's modules directory
```bash
sudo cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules/
```
#### Enable ModSecurity in Nginx
```bash
sudo nano /etc/nginx/nginx.conf
```
Add line:
````nginx
   load_module modules/ngx_http_modsecurity_module.so;
````
#### Get the OWASP Core Rule Set for Modsecurity

```bash
sudo git clone https://github.com/coreruleset/coreruleset /opt/coreruleset
```
Cloning the OWASP Core Rule Set (CRS) repository to our server

```bash
sudo mv /opt/coreruleset/crs-setup.conf.example /opt/coreruleset/crs-setup.conf
```
Renaming the example CRS setup configuration file to make it active

```bash
sudo mv /opt/coreruleset/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example /opt/coreruleset/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
```
Activating exclusion rules provided by CRS by renaming it

```bash
sudo mkdir /etc/nginx/modsec
```
Create directory modsec

```bash
sudo cp ~/ModSecurity/unicode.mapping /etc/nginx/modsec
```
Copying the Unicode mapping file to the ModSecurity configuration directory

```bash
sudo cp ~/ModSecurity/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf
```
Copying the recommended ModSecurity configuration file to the ModSecurity configuration directory

```bash
sudo nano /etc/nginx/modsec/modsecurity.conf
```
Opening the ModSecurity configuration file for editing

Edit the configuration and change SecRuleEngine DetectionOnly to On

```bash
sudo nano /etc/nginx/modsec/main.conf
```
Creating the main configuration file for ModSecurity integration
Adding the following lines to the config file:
```
Include /etc/nginx/modsec/modsecurity.conf
Include /opt/coreruleset/crs-setup.conf
Include /opt/coreruleset/rules/*.conf
```

#### Virtual host

```bash
sudo nano /etc/nginx/conf.d/default.conf
```
Edit the virtual host
Added these lines in server listen 80 under server name:
```
modsecurity on;
modsecurity_rules_file /etc/nginx/modsec/main.conf;
```