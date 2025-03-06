import os

current_dir = os.path.dirname(os.path.abspath(__file__))

savesDir = os.path.join(current_dir, "saves")
assetsDir = os.path.join(current_dir, "assets")
tmpDir = os.path.join(current_dir, "tmp")
songAliasDBPath = os.path.join(current_dir, "db", "songAlias.db")
songDataDBPath = os.path.join(current_dir, "db", "songs.db")

scorePredictorModelPath = os.path.join(current_dir, "model", "score_predictor.pth")
