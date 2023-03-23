import io
import json
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request


app = Flask(__name__)
imagenet_class_index = json.load(open('/home/ant/imagenet_class_index.json'))

model = models.densenet121(pretrained=True)
model.eval()

def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(500),
                                        transforms.CenterCrop(450),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.5, 0.5, 0.5],
                                            [0.5, 0.5, 0.5])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)

def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        return jsonify({'class_id': class_id, 'class_name': class_name})

# /classes로 요청을 보내면, 클래스 리스트를 보여주는 api
@app.route('/classes', methods=['GET'])
def classes():
    if request.method == 'GET':
        return jsonify(imagenet_class_index)

# /로 요청을 보내면, 홈페이지를 보여주는 api
# 이미지를 업로드하고, predict 버튼을 누르면, /predict로 요청을 보내고, 결과를 받아온다.
# 결과와 업로드한 이미지를 보여준다.
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="/predict" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''

if __name__ == '__main__':
    app.run()