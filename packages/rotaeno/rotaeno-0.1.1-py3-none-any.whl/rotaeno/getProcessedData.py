from . import getInfo
from . import utils
from . import database
from . import config
import json
import time
import io
import traceback
import math
import scipy.stats
import numpy
import random
from concurrent.futures import ThreadPoolExecutor

def getPlayerInfo(userProfile, justDATA=False, justHTML=False):
    userdata = getInfo.getPlayerUserData(userProfile)
    save = getInfo.getSave(userProfile)
    
    results = userdata
    results["playerRating"] = round(save[1]["playerRating"], 4)
    results["TotalPlayCount"] = save[1]["playerPlayRecords"]["TotalPlayCount"]
    results["PlayCountI"] = save[1]["playerPlayRecords"]["PlayCountI"]
    results["PlayCountIi"] = save[1]["playerPlayRecords"]["PlayCountIi"]
    results["PlayCountIii"] = save[1]["playerPlayRecords"]["PlayCountIii"]
    results["PlayCountIv"] = save[1]["playerPlayRecords"]["PlayCountIv"]
    results["PlayTotalFc"] = save[1]["playerPlayRecords"]["TotalFc"]
    results["PlayTotalAp"] = save[1]["playerPlayRecords"]["TotalAp"]
    results["PlayTotalApp"] = save[1]["playerPlayRecords"]["TotalApp"]
    results["PlayTotalEx"] = save[1]["playerPlayRecords"]["TotalEx"]
    results["PlayTotalExPlus"] = save[1]["playerPlayRecords"]["TotalExPlus"]
    results["Combo"] = {}
    results["Combo"]["Tap"] = save[1]["playerPlayRecords"]["Tap"]
    results["Combo"]["Slide"] = save[1]["playerPlayRecords"]["Slide"]
    results["Combo"]["Flick"] = save[1]["playerPlayRecords"]["Flick"]
    results["Combo"]["Catch"] = save[1]["playerPlayRecords"]["Catch"]
    results["Combo"]["Rotate"] = save[1]["playerPlayRecords"]["Rotate"]
    results["Combo"]["Status"] = {}
    results["Combo"]["Status"]["Early"] = save[1]["playerPlayRecords"]["Early"]
    results["Combo"]["Status"]["Late"] = save[1]["playerPlayRecords"]["Late"]
    results["Combo"]["Status"]["Good"] = save[1]["playerPlayRecords"]["Good"]
    results["Combo"]["Status"]["Miss"] = save[1]["playerPlayRecords"]["Miss"]
    results["Combo"]["Status"]["Perfect"] = save[1]["playerPlayRecords"]["Perfect"]
    results["Combo"]["Status"]["PerfectPlus"] = save[1]["playerPlayRecords"]["PerfectPlus"]
    
    # 自定义背景 / 头像 / 角色 (这就是特权) (阶级(?))
    if results["playerName"] == "Terlity":
        results["backgroundID"] = "terlity"
        results["avatarID"] = "terlity"
        results["characterID"] = "empty"
    
    if justDATA:
        return results
    with open(f"{config.assetsDir}/html/me_info.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(results, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((900, 900), 1.5, html_data=html, isHTML=True)

def getFriendAndFollow(userProfile, justDATA=False, justHTML=False):
    results = getInfo.getAllFollowDatas(userProfile)
    
    if justDATA:
        return results
    with open(f"{config.assetsDir}/html/friend_info.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(results, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((1400, 1100), 1.5, html_data=html, isHTML=True)

def getFollowPlayerData(userProfile, shortID, justDATA=False, justHTML=False):
    player_data = {}
    for i in getInfo.getAllFollowDatas(userProfile):
        if i["shortID"] == shortID:
            player_data = i
            break
    
    if justDATA:
        return player_data
    with open(f"{config.assetsDir}/html/friend_code.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(player_data, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((900, 900), 1.5, html_data=html, isHTML=True)

def getFriendBest40(userProfile, shortID, justDATA=False, justHTML=False):
    player_data = {}
    for i in getInfo.getAllFollowDatas(userProfile):
        if i["shortID"] == shortID and i["isFriend"]:
            player_data = i
            break
    if player_data == {}:
        return ""
    return getBest40(utils.shortIDToUserProfile(shortID), justDATA, justHTML)

def getBest40(userProfile, justDATA=False, justHTML=False):
    results = getInfo.getSave(userProfile)
    results[0] = sorted(results[0], key=lambda x: x["rating"], reverse=True)[:40]
    
    if justDATA:
        return results
    with open(f"{config.assetsDir}/html/b40.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(results, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((1400, 1310), 1.5, html_data=html, isHTML=True)

def getBest40RatingChart(userProfile):
    data = getBest40(userProfile, justDATA=True)[0]
    ratings = [round(x["rating"], 4) for x in data]
    song_names = [x["songName"] for x in data]
    return utils.draw_bar_chart(ratings, song_names, save_path=f"{config.tmpDir}/{time.time()}.png", title="Best40 Rating曲线分布")

def getSongsStatus(userProfile, songStatus, justDATA=False, justHTML=False):
    # songStatus [NONE  FC  AP  APP  CLEAR  NOTCLEAR]
    songStatus = list({x for x in [x.replace(" ", "") for x in songStatus.split("/")]})
    getAll = getInfo.getSave(userProfile)
    getAll[1]["songStatus"] = '/'.join(map(str, songStatus))
    results = [[], getAll[1]]
    for songData in getAll[0]:
        if songData["songStatus"] in songStatus:
            if not songData in results[0]:
                results[0].append(songData)
        if "CLEAR" in songStatus and songData["isCleared"]:
            if not songData in results[0]:
                results[0].append(songData)
        if "NOTCLEAR" in songStatus and not songData["isCleared"]:
            if not songData in results[0]:
                results[0].append(songData)
    results[0] == sorted(results[0], key=lambda x: x["rating"], reverse=True)
    
    if justDATA:
        return results
    with open(f"{config.assetsDir}/html/songs_status.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(results, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((1400, 1310), 3, html_data=html, isHTML=True)

def getSong(userProfile, song_id, justDATA=False, justHTML=False):
    # ==========================================================
    # 重点关注(大学)
    gaoxiao_211 = False
    if song_id == "211大学":
        gaoxiao_211 = True
        song_id = "abstruse-dilemma"
    # ==========================================================
    
    data = {}
    getAll = getInfo.getSave(userProfile)
    for song_data in getAll[0]:
        if song_data["songID"] == song_id:
            data[song_data["songLevelName"]] = {"songData": song_data,
                                                "artist": database.songData.getSong(song_id)["artist"]}
    results = [
                {
                    "songID": song_id,
                    "songName": data["I"]["songData"]["songName"],
                    "songArtist": data["I"]["artist"],
                    "songData": data
                },
                getAll[1]
            ]
    """
    results = [
        0: {
            "songID": songID,
            "songName": songName,
            "songArtist": songArtist,
            "songData": {
                "I": {
                    "songData": {
                        "score": score,
                        "level": level,
                        "sourceRating": sourceRating,
                        "songStatus": songStatus,
                        "isCleared": isCleared,
                    },
                    "artist": artist
                }, ...
            }
        },
        1: PlayerInfo
    ]
    """
    
    if justDATA:
        return results
    # ==========================================================
    # 重点关注(大学)
    if gaoxiao_211:
        results[0]["songID"] = f"211大学_{random.randint(1, 2)}"
    # ==========================================================
    with open(f"{config.assetsDir}/html/song.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(results, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((1400, 1100), 1.5, html_data=html, isHTML=True)

def getSongAllScore(song_id, needScoreList=False, needZero=False):
    allScores = {"I": [0, 0], "II": [0, 0], "III": [0, 0], "IV": [0, 0], "IV_Alpha": [0, 0]}
    _allScores = {"I": [], "II": [], "III": [], "IV": [], "IV_Alpha": []}
    for objectID in getInfo.getAllUsersObjectID():
        tmp = getSong({"server": "local", "sign": "", "session": "", "objectId": objectID}, song_id, justDATA=True)
        for level in tmp[0]["songData"]:
            score = tmp[0]["songData"][level]["songData"]["score"]
            if score == 0 and not needZero: continue
            if needScoreList:
                _allScores[level].append(score)
                continue
            allScores[level][0] += 1
            allScores[level][1] += score
    return _allScores if needScoreList else  allScores

def getSongVarianceScore(song_id, needScoreList=False): # 获取方差
    allScores = getSongAllScore(song_id, needScoreList=True)
    results = {}
    for level in allScores: # 先用这个, 如果出错就用 levelScore, levelAverage in zip(allScores, getAverage)
        if len(allScores[level]) == 0:
            results[level] = 0
            continue
        results[level] = numpy.var(allScores[level])
    if needScoreList:
        return [allScores, results]
    return results

def getSongAverageScore(song_id): # 获取平均值
    allScores = getSongAllScore(song_id)
    results = {}
    for level in allScores:
        if allScores[level][0] == 0:
            results[level] = 0
        else:
            results[level] = numpy.mean(allScores[level][1], dtype=int)
            if results[level] > 1010000: results[level] = 1010000
    return results

def getSongStdScore(song_id, scores): # 获取标准差
    getVariances = getSongVarianceScore(song_id, needScoreList=True)
    getAverage = getSongAverageScore(song_id)
    result = {}
    for level in scores: #  先用这个, 如果出错就用 scores, levelVariance, levelAverage in zip(scores, getVariances[1], getAverage)
        mean = getAverage[level]
        variance = getVariances[1][level]
        target_variance = (scores[level] - mean) ** 2
        result[level] = math.sqrt((variance * len(scores) + target_variance) / (len(scores) - 1))
    return result

def getSongSKScore(song_id): # 获取偏度
    getScores = getSongAllScore(song_id, needScoreList=True)
    result = {}
    for level in getScores:
        result[level] = scipy.stats.skew(getScores[level])
    return result

def getSongKurScore(song_id): # 获取峰度
    getScores = getSongAllScore(song_id, needScoreList=True)
    result = {}
    for level in getScores:
        result[level] = scipy.stats.kurtosis(getScores[level])
    return result

def getSongRatingRealRangeData(userProfile, songRatingReal, justDATA=False, justHTML=False):
    data = []
    getAll = getInfo.getSave(userProfile)
    songNeed = database.songData.getSongsRatingRealRange(songRatingReal[0], songRatingReal[1])
    
    for song_data in getAll[0]:
        for song in songNeed:
            if song["id"] == song_data["songID"] and song_data["songLevelName"] in song["levels"] and song_data["score"] != 0:
                data.append(song_data)
    
    data = sorted(data, key=lambda x: x["sourceRating"], reverse=True)
    getAll[0] = data

    if justDATA:
        return getAll
    with open(f"{config.assetsDir}/html/song_ratingreal_range.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(getAll, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((1400, 1310), 3, html_data=html, isHTML=True)

def getSongHistory(userProfile, song_id, justDATA=False):
    getInfo.getSave(userProfile)
    histories = []
    for data in utils.sorted_json_files(f"{config.savesDir}/{userProfile['objectId']}/save", reverse=False, needTimestamp=True):
        timestamp, filePath = int(round(float(data[0]), 0)), data[1]
        histories.append((timestamp, getSong({"server": "history", "historyFilePath": filePath, "sign": "", "session": "", "objectId": ""}, song_id, justDATA=True)[0]))
    LevelScore = {}
    for timestamp, data in histories:
        for level in data["songData"]:
            if level not in LevelScore:
                LevelScore[level] = []
            LevelScore[level].append({
                "timestamp": timestamp,
                "songScore": data["songData"][level]["songData"]["score"],
                "songRating": data["songData"][level]["songData"]["sourceRating"],
                "songStatus": data["songData"][level]["songData"]["songStatus"],
                "songIsCleared": data["songData"][level]["songData"]["isCleared"]
            })
    try:
        for level in LevelScore:
            unique_lst = []
            for x in LevelScore[level]:
                for y in unique_lst:
                    if y["songScore"] >= x["songScore"]:
                        break
                else:
                    unique_lst.append(x)
            LevelScore[level] = unique_lst
    except Exception as e:
        traceback.print_exc()
        LevelScore = {}

    if justDATA:
        return LevelScore
    _save_path = f"{config.tmpDir}/{time.time()}"
    save_paths = []
    for level in LevelScore:
        save_paths.append(f"{_save_path}-{level}.png")
        utils.draw_line_datatime(LevelScore[level], save_paths[-1], f"{level.replace('_', ' ')} Score Trend", "Score")
    return save_paths

def getRatingTrend(userProfile, justDATA=False):
    getInfo.getSave(userProfile)
    histories = []
    for data in utils.sorted_json_files(f"{config.savesDir}/{userProfile['objectId']}/save", reverse=False, needTimestamp=True):
        timestamp, filePath = int(round(float(data[0]), 0)), data[1]
        histories.append((timestamp, getBest40({"server": "history", "historyFilePath": filePath, "sign": "", "session": "", "objectId": ""}, justDATA=True)[1]["playerRating"]))
    
    if justDATA:
        return histories
    return utils.draw_line_datatime(histories, f"{config.tmpDir}/{time.time()}.png", "Rating Trend", "Rating")

def getSongFollowerRanking(userProfile, song_id, vicinity=None, rangeNum=4, justDATA=False, justHTML=False):
    result = {"I": [], "II": [], "III": [], "IV": []}
    # 这个getAllFollowDatas只能获取到关注者的数据, 没有自己的分数
    for user in getInfo.getAllFollowDatas(userProfile):
        for level in result:
            result[level].append({
                "playerName": user["playerName"],
                "avatarID": user["avatarID"],
                "songScore": user["songScores"][song_id][level.lower()],
                "isFriend": user["isFriend"],
                "type": ("follower", user["shortID"])
            })
    # 在这里添加用户自己的数据
    getSongData = getSong(userProfile, song_id, justDATA=True)
    for level in getSongData[0]["songData"]:
        if "Alpha" in level: continue
        result[level].append({
            "playerName": getSongData[1]["playerName"],
            "avatarID": getSongData[1]["playerAvatar"],
            "songScore": getSongData[0]["songData"][level]["songData"]["score"],
            "isFriend": True,
            "type": ("user", "114514")
        })
    # 处理这些数据
    for level in result:
        result[level] = sorted(result[level], key=lambda x: x['songScore'], reverse=True)
        for i in range(len(result[level])):
            result[level][i]["rank"] = i + 1
        if vicinity is not None:
            if vicinity == "user":
                b_index = next((index for index, item in enumerate(result[level]) if item["type"][0] == "user"), None)
                result[level] = result[level][max(b_index - rangeNum, 0):min(b_index + rangeNum + 1, len(result[level]))] if b_index is not None else []
            elif len(vicinity) == 2 and vicinity[0] == "follower":
                b_index = next((index for index, item in enumerate(result[level]) if item["type"][0] == "follower" and item["type"][1].lower() == vicinity[1].lower()), None)
                result[level] = result[level][max(b_index - rangeNum, 0):min(b_index + rangeNum + 1, len(result[level]))] if b_index is not None else []
        
    if justDATA:
        return result
    with open(f"{config.assetsDir}/html/friend_song_score_ranking.html", "r", encoding="utf-8") as f:
        html = f.read()
    htmls = []
    for level in result:
        htmls.append(html.replace("/{{{data}}}/", json.dumps({"data": result[level], "level": level, "songName": getSongData[0]["songName"]}, indent=4, ensure_ascii=False)))
    if justHTML:
        return htmls
    with ThreadPoolExecutor() as executor:
        return list(executor.map(lambda html: utils.render_html_to_jpg((500, 1310), 3, html_data=html, isHTML=True), htmls))

def getAllUserSaveRanking(sorting, vicinity=None, rangeNum=4, maxNum=20, justDATA=False, justHTML=False):
    allUserSaves = getInfo.getAllUsersSave(withObjectID=True)
    result = []
    for user in allUserSaves:
        if sorting == "rating":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": round(user[0][1]["playerRating"], 4),
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno Rating Ranking"
        elif sorting == "fc":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["TotalFc"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno FC Ranking"
        elif sorting == "ap":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["TotalAp"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno AP Ranking"
        elif sorting == "ap+" or sorting == "app":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["TotalApp"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno APP Ranking"
        elif sorting == "miss":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["Miss"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno Miss Ranking"
        elif sorting == "good":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["Good"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno Good Ranking"
        elif sorting == "perfect":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["Perfect"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno Perfect Ranking"
        elif sorting == "perfect+":
            result.append({
                "playerName": user[0][1]["playerName"],
                "sorting": user[0][1]["playerPlayRecords"]["PerfectPlus"],
                "playerAvatar": user[0][1]["playerAvatar"],
                "objectId": user[1]
            })
            title = "Rotaeno PerfectPlus Ranking"
        elif sorting[0] == "song":
            songID = sorting[1]
            songLevel = sorting[2]
            # print(user)
            for song in user[0][0]:
                if song["songID"] == songID and song["songLevelName"] == songLevel and song["score"] != 0:
                    result.append({
                        "playerName": user[0][1]["playerName"],
                        "sorting": song["score"],
                        "playerAvatar": user[0][1]["playerAvatar"],
                        "objectId": user[1]
                    })
            title = f"Rotaeno {sorting[1]} ({songLevel.replace('_', ' ')}) Ranking"
    result = sorted(result, key=lambda x: x["sorting"], reverse=True)
    for i in range(len(result)):
        result[i]["rank"] = i + 1
    if vicinity is not None: # 使用objectID判断(me)
        b_index = next((index for index, item in enumerate(result) if item["objectId"] == vicinity), None)
        result = result[max(b_index - rangeNum, 0):min(b_index + rangeNum + 1, len(result))] if b_index is not None else []
    for i in range(len(result)):
        del result[i]["objectId"]
    result = result[:maxNum]
    
    result = {
        "data": result,
        "title": title
    }
    
    if justDATA:
        return result
    with open(f"{config.assetsDir}/html/user_ranking.html", "r", encoding="utf-8") as f:
        html = f.read()
        html = html.replace("/{{{data}}}/", json.dumps(result, indent=4, ensure_ascii=False))
    if justHTML:
        return html
    return utils.render_html_to_jpg((500, 1100), 1.5, html_data=html, isHTML=True)

def getSongPreviewByteIO(song_id):
    with open(f"{config.assetsDir}/song/preview/{song_id}.wav", "rb") as f: return io.BytesIO(f.read())

updateSave = getInfo._getSave
getLatestSaveTimestamp = getInfo.getLatestSaveTimestamp
