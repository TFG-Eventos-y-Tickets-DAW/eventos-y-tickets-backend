sudo dnf update -y
sudo dnf install mariadb105-server
# aws rds generate-db-auth-token --hostname eventosyticketsdb.czc8eckmuzy0.us-east-1.rds.amazonaws.com --port 3306 --username eventosytickets
# RDS:
# mysql -u eventosytickets -h eventosyticketsdb.czc8eckmuzy0.us-east-1.rds.amazonaws.com -P 3306 -p
# Aurora:
# mysql -u root -h eventosytickets-mysqlv2-one.czc8eckmuzy0.us-east-1.rds.amazonaws.com -P 3306 -p