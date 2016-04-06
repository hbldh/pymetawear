#!/bin/bash
rm -rf out || exit 0;
mkdir out;
cd docs
make html
cd ..
( cd out
 git init
 git config user.name "Henrik Blidh"
 git config user.email "henrik.blidh@nedomkull.com"
 cp -r ../docs/build/html/* .
 git add .
 git commit -m "Deployed to Github Pages"
 git push --force --quiet "https://${GH_TOKEN}@${GH_REF}" master:gh-pages > /dev/null 2>&1
)
