# 一个非官方的Rotaeno Python库
## 安装
```bash
pip install rotaeno
```
## 使用
> 请自行修改getInfo.py的代码并添加assets文件夹的内容
```python
import rotaeno

userProfile = {
    "server": "history",
    "historyFilePath": "history.json"
}

# 获取Best40
rotaeno.getProcessedData.getBest40(userProfile) # 返回图像地址
rotaeno.getProcessedData.getBest40(userProfile, justDATA=True) # 返回数据
rotaeno.getProcessedData.getBest40(userProfile, justHTML=True) # 返回HTML格式数据
```
