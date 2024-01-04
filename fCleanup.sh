#!/bin/bash
echo "Cleaning Coverage-Branches ..."
rm -rf ./results-verified/coverage-branches_*/Coverage-Branches/*.yml/*_*
rm ./coverage-branches_*/coverage-branches_*_res.diff.csv
rm ./coverage-branches_*/coverage-branches_*_res.diff.html

echo "Cleaning Coverage-Error-Call ..."
rm -rf ./results-verified/coverage-error-call_*/Coverage-Error-Call/*.yml/*_*

echo "${0} Done ..... !!!"
exit 0
