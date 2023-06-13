# pymongo_backup_AWS

The script connects to the MongoDB instance using the provided URI, performs the backup by saving each document to a gzip-compressed file,
uploads the backup file to the specified S3 bucket, and appends the backup S3 key to the backup list file stored on S3.
The script also provides a restore function that downloads the backup file from S3 and restores the database based on the documents in the file.
Additionally, it includes a function to download the backup list file from S3 and display its contents.
Uses an external json file, so you can have a different variable file for each enviroment.

Libs:pymongo, boto3

Replace the mongo_uri, db_name, s3_bucket, s3_prefix, and backup_list_key variables with the appropriate values.

Usage:

Backup the database:

	python pymongobackup backup variables.json

Restore the database:

	python pymongobackup restore variables.json

List backups:
	
	python pymongobackup list variables.json
