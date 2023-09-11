#/usr/bin/sh
systemctl daemon-reload
systemctl enable phy_parser.service
systemctl enable cu_parser.service
systemctl enable watchdog_parser.service
systemctl enable bbu_api.service
systemctl enable du_parser_new_148.service
systemctl enable ru_acc_parser.service
systemctl enable fans_rpm.service
echo 'Service status is showed.'
