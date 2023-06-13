from pymongo import MongoClient
import boto3
import datetime
import gzip
import shutil
import tempfile
import sys
import json


def load_variables(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def backup_mongo_aws(mongo_uri, db_name, s3_bucket, s3_prefix, backup_list_key):
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

    # Append backup S3 key to the backup list file on S3
    backup_list_content = f"{s3_key}\n"
    s3_client.put_object(Body=backup_list_content, Bucket=s3_bucket, Key=backup_list_key)

    print(f"Backup saved to S3: s3://{s3_bucket}/{s3_key}")


def restore_mongo_aws(mongo_uri, db_name, s3_bucket, s3_key):
    # Download backup file from S3
    s3_client = boto3.client("s3")
    with tempfile.NamedTemporaryFile() as temp_file:
        s3_client.download_file(s3_bucket, s3_key, temp_file.name)

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]

        # Restore the database from the backup file
        with gzip.open(temp_file.name, "rt") as f:
            lines = f.readlines()
            for line in lines:
                document = eval(line)
                collection_name = document.get("_collection")
                collection = db[collection_name]
                collection.insert_one(document)

    print("Database restored successfully.")


def download_backup_list_file(s3_bucket, backup_list_key):
    s3_client = boto3.client("s3")
    with tempfile.NamedTemporaryFile() as temp_file:
        s3_client.download_file(s3_bucket, backup_list_key, temp_file.name)
        with open(temp_file.name, "r") as f:
            backup_list = f.read()
            print("List of Backups:")
            print(backup_list)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a command: backup, restore, or list.")
        sys.exit(1)

    command = sys.argv[1]

    if command == "backup":
        if len(sys.argv) < 3:
            print("Please provide the path to the variable file.")
            sys.exit(1)
        variable_file = sys.argv[2]
        variables = load_variables(variable_file)
        backup_mongo_aws(**variables)
    elif command == "restore":
        if len(sys.argv) < 4:
            print("Please provide the path to the variable file and the S3 key for the backup file to restore.")
            sys.exit(1)
        variable_file = sys.argv[2]
        variables = load_variables(variable_file)
        s3_key = sys.argv[3]
        restore_mongo_aws(**variables, s3_key=s3_key)
    elif command == "list":
        if len(sys.argv) < 3:
            print("Please provide the path to the variable file.")
            sys.exit(1)
        variable_file = sys.argv[2]
        variables = load_variables(variable_file)
        download_backup_list_file(**variables)
    else:
        print("Invalid command. Please use 'backup', 'restore', or 'list'.")
