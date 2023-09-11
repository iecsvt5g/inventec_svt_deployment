#mkdir -p /etc/inventec_svt_deployment/
echo "- Stop service"
sudo systemctl stop bbu_api
sleep 1

echo "- Update service"
sudo chmod 644 *.service
sudo cp *.service /etc/systemd/system
sleep 1

#echo "- Copy from management system"
#cp api.py /etc/inventec_svt_deployment/
#cp my_bbu /etc/inventec_svt_deployment/

sudo systemctl daemon-reload
sleep 1
sudo systemctl start  bbu_api
sleep 1
sudo systemctl enable bbu_api

echo "- Check service status"
sudo systemctl status  bbu_api