from flask import Flask,render_template,request
import json
import os
import cv2
import numpy as np
import shutil
import time
import pytesseract as py
import urllib.parse
print ("starting!!!!!!!")
IMAGE_UPLOADS = "./static/images"
OUTPUT_UPLOADS= "./static/images/output"

import os, sys
base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = os.path.join(sys._MEIPASS)

app=Flask(__name__,
        static_folder=os.path.join(base_dir, 'static'),
        template_folder=os.path.join(base_dir, 'templates'))

@app.route('/')
def home():
	# print ("BACKKKKKKKK")
	pass
	return render_template('image.html')

@app.route('/uploadimage',methods = ['GET', 'POST'])
def uploadimage():
	 # image = request.args.get("image")
	 # print (image,os.path.join(IMAGE_UPLOADS, image))
	 # Image.save(os.path.join(IMAGE_UPLOADS, image))

    print("Image saving")	 
    if request.method == 'POST':
        f = request.files['image']
        # print ("hi",f)
        for file in os.listdir(IMAGE_UPLOADS):
            if file != "output":
            	os.remove(os.path.join(IMAGE_UPLOADS,file))
        for file in os.listdir(OUTPUT_UPLOADS):
            os.remove(os.path.join(OUTPUT_UPLOADS,file))
        # f.save(secure_filename(f.filename))
        path=os.path.join(IMAGE_UPLOADS, f.filename)
        f.save(os.path.join(IMAGE_UPLOADS, f.filename))
        shutil.copyfile(os.path.join(IMAGE_UPLOADS, f.filename), os.path.join(OUTPUT_UPLOADS, f.filename))
        # print ("image path-------",path)
        return render_template('class.html',path=path,filename=f.filename)
    else: 
    	path=request.args.get('path')
    	for file in os.listdir(IMAGE_UPLOADS):
            if file != "output":
            	path=os.path.join(IMAGE_UPLOADS,file)
            	filename=file

    	return render_template('class.html',path=path,filename=filename)
    	
@app.route('/final',methods=['GET','POST'])  
def final():
	data=request.data.decode("utf-8")
	# print(data)
	
	ls=data.split('&')
	val = {k:v for k,v in (x.split('=') for x in ls) }
	# print (val)
	erode=int(val['erode'])
	dilate=int(val['dilate'])
	blur=int(val['blur'])
	width=int(val['width'])
	height=int(val['height'])
	interpolation=str(val['interpolation'])
	imgname=str(val['image'])

	path=os.path.join(IMAGE_UPLOADS,imgname)
	
	# print ("The image path is", path)
	img=cv2.imread(path)

	image_name=imgname.split('.')
	millis = str(round(time.time()))
	imgname=image_name[0]+millis+'.'+image_name[1]

##Blur
	img = cv2.blur(img, (blur,blur))

##Resize
	interpolation="cv2."+interpolation
	img = cv2.resize(img, None, fx=width, fy=height) 

##Erode
	kernel = np.ones((erode,erode), np.uint8) 
	img = cv2.erode(img, kernel, iterations=1) 
##Dilate

	kernel = np.ones((dilate,dilate), np.uint8) 
	img = cv2.dilate(img, kernel, iterations=1) 
	
	for file in os.listdir(OUTPUT_UPLOADS):
	 	os.remove(os.path.join(OUTPUT_UPLOADS,file))

	for file in os.listdir(OUTPUT_UPLOADS):
	 	os.remove(os.path.join(OUTPUT_UPLOADS,file))

	cv2.imwrite(os.path.join(OUTPUT_UPLOADS,imgname),img)
	# print ("The image path is***********", imgname)
	finalpath=os.path.join(OUTPUT_UPLOADS,imgname)
	result=finalpath

	return json.dumps({'result':result})

@app.route('/clean',methods=["POST","GET"])
def clean():
	for file in os.listdir(OUTPUT_UPLOADS):
	 	os.remove(os.path.join(OUTPUT_UPLOADS,file))

	
	data=request.data.decode("utf-8")
	# print(data)
	
	ls=data.split('&')
	val = {k:v for k,v in (x.split('=') for x in ls) }
	# print (val)
	imgname=str(val['image']) 	
	finalpath=os.path.join(IMAGE_UPLOADS,imgname)
	shutil.copyfile(os.path.join(IMAGE_UPLOADS, imgname), os.path.join(OUTPUT_UPLOADS, imgname))
	result=finalpath 	
	return json.dumps({'result':result})

@app.route('/submit',methods=["POST","GET"])
def submit():
	
	erode=request.form.get('Erode')
	dilate=request.form.get('Dilate')
	blur=request.form.get('Blur')
	width=request.form.get('width')
	height=request.form.get('height')


	for file in os.listdir(OUTPUT_UPLOADS):
		imgpath=os.path.join(OUTPUT_UPLOADS,file)
		# print (imgpath)
		img=cv2.imread(os.path.join(OUTPUT_UPLOADS,file))
		
	text=py.image_to_string(img)
	return render_template("submit.html",erode=erode,dilate=dilate,blur=blur,width=width,height=height,imgpath=imgpath,text=text)	

if __name__ == '__main__':
	print ("Lets go")
	app.run(host="0.0.0.0",port=8000,debug=True)
