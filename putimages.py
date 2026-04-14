import boto3

# Specify region (IMPORTANT)
s3 = boto3.resource('s3', region_name='us-east-1')

# Images list
images = [
    ('image1.jpg','Prasad'),
    ('image2.jpg','Ramya'),
    ('image3.jpg','Chandrika'),
    ('image4.jpg','Sasi Priya'),
    ('image5.jpg','Bhavana'),
    ('image6.jpg','Spandhana'),
    ('image7.jpg','Babitha'),
    ('image8.jpg','Sapanthi'),
]

# Upload images to S3
for image in images:
    with open(image[0], 'rb') as file:
        obj = s3.Object('studentfaces-1', 'images/' + image[0])
        response = obj.put(
            Body=file,
            Metadata={'fullname': image[1]}   
        )
        print(f"Uploaded {image[0]} successfully")