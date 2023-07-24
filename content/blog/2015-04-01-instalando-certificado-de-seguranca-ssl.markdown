+++
date = "2015-04-01"
title = "Instalando certificado de segurança SSL"
tags = ["security","linux"]
+++

O SSL **(Secure Socket Layer)** é um protocolo desenvolvido para elevar a segurança dos dados transmitidos pela internet. O SSL pode ser usado em vários serviços, sendo que o mais comum é o acesso à páginas web.

# Introdução

### Antes de tudo. O que é SSL?

O **SSL (Secure Socket Layer)** é um protocolo desenvolvido para elevar a segurança dos dados transmitidos pela internet. O SSL pode ser usado em vários serviços, sendo que o mais comum é o acesso à páginas web. Neste caso o endereço dos recursos acessados passa a ser feito no formato: `https://website`.

As conexões via SSL são particularmente recomendadas para envio de informações como números de cartão de crédito, senhas e qualquer outra informação sigilosa via internet.

O SSL faz uso de **criptografia** para garantir o sigilo das informações transferidas entre o navegador do usuário e o servidor web. Como consequência, mesmo que as informações sejam interceptadas elas não podem ser lidas sem que sejam **descriptografadas**.

### O que é um certificado SSL?

O certificado SSL tem a função de certificar que o site que você está acessando é realmente ele mesmo. Este processo é realizado por empresas que emitem certificados SSL. Elas fazem a validação do domínio e, dependendo do tipo de certificado, também da entidade detentora do domínio.

Sempre que você acessa uma página segura, isto é, protegida por um certificado SSL, é apresentada uma chave ou um cadeado na barra de status para indicar a comunicação segura. Os certificados tradicionais exigem que você clique na chave ou cadeado para ter acesso às informações do detentor do certificado SSL.

Texto retirado do site: centralserver.com.br clique aqui para visualizar o texto completo.

O domínio leonardorifeli.com possuí o certificado SSL COMODO 256bits. Efetuei a compra do certificado por fins didáticos (estudos para configuração). Estarei demonstrando como efetuei a instalação do certificado no servidor.

**Obs.:** Salientando que não demonstrarei como efetuar a compra/solicitação do certificado.

# Informações

Sistema Operacional (servidor): Ubuntu Server 14.04; Dependências: apache2, openssl e ssl-cert;

### Dependências

As depências são os recursos/bibliotecas utilizadas para a gerar e configurar o certificado. Faça acesso SSH com o servidor, utilizando privilégios de root (oh my god! Yes!).

Execute os comandos abaixo para atualização de dependências já instaladas. Posteriormente, certifique-se que: apache2, openssl e ssl-cert encontram-se instalados no ambiente.

`apt-get update
apt-get upgrade
apt-get install apache2 openssl ssl-cert`

# Gerando as chaves

Criando o diretório onde os certificados serão armazenados.

`mkdir /etc/apache2/ssl/`

Acessando o diretório dos certificados.

`cd /etc/apache2/ssl/`

Gerando as chaves. Atente-se leia os descritivos abaixo antes de acionar enter.

`openssl req -nodes -newkey rsa:2048 -keyout dominio.com.key -out dominio.com.csr`

Primeiro entenderemos o que o comando acima executará.

O comando em questão irá gerar o arquivo **dominio.com.key**, o qual contém a chave privada e **não deverá em hípotese alguma, ser fornecido há alguém**.

De imediato, certifique-se de fazer o backup da chave privada **(dominio.com.key)**, pois não há meios de recuperá-la. A chave privada é utilizada como entrada no processo para gerar um **“Pedido de Assinatura de Certificado (CSR)”.** O CSR é um arquivo contendo as informações da solicitação do certificado (logo você preencherá algumas informações), incluindo sua chave pública.

Agora que foi informado a função do comando citado, pode acionar enter, logo você preencherá as informações para o certificado:

Veja como as perguntas serão feitas e como respondê-las:

