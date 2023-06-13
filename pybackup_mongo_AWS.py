from pymongo import MongoClient
import boto3
import datetime
import gzip
import shutil

def backup_mongo_aws(mongo_uri, db_name, s3_bucket, s3_prefix):
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Generate a timestamp for the backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Create the backup filename
    backup_filename = f"{db_name}_{timestamp}.gz"

    # Backup the database to a gzip-compressed file
    with gzip.open(backup_filename, "wt") as f:
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            for document in collection.find():
                f.write(str(document))

    # Upload backup file to S3
    s3_client = boto3.client("s3")
    s3_key = f"{s3_prefix}/{backup_filename}"
    s3_client.upload_file(backup_filename, s3_bucket, s3_key)

    # Clean up local backup file
    shutil.rmtree(backup_filename)

    print(f"Backup saved to S3: s3://{s3_bucket}/{s3_key}")
