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
systemctl status du_parser.service | grep Loaded
systemctl status du_parser.service | grep Active
systemctl status du_parser_new.service | grep Loaded
systemctl status du_parser_new.service | grep Active
systemctl status bbu_api.service | grep Loaded
systemctl status bbu_api.service | grep Active
systemctl status du_parser_new_148.service | grep Loaded
systemctl status du_parser_new_148.service | grep Active
systemctl status ru_acc_parser.service | grep Loaded
systemctl status ru_acc_parser.service | grep Active
systemctl status fans_rpm.service | grep Loaded
systemctl status fans_rpm.service | grep Active
<<<<<<< HEAD
systemctl status ping.service | grep Loaded
systemctl status ping.service | grep Active
systemctl status test3.service | grep Loaded
systemctl status test3.service | grep Active
=======
# systemctl status ping.service | grep Loaded
# systemctl status ping.service | grep Active
>>>>>>> c377bee321e0ba9c0362cf512aaa4f75103decce
echo 'Service status is showed.'
