# HOW TO RUN

1) deploy 5G
2) deploy capif
3) take access as admin to create a user(invoker/provider)
4) onboard provider and invoker
From ocf-integration git repo:
5) run script that uploads provider's required file to sftp
6) run script that uploads inovker's required file to sftp
7) Then go to provider's repo(e.g. NEF) and deploy it after download from sftp the provider's file
8) Then download the invoker's file from sftp, copy access token and test it using Swagger.
