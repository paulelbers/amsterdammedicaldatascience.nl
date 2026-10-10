#!/usr/bin/env bash
# Downloads every file under images/ and press/ that index.html refers to.
#   bash tools/copy-assets.sh https://amsterdammedicaldatascience.nl
# Stops at the first file that is missing or is not what its name says, so an
# error page is never saved as a picture.
set -euo pipefail
source_url="${1:?give the address of the site to copy from}"

files=$(grep -oE '(src|href)="(images|press)/[^"]+"' index.html | sed -E 's/^[a-z]+="//; s/"$//' | sort -u)
[ -n "$files" ] || { echo "index.html refers to no images or PDFs."; exit 1; }

for f in $files; do
  mkdir -p "$(dirname "$f")"
  curl -fsSL --retry 3 --max-time 60 -o "$f" "$source_url/$f" || { echo "::error::could not download $f"; exit 1; }
  kind=$(file -b --mime-type "$f")
  case "$f" in
    *.pdf) [ "$kind" = "application/pdf" ] || { echo "::error::$f is $kind, not a PDF"; exit 1; } ;;
    *)     case "$kind" in image/*) ;; *) echo "::error::$f is $kind, not an image"; exit 1 ;; esac ;;
  esac
  printf '%-26s %9s bytes  %s\n' "$f" "$(stat -c %s "$f")" "$kind"
done
echo "Copied $(echo "$files" | wc -l) files."
