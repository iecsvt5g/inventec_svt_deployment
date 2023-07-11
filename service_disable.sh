#/usr/bin/sh

systemctl disable phy_parser_status.service
systemctl status phy_parser_status.service | grep Loaded
systemctl status phy_parser_status.service | grep Active
systemctl disable du_parser.service
systemctl status du_parser.service | grep Loaded
systemctl status du_parser.service | grep Active
systemctl disable du_parser_new.service
systemctl status du_parser_new.service | grep Loaded
systemctl status du_parser_new.service | grep Active

# systemctl enable ping.service
# systemctl status ping.service | grep Loaded
# systemctl status ping.service | grep Active
echo 'Service status is showed.'
