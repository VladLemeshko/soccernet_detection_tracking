import os

dataset_path = "dataset"

# Создание data.yaml
data_yaml_path = os.path.join(dataset_path, "data.yaml")
with open(data_yaml_path, "w") as f:
    f.write("path: /home/student/lemeshko/cv_project/dataset\n")
    f.write("train: /home/student/lemeshko/cv_project/dataset/train\n")
    f.write("val: /home/student/lemeshko/cv_project/dataset/validation\n")
    f.write("test: /home/student/lemeshko/cv_project/dataset/test\n")
    f.write("nc: 4\n")  # Количество классов
    f.write("names:\n")
    f.write("    0: player\n")
    f.write("    1: goalkeeper\n")
    f.write("    2: referee\n")
    f.write("    3: ball")