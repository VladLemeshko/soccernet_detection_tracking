import zipfile

data_path = "data/SoccerNetGS/gamestate-2024/"

"""
with zipfile.ZipFile(data_path + 'train.zip', 'r') as zip_ref:
        zip_ref.extractall(data_path + 'train')
with zipfile.ZipFile(data_path + 'valid.zip', 'r') as zip_ref:
        zip_ref.extractall(data_path + 'validation')
"""

with zipfile.ZipFile(data_path + 'test.zip', 'r') as zip_ref:
        zip_ref.extractall(data_path + 'test')
with zipfile.ZipFile(data_path + 'challenge.zip', 'r') as zip_ref:
        zip_ref.extractall(data_path + 'challenge')

