import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import re

min_confidence_selection=30


def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        if (customLabel['Confidence']>min_confidence_selection):
            print('Label ' + str(customLabel['Name']))
            print('Confidence ' + str(customLabel['Confidence']))
            
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 20)
            fnt1 = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 20)
            ghd_font = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 20)
            draw.text((25,35), "In.AI", fill='#FFFFFF', font=ghd_font)
            draw.text((left,top+50), customLabel['Name'], fill='#00d400', font=fnt1)
            draw.text((left,top), str(round(customLabel['Confidence'],0)), fill='#00d400', font=fnt)
    
            
            #print('Left: ' + '{0:.0f}'.format(left))
            #print('Top: ' + '{0:.0f}'.format(top))
            #print('Label Width: ' + "{0:.0f}".format(width))
            #print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#FFA500', width=1)

    #image.show()
    file_name = re.sub(r"Water//", "", photo)
    image.save("Infer_"+file_name)

def show_custom_labels(model,bucket,photo, min_confidence):
    client=boto3.client('rekognition', region_name='ap-southeast-2')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)
    
    print(response)

    # For object detection use case, uncomment below code to display image.
    display_image(bucket,photo,response)

    return len(response['CustomLabels'])

def main():

    bucket = 'training'
    #my_bucket='inspecta-training'
    #photo='Water/Water AI/v0.0/W.jpg'
    model='arn:aws:rekognition:ap-southeast'
    min_confidence=min_confidence_selection
    s1 = boto3.resource('s3')
    my_bucket = s1.Bucket('inspecta-training')

    for obj in my_bucket.objects.filter(Delimiter='/', Prefix='Water/Water AI/v0.0/moata/moata_images_set1/'):
        #print(obj.key)
    
        if(obj.key.endswith('.jpg')):
              p=obj.key
              
              label_count=show_custom_labels(model,bucket,p,min_confidence)
            
              print("Custom labels detected: " + str(label_count))
    
    

    
if __name__ == "__main__":
    main()
