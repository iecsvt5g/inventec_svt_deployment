#/usr/bin/sh
systemctl daemon-reload
systemctl start phy_parser.service
systemctl start cu_parser.service
systemctl start watchdog_parser.service
systemctl start bbu_api.service
systemctl start du_parser_new_148.service
systemctl start ru_acc_parser.service
systemctl start fans_rpm.service

echo 'Service is started.'
