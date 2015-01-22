### 从 tumblr 上下载图片回来
根据各个博主的二级域名建立对应的文件夹，存放相应的图片资源

#### 依赖库
- requests

#### 功能支持
- 多线程下载

#### 使用说明
e.g http://er0.tumblr.com

dl = tumblr.Tumblr('er0')
dl.run()

更多的博主链接可以参考 general_run.py 中列出来的