`Country Name (2 letter code) [AU]: BR
State or Province Name (full name) [Some-State]: SP
Locality Name (eg, city) []: Araraquara
Organization Name (eg, company) [Internet Widgits Pty Ltd]: Nome da empresa (deixe em branco caso não possua)
Organizational Unit Name (eg, section) []: Cargo na empresa (deixe em branco caso não possua)
Common Name (eg, YOUR name) []: dominio.com
Email Address []: contato@dominio.com
Please enter the following ‘extra’ attributes to be sent with your certificate request
A challenge password []: aperte enter (deixar em branco)
An optional company name []: aperte enter (deixar em branco)`

Após a finalização, o arquivo **dominio.com.key** será criado. Deixe-o com permissão de acesso 600.

`chmod 600 dominio.com.key`

Após finalizar, certifique-se que dois arquivos foram criados, **dominio.com.key** e **dominio.com.csr**. Lembre-se que o conteúdo do arquivo **“dominio.com.csr”** deve ser utilizado para finalizar a solicitação de registro do certificado (colar no campo “Enter CSR”). Efetuei a compra no site Comodo.

Pegando o conteúdo do arquivo **dominio.com.csr**.

`cat dominio.com.csr`

Após finalizar a compra, o provedor do certificado envia os seguintes arquivos para serem instalados no servidor:

1. **Root CA Certificate:** AddTrustExternalCARoot.crt
2. **Intermediate CA Certificate:** AAddTrustCA.crt
3. **Intermediate CA Certificate:** DomainValidationSecureServerCA.crt
4. **Your PositiveSSL Certificate:** (dominio).crt

PS: A empresa **Comodo** enviou os arquivos acima via e-mail. Lembre-se, guarde-os com segurança.

Faça upload dos arquivos no diretório, `/etc/apache2/ssl`.

Os três primeiros arquivos serão utilizados para gerar o arquivo que será utilizado pelo `Apache` **(criar arquivo com extensão ”.ca-bundle”)**. Mergeie (mesclar, juntar) os conteúdos em um único arquivo com nome “dominio.ca-bundle, utilizando o comando.

`cat AAddTrustCA.crt DomainValidationSecureServerCA.crt AddTrustExternalCARoot.crt > www.dominio.com.ca-bundle`

# Configuração no Apache

Com o arquivo `.ca-bundle` criado, efetuaremos a configuração no arquivo `.conf` do respectivo domínio (no apache).

`cd /etc/apache2/sites-available
nano arquivo-configuracao-utilizado.conf`

Segue abaixo um modelo em funcionamento (você poderá utilizá-lo como base).

### Configuração da porta 80 para redirecionar os acessos http para https, porta 443;

`<VirtualHost *:80> ServerAdmin your@dominio.com ServerName dominio.com ServerAlias www.dominio.com RewriteEngine On RewriteCond %{HTTPS} off RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI}
</VirtualHost>`

### Configuração da porta 443, onde o site funcionará (acesso https);

`<VirtualHost *:443> ServerName www.dominio.com:443 ServerAdmin your@dominio.com ServerName dominio.com ServerAlias www.dominio.com DocumentRoot /var/www/website DirectoryIndex index.php index.htm index.html TransferLog /var/log/apache2/website.log SSLEngine on SSLCertificateKeyFile /etc/apache2/ssl/www.dominio.com.key SSLCertificateFile /etc/apache2/ssl/www.dominio.com.crt SSLCertificateChainFile /etc/apache2/ssl/www.dominio.com.ca-bundle ServerSignature off <Directory "/var/www/website"> AllowOverride All </Directory> ErrorLog ${APACHE_LOG_DIR}/error.log CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>`

Após finalizar a configuração.

`service apache2 restart`

Caso dê algum erro, verifique os logs (pois é para isso que eles existem). Brincadeiras, entre em contato, ficarei feliz em dar auxilio na medida do possível.

# Conclusão

A utilização de certificado de segurança em sites/sistemas que possuem tráfego de informações privilegiadas é imprescindível. Portanto, certifique-se que as informações contídas nas áreas restritas, encontram-se seguras.

Espero ter-lhe auxiliado em algum aspecto. Até o próximo post.