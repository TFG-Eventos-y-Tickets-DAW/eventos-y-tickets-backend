sudo dnf update -y
sudo dnf install mariadb105-server
# aws rds generate-db-auth-token --hostname eventosyticketsdb.czc8eckmuzy0.us-east-1.rds.amazonaws.com --port 3306 --username eventosytickets
# mysql -u MY_USER -h MY_HOST -P 3306 -p