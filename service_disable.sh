#/usr/bin/sh
systemctl daemon-reload
systemctl disable phy_parser.service
systemctl disable cu_parser.service
systemctl disable watchdog_parser.service
systemctl disable bbu_api.service
systemctl disable du_parser_new_148.service
systemctl disable ru_acc_parser.service
systemctl disable fans_rpm.service

echo 'Service status is showed.'
