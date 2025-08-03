#!/bin/bash

AVAHI_SERVICE_FILE="/etc/avahi/services/minidlna.service"
AVAHI_SERVICE_HTTPS_FILE="/etc/avahi/services/https-api.service"

SERIAL_NUMBER=$(grep -m 1 'Serial' /proc/cpuinfo | awk '{print $3}')

if [ -z  "$SERIAL_NUMBER" ]; then
        echo "Error: unable to get the cpu serial number"
        exit 1
fi

sudo tee "$AVAHI_SERVICE_FILE" > /dev/null << 'EOF'
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">${SERIAL_NUMBER}.storagepod.campuscatalyst</name>
  <service>
    <type>_dlna._tcp</type>
    <port>8200</port>
  </service>
</service-group>
EOF

sudo tee "$AVAHI_SERVICE_HTTPS_FILE" > /dev/null << 'EOF'
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <!-- The hostname advertised by mDNS -->
  <name replace-wildcards="yes">storagepod</name>
  <service>
    <type>_https._tcp</type>
    <port>443</port>
  </service>
</service-group>
EOF

sudo sed -i "s/\${SERIAL_NUMBER}/$SERIAL_NUMBER/g" "$AVAHI_SERVICE_FILE"

echo "Avahi service file created/updated at: $AVAHI_SERVICE_FILE"
echo "Service name: ${SERIAL_NUMBER}.storagepod.campuscatalyst"
echo "Avahi service file HTTPs api created/updated"