sudo chmod 644 postgresql.conf

# Copy configuration files
sudo cp -f ./pg_hba.conf /etc/postgresql/13/main/pg_hba.conf
sudo cp -f ./postgresql.conf /etc/postgresql/13/main/postgresql.conf

sudo chmod 644 postgresql.conf

# Start postgres
sudo service postgresql restart