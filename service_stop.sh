#/usr/bin/sh
systemctl daemon-reload
systemctl stop phy_parser.service
systemctl stop cu_parser.service
systemctl stop watchdog_parser.service
systemctl stop bbu_api.service
systemctl stop du_parser_new_148.service
systemctl stop ru_acc_parser.service
systemctl stop fans_rpm.service

echo 'Service is stopped.'
