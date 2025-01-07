import os,sys, zipfile
import yaml
import shutil
from Dog_Breed_Detection.utils.main_utils import read_yaml_file
from Dog_Breed_Detection.logger import logging
from Dog_Breed_Detection.exception import AppException
from Dog_Breed_Detection.entity.config_entity import ModelTrainerConfig
from Dog_Breed_Detection.entity.artifacts_entity import ModelTrainerArtifact



class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
    ):
        self.model_trainer_config = model_trainer_config


    

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        logging.info("Entered initiate_model_trainer method of ModelTrainer class")

        try:
            logging.info("Unzipping data")
            with zipfile.ZipFile('dataset.zip', 'r') as zip_ref:
                zip_ref.extractall('.')
            os.remove('dataset.zip')

            with open("data.yaml", 'r') as stream:
                num_classes = str(yaml.safe_load(stream)['nc'])

            model_config_file_name = self.model_trainer_config.weight_name.split(".")[0]
            print(model_config_file_name)

            config = read_yaml_file(f"yolov5/models/{model_config_file_name}.yaml")
            config['nc'] = int(num_classes)

            with open(f'yolov5/models/custom_{model_config_file_name}.yaml', 'w') as f:
                yaml.dump(config, f)

            os.system(f"cd yolov5 && python train.py --img 416 --batch {self.model_trainer_config.batch_size} --epochs {self.model_trainer_config.no_epochs} --data ../data.yaml --cfg ./models/custom_{model_config_file_name}.yaml --weights {self.model_trainer_config.weight_name} --name yolov5s_results --cache")
            shutil.copy("yolov5/runs/train/yolov5s_results/weights/best.pt", "yolov5/")
            os.makedirs(self.model_trainer_config.model_trainer_dir, exist_ok=True)
            shutil.copy("yolov5/runs/train/yolov5s_results/weights/best.pt", self.model_trainer_config.model_trainer_dir)

            # Cleanup
            shutil.rmtree('yolov5/runs', ignore_errors=True)
            for folder in ['train', 'test', 'valid']:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
            if os.path.exists("data.yaml"):
                os.remove("data.yaml")

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path="yolov5/best.pt",
            )

            logging.info("Exited initiate_model_trainer method of ModelTrainer class")
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact

        except Exception as e:
            raise AppException(e, sys)