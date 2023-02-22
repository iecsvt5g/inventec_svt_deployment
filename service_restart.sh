#/usr/bin/sh
systemctl daemon-reload
systemctl restart phy_parser.service
systemctl status phy_parser.service | grep Loaded
systemctl status phy_parser.service | grep Active
systemctl restart cu_parser.service
systemctl status cu_parser.service | grep Loaded
systemctl status cu_parser.service | grep Active
systemctl restart cu_parser_ue.service
systemctl status cu_parser_ue.service | grep Loaded
systemctl status cu_parser_ue.service | grep Active
systemctl restart watchdog_parser.service
systemctl status watchdog_parser.service | grep Loaded
systemctl status watchdog_parser.service | grep Active
systemctl restart phy_parser_status.service
systemctl status phy_parser_status.service | grep Loaded
systemctl status phy_parser_status.service | grep Active
systemctl restart du_parser.service
systemctl status du_parser.service | grep Loaded
systemctl status du_parser.service | grep Active
systemctl restart du_parser_new.service
systemctl status du_parser_new.service | grep Loaded
systemctl status du_parser_new.service | grep Active
echo 'Service is restarted.'
