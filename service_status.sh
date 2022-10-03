#/usr/bin/sh
systemctl daemon-reload
systemctl status phy_parser.service | grep Loaded
systemctl status phy_parser.service | grep Active
systemctl status cu_parser.service | grep Loaded
systemctl status cu_parser.service | grep Active
systemctl status cu_parser_ue.service | grep Loaded
systemctl status cu_parser_ue.service | grep Active
systemctl status watchdog_parser.service | grep Loaded
systemctl status watchdog_parser.service | grep Active
systemctl status phy_parser_status.service | grep Loaded
systemctl status phy_parser_status.service | grep Active
echo 'Service status is showed.'