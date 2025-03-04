## haikubot：B站引流狗最爱的俳句生成器

### 简介

haikubot 是一个基于 Bilibili 视频生成俳句的命令行工具。

在这里，我参考了 [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 仓库用于获取B站视频信息，你可以在 [musicstream_url.md](references/musicstream_url.md) 和 [videostream_url.md](references/videostream_url.md) 来参考如何获取音视频流地址。

接着，我使用了dashscope api，调用alibaba的paraformer模型进行语音识别，识别出类字幕文本。

最后，我使用了openai的api，可以用兼容模型（比如qwen/deepseek）来生成俳句。

### 安装

```bash
pip install haikubot
```

## 使用方法

```bash
# 第一次使用，你应该配置dashscope的API密钥，你可以搜索百炼平台，进去获取api key，随后替换这里的YOUR_API_KEY，然后运行
haikubot config YOUR_API_KEY

# 之后，你可以这样使用BVID处理视频生成俳句
haikubot process BV117XoYGErB

# 显示版本信息
haikubot version
```
