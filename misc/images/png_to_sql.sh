#!/bin/bash

# A script to generate SQL from PNG images
# depends on hexdump and base64

scriptdir="$(dirname "$0")"
pngdir="${1:-png_modern}"
sqlbasedir="$scriptdir/../../database"
imagefile="images.sql"

imagefile_mysql="$sqlbasedir/mysql/$imagefile"
imagefile_pgsql="$sqlbasedir/postgresql/$imagefile"

for imagefile in "$imagefile_mysql" "$imagefile_pgsql"; do
	[[ -s "$imagefile" ]] && {
		echo "Non-empty $imagefile already exists, stopping"
		exit 1
	}
done

echo "Generating SQL files"


imagecount=$(find "$pngdir" -name '*.png' | wc -l)
# Use 'find' to correctly handle file names containing spaces
find "$pngdir" -name '*.png' -print0 | while IFS= read -r -d '' imagefile; do
	((imagesdone++))
	imagename="$(basename "${imagefile%.png}")"
	image_data=$(hexdump -ve '"" 1/1 "%02X"' "$imagefile")

	# ----- MySQL
	echo "INSERT INTO \`images\` (\`imageid\`,\`imagetype\`,\`name\`,\`image\`) VALUES ($imagesdone,1,'$imagename',0x$image_data);" >> "$imagefile_mysql"
	# ----- PostgreSQL
	echo "INSERT INTO images (imageid,imagetype,name,image) VALUES ($imagesdone,1,'$imagename',decode('$image_data','hex'));" >> "$imagefile_pgsql"

	echo -ne "\b\b\b\b$[$imagesdone*100/$imagecount]% "
done
echo
