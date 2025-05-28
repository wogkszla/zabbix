#!/bin/bash

# A script to generate Zabbix map XML from PNG images
# depends on base64

echo "Generating XML"

imagedir="$1"
outputfile="$2"

echo '<?xml version="1.0" encoding="UTF-8"?>
<zabbix_export version="1.0" date="'$(date "+%d.%m.%y")'" time="'$(date "+%H.%M")'">
  <images>' > "$outputfile"

imagecount=$(find "$imagedir" -name '*.png' | wc -l)
# Use 'find' to correctly handle file names containing spaces
find "$imagedir" -name '*.png' -print0 | while IFS= read -r -d '' imagefile; do
	((imagesdone++))
	echo "    <image>
      <name>$(basename "${imagefile%.png}")</name>
      <imagetype>1</imagetype>
      <encodedImage>$(base64 --wrap=0 "$imagefile")</encodedImage>
    </image>" >> "$outputfile"
	echo -n "$[$imagesdone*100/$imagecount]% "
done
echo

echo '  </images>
  <sysmaps>
  </sysmaps>
</zabbix_export>' >> "$outputfile"
