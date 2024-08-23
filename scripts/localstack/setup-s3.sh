#!/usr/bin/env bash
awslocal s3 mb s3://bucket
echo -n "" > my_file
awslocal s3 cp my_file s3://bucket/my_file
