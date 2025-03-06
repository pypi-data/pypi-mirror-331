from . import config
from . import getProcessedData
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import os

# 定义神经网络模型
class ScorePredictor(nn.Module):
    def __init__(self):
        super(ScorePredictor, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(2, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        self.is_trained = False
    
    def forward(self, x):
        return self.model(x)
    
    def save_model(self, path):
        if not self.is_trained:
            raise ValueError("模型尚未训练，无法保存")
        torch.save(self.state_dict(), path)
    
    def load_model(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"模型文件 {path} 不存在")
        self.load_state_dict(torch.load(path))
        self.is_trained = True
    
    def predict(self, song_level, player_rating):
        if not self.is_trained:
            raise ValueError("模型尚未训练，无法进行预测")
        
        self.eval()
        with torch.no_grad():
            x = torch.FloatTensor([[song_level, player_rating]])
            score = self.model(x)
            return score.item()

def load_real_data():
    with open('AIdata.json', 'r') as f:
        data = json.load(f)
    
    scores = np.array(data[0])
    player_ratings = np.array(data[1])
    song_levels = np.array(data[2])
    
    # 过滤掉无效的分数（小于0或大于20.5的分数）
    valid_indices = (scores >= 0) & (scores <= 20.5)
    scores = scores[valid_indices]
    player_ratings = player_ratings[valid_indices]
    song_levels = song_levels[valid_indices]
    
    # 为高分数据添加随机噪声
    high_scores_mask = scores > 20.0
    noise = np.random.uniform(0.01, 0.05, size=scores[high_scores_mask].shape)
    scores[high_scores_mask] -= noise
    
    # 归一化分数到20.5满分
    max_score = 20.5
    scores = np.minimum(scores, max_score)
    
    # 确保数据维度正确
    scores = scores.reshape(-1, 1)
    player_ratings = player_ratings.reshape(-1, 1)
    song_levels = song_levels.reshape(-1, 1)
     
    return song_levels, player_ratings, scores

# 训练模型
def train_model(model, n_epochs=10000):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=0.01)
    
    song_levels, player_levels, scores = load_real_data()
    
    X = torch.FloatTensor(np.hstack([song_levels, player_levels]))
    y = torch.FloatTensor(scores)
    
    if len(X.shape) == 1:
        X = X.view(-1, 2)
    if len(y.shape) == 1:
        y = y.view(-1, 1)
    
    model.train()
    for epoch in range(n_epochs):
        outputs = model(X)
        loss = criterion(outputs, y)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{n_epochs}], Loss: {loss.item():.4f}')
    
    model.is_trained = True


def score(userProfile, level):
    model = ScorePredictor()
    model.load_model(config.scorePredictorModelPath)
    rating = getProcessedData.getPlayerInfo(userProfile, justDATA=True)["playerRating"]
    return int(model.predict(level, rating) * 50000)


def main():
    model = ScorePredictor()
    
    print("开始训练模型...")
    train_model(model)
    
    model.save_model('score_predictor.pth')
    print("模型已保存到 score_predictor.pth")
    
    new_model = ScorePredictor()
    new_model.load_model('score_predictor.pth')
    
    print("\n测试模型...")
    song_level = 14.2
    player_rating = 17.42
    predicted_score = new_model.predict(song_level, player_rating) * 50000
    print(f"歌曲难度: {song_level}, 玩家等级: {player_rating}")
    print(f"预测分数: {predicted_score:.2f}")

if __name__ == "__main__":
    main()

# AIdata.json
# [
#   [score / 50000 ...],
#   [playerRating ...]
#   [songLevel ...]
# ]
