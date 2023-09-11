#/usr/bin/sh
systemctl daemon-reload
systemctl status phy_parser.service
systemctl status cu_parser.service
systemctl status watchdog_parser.service
systemctl status bbu_api.service
systemctl status du_parser_new_148.service
systemctl status ru_acc_parser.service
systemctl status fans_rpm.service

echo 'Service status is showed.'
