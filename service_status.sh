#/usr/bin/sh
systemctl daemon-reload
# systemctl restart phy_parser.service
systemctl status phy_parser.service | grep Loaded
systemctl status phy_parser.service | grep Active
# systemctl restart cu_parser.service
systemctl status cu_parser.service | grep Loaded
systemctl status cu_parser.service | grep Active
# systemctl restart cu_parser_ue.service
systemctl status cu_parser_ue.service | grep Loaded
systemctl status cu_parser_ue.service | grep Active
# systemctl restart watchdog_parser.service
systemctl status watchdog_parser.service | grep Loaded
systemctl status watchdog_parser.service | grep Active
# systemctl restart phy_parser_status.service
systemctl status phy_parser_status.service | grep Loaded
systemctl status phy_parser_status.service | grep Active
echo 'Service status is showed.'
