#/usr/bin/sh
systemctl daemon-reload
systemctl stop phy_parser.service
systemctl status phy_parser.service | grep Loaded
systemctl status phy_parser.service | grep Active
systemctl stop cu_parser.service
systemctl status cu_parser.service | grep Loaded
systemctl status cu_parser.service | grep Active
systemctl stop cu_parser_ue.service
systemctl status cu_parser_ue.service | grep Loaded
systemctl status cu_parser_ue.service | grep Active
systemctl stop watchdog_parser.service
systemctl status watchdog_parser.service | grep Loaded
systemctl status watchdog_parser.service | grep Active
# systemctl stop phy_parser_status.service
# systemctl status phy_parser_status.service | grep Loaded
# systemctl status phy_parser_status.service | grep Active
# systemctl stop du_parser.service
# systemctl status du_parser.service | grep Loaded
# systemctl status du_parser.service | grep Active
# systemctl stop du_parser_new.service
# systemctl status du_parser_new.service | grep Loaded
# systemctl status du_parser_new.service | grep Active
systemctl stop bbu_api.service
systemctl status bbu_api.service | grep Loaded
systemctl status bbu_api.service | grep Active
systemctl stop du_parser_new_148.service
systemctl status du_parser_new_148.service | grep Loaded
systemctl status du_parser_new_148.service | grep Active
systemctl stop ru_acc_parser.service
systemctl status ru_acc_parser.service | grep Loaded
systemctl status ru_acc_parser.service | grep Active
systemctl stop fans_rpm.service
systemctl status fans_rpm.service | grep Loaded
systemctl status fans_rpm.service | grep Active
# systemctl stop ping.service
# systemctl status ping.service | grep Loaded
# systemctl status ping.service | grep Active
echo 'Service is stopped.'
