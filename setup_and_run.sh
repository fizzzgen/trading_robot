apt-get install python3-pip
pip install -r requirements.txt
cp trading_robot/services/* /etc/systemd/system/.
systemctl daemon-reload
systemctl start job_predict.service
systemctl start job_price_update.service
systemctl start job_orders_engine.service
systemctl status job_predict.service job_price_update.service job_orders_engine.service
