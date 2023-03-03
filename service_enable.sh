#/usr/bin/sh
systemctl daemon-reload
systemctl enable phy_parser.service
systemctl status phy_parser.service | grep Loaded
systemctl status phy_parser.service | grep Active
systemctl enable cu_parser.service
systemctl status cu_parser.service | grep Loaded
systemctl status cu_parser.service | grep Active
systemctl enable cu_parser_ue.service
systemctl status cu_parser_ue.service | grep Loaded
systemctl status cu_parser_ue.service | grep Active
systemctl enable watchdog_parser.service
systemctl status watchdog_parser.service | grep Loaded
systemctl status watchdog_parser.service | grep Active
systemctl enable phy_parser_status.service
systemctl status phy_parser_status.service | grep Loaded
systemctl status phy_parser_status.service | grep Active
systemctl enable du_parser.service
systemctl status du_parser.service | grep Loaded
systemctl status du_parser.service | grep Active
systemctl enable du_parser_new.service
systemctl status du_parser_new.service | grep Loaded
systemctl status du_parser_new.service | grep Active
systemctl enable bbu_api.service
systemctl status bbu_api.service | grep Loaded
systemctl status bbu_api.service | grep Active
echo 'Service status is showed.'
