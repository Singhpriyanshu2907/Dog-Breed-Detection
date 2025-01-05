import sys,os
from Dog_Breed_Detection.pipeline.training_pipeline import TrainPipeline
from Dog_Breed_Detection.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template,Response
#from flask_cors import CORS, cross_origin


obj = TrainPipeline()
obj.run_pipeline()