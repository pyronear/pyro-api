from app.services.bucket.s3 import S3Service

bucket_service = S3Service()
"""bucket_service.create_bucket("mypyroneartest", "eu-west-3")
bucket_service.fetch_buckets()

import random
random_text = str(random.random())  * 5
random_title = str(random.random())
print(random_text)


with open(random_title, 'rb') as f:
    print(f.read())
    f.close()

with open(random_title, 'w') as f:
    f.write(random_text)
    f.close()


bucket_service.upload_file("mypyroneartest", random_title, random_title)
bucket_service.get_uploaded_file("mypyroneartest", random_title, "retrieved_" + random_title)
print("Success")

"""