#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import time
from http import HTTPStatus
from dashscope.audio.asr import Transcription
from openai import OpenAI

def get_video_info(bvid):
    """获取视频信息，提取cid"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            # 获取第一个分P的cid
            cid = data["data"]["cid"]
            title = data["data"]["title"]
            return cid, title
    raise Exception(f"获取视频信息失败: {response.text}")

def get_audio_url(bvid, cid):
    """获取音频流URL"""
    url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&fnval=16"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/video/{bvid}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0 and "data" in data and "dash" in data["data"] and "audio" in data["data"]["dash"]:
            # 获取音频流列表中的第一个（通常是最高质量）
            audio_url = data["data"]["dash"]["audio"][0]["baseUrl"]
            return audio_url
    raise Exception(f"获取音频流失败: {response.text}")

def download_audio(url, output_path="audio.m4s"):
    """下载音频文件"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com"
    }
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return output_path
    raise Exception(f"下载音频失败: {response.status_code}")

def upload_to_catbox(file_path):
    """上传文件到catbox.moe获取URL"""
    files = {
        'reqtype': (None, 'fileupload'),
        'fileToUpload': ('audio.m4s', open(file_path, 'rb')),
    }
    response = requests.post('https://catbox.moe/user/api.php', files=files)
    if response.status_code == 200:
        return response.text.strip()  # 返回文件URL
    else:
        raise Exception(f"上传失败: {response.status_code}")

def upload_to_tmpfiles(file_path):
    """上传文件到tmpfiles.org获取URL"""
    files = {'file': open(file_path, 'rb')}
    response = requests.post('https://tmpfiles.org/api/v1/upload', files=files)
    if response.status_code == 200:
        data = response.json()
        file_url = data['data']['url'].replace('/dl/', '/api/v1/dl/')
        return file_url
    else:
        raise Exception(f"上传失败: {response.status_code}")

def transcribe_audio(audio_url):
    """使用DashScope进行语音识别"""
    transcribe_response = Transcription.async_call(
        model='paraformer-v2',
        file_urls=[audio_url],
        language_hints=['zh', 'en']
    )

    while True:
        if transcribe_response.output.task_status in ['SUCCEEDED', 'FAILED']:
            break
        time.sleep(2)  # 等待2秒再检查状态
        transcribe_response = Transcription.fetch(task=transcribe_response.output.task_id)

    if transcribe_response.status_code == HTTPStatus.OK:
        if transcribe_response.output.task_status == 'SUCCEEDED':
            transcription_url = transcribe_response.output.results[0]['transcription_url']
            response = requests.get(transcription_url)
            if response.status_code == 200:
                transcription_result = response.json()
                return transcription_result['transcripts'][0]['text']
        else:
            raise Exception(f"识别任务失败: {transcribe_response.output.task_status}")
    raise Exception(f"识别请求失败: {transcribe_response.status_code}")

def generate_haiku(text):
    """根据识别文本生成俳句"""
    client = OpenAI(
        api_key=dashscope.api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    completion = client.chat.completions.create(
        model="deepseek-v3",  # 可按需更换模型
        messages=[
            {'role': 'system', 'content': '你是一个俳句诗人，擅长创作俳句，必须严格遵守俳句的格式：第一句为5个字，第二句为7个字，第三句为5个字，句子之间插入换行符。我将会给你一系列从音视频里提取的文本，请根据这些文本创作一首3行的俳句，作为对这个音视频的评价。这个评价要幽默、让人忍俊不禁。请直接输出俳句，其他内容不需要。'},
            {'role': 'user', 'content': text}
        ],
        temperature=1.2,
    )
    
    return completion.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description='从Bilibili视频下载音频并生成俳句')
    parser.add_argument('bvid', help='Bilibili视频的BV号')
    args = parser.parse_args()
    
    try:
        # 步骤1: 获取视频信息
        print(f"正在获取视频信息...")
        cid, title = get_video_info(args.bvid)
        print(f"视频标题: {title}")
        
        # 步骤2: 获取音频流URL
        print("正在获取音频流...")
        audio_url = get_audio_url(args.bvid, cid)
        print(f"已获取音频URL")
        
        # 步骤3: 首先尝试直接使用Bilibili音频URL进行识别
        print("正在尝试直接使用音频URL进行识别...")
        try:
            text = transcribe_audio(audio_url)
            print("识别完成，正在生成俳句...")
            haiku = generate_haiku(text)
            print("\n俳句结果:")
            print("="*50)
            print(haiku)
            print("="*50)
            return  # 如果成功，直接返回
        except Exception as e:
            print(f"直接使用音频URL识别失败，尝试备选方案: {str(e)}")
        
        # 备选方案: 下载 -> 上传 -> 识别
        # 步骤4: 下载音频文件
        print("正在下载音频文件...")
        local_file = download_audio(audio_url)
        print(f"音频已保存至: {local_file}")
        
        # 步骤5: 上传文件获取URL (尝试两种上传方式)
        print("正在上传音频文件获取URL...")
        try:
            upload_url = upload_to_catbox(local_file)
        except Exception as e:
            print(f"catbox上传失败，尝试使用tmpfiles: {str(e)}")
            upload_url = upload_to_tmpfiles(local_file)
        print(f"上传成功，URL: {upload_url}")
        
        # 步骤6: 进行语音识别
        print("正在进行语音识别...")
        text = transcribe_audio(upload_url)
        
        # 步骤7: 生成俳句并输出结果
        print("识别完成，正在生成俳句...")
        haiku = generate_haiku(text)
        print("\n俳句结果:")
        print("="*50)
        print(haiku)
        print("="*50)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    try:
        import dashscope
        from dashscope_api import api
        dashscope.api_key = api
        main()
    except Exception as e:
        print(f"发生错误: {str(e)}")
