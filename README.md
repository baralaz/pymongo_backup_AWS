# pymongo_backup_AWS
backup and restore a MongoDB database hosted on AWS using Python

Usage:

export:

  'mongo_uri = "mongodb://username:password@host:port"'
  'db_name = "mydatabase"'
  's3_bucket = "your-s3-bucket"'
  's3_prefix = "backup"'
  's3_key = "backup/mydatabase_22220101120000.gz"'

Backup the database:

  backup_mongo_aws(mongo_uri, db_name, s3_bucket, s3_prefix)

Restore the database:

  restore_mongo_aws(mongo_uri, db_name, s3_bucket, s3_key)
