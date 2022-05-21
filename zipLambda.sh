#!/bin/bash
cd package
zip -r ../my-deployment-package.zip .
cd ..
zip -g my-deployment-package.zip lambda_function.py
aws lambda update-function-code --function-name=parkingLot --zip-file=fileb://my-deployment-package.zip