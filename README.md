# SetuScore
一个为色图打分的插件

## 盐的fork version

1. 将色图打分改为了常开的模式，每次发送图片都会自动打分, 疑似高于350才会向群内发送提示
2. 对表情包进行了区分
3. 删除了数量限制
4. 将api的配置移动到了config文件夹下
5. 添加了数据库, 避免图片重复打分
6. 添加了可设置的禁言阈值, 高于阈值的图片将会被禁言

## 功能 

```text
[打分/评分] 图片 涩图打分
开启后将在群组内自动识别, 评分高于350才会提示分值
[禁言阈值 分数] 发高于阈值的图片将会被禁言
[取消禁言阈值] 取消当前群组的禁言阈值
```
## 新增的步骤

将目录下的[config_sample-setu_score.py](config_sample-setu_score.py)重命名为`setu_score.py`并填入对应的信息, 将其移动至`config`文件夹下,
路径应为`hoshino/config/setu_score.py`

## 注意

插件为默认关闭, 因为它会将群内所有图片都进行分值查询, 如果是图片较多的群注意API的消耗

为了减少调用次数, 插件对图片的名字和分值进行了存储, 并忽略了表情包

## 原仓库的使用说明

在 https://cloud.baidu.com/product/imagecensoring 页面开通服务

开通后进入管理台创建应用
![img](./img/img1.png)

名称和描述随便填一下就行
![img](./img/img2.png)

记住你的Api Key, Secret Key,填入`setu_score.py`里对应的位置
![img](./img/img3.png)

开通图片审核服务,有免费一万次记得领一下,用完的话就往账号里存十块钱,够用很久了
![img](./img/img7.png)

进入 https://ai.baidu.com/censoring#/strategylist 页面创建策略
![img](./img/img4.png)

这里应用选你刚才创建那个
![img](./img/img5.png)

色情疑似区间拉满(这一步很重要！),然后在页面最下面保存策略
![img](./img/img6.png)
![img](./img/img10.png)

把文件夹放入`modules`中并在`__bot__.py`中添加该插件

效果图:
![img](./img/img9.jpg)


## 致谢
连续对话代码参考了 https://github.com/pcrbot/picfinder_take

数据库处理部分参考了 https://github.com/azmiao/XQA