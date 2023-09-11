#/usr/bin/sh
systemctl daemon-reload
systemctl restart phy_parser.service
systemctl restart cu_parser.service
systemctl restart watchdog_parser.service
systemctl restart bbu_api.service
systemctl restart du_parser_new_148.service
systemctl restart ru_acc_parser.service
systemctl restart fans_rpm.service

echo 'Service is restarted.'

