sudo apt-get install python-setuptools
sudo easy_install werkzeug
sudo easy_install scipy 
#sudo easy_install scikit-learn 
sudo easy_install redis
sudo easy_install jinja2
sudo easy_install pika
sudo easy_install json-rpc
sudo easy_install requests
sudo add-apt-repository ppa:rwky/redis
sudo apt-get update
sudo apt-get install redis-server
sudo apt-get install python-numpy python-scipy
sudo apt-get install rabbitmq-server

<<<<<<< HEAD
=======
sudo apt-get install nginx

>>>>>>> 8241059c9b8f4220ca1869df2d75e6bb8dd9b93a
sudo apt-get install netpbm
sudo apt-get install imagemagick


sudo rabbitmq-plugins enable rabbitmq_management
sudo rabbitmq-plugins enable rabbitmq_management_visualiser
sudo rabbitmqctl stop
sudo invoke-rc.d rabbitmq-server start
sudo rabbitmqctl status
