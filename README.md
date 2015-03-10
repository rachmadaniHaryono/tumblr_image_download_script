### 从 tumblr 上下载图片回来
根据各个博主的二级域名建立对应的文件夹，存放相应的图片资源

#### 依赖库
- requests

#### 功能支持
- 多线程下载

#### 使用说明

首先获取博主二级域名, e.g http://er0.tumblr.com --> er0

```python
dl = tumblr.Tumblr('er0')
dl.run()
```

#### update 
- 添加了 http proxy 支持，按照 requests 的使用方法，提供如下形式的 http 代理
```python
proxies = {'schema':'schema://host:port'}
dl = tumblr.Tumblr('er0', proxies=proxies)
dl.run()
```

- 如果不需要下载图片，而只想要提取图片链接，可以传入参数 ```need_save=False```
图片链接保存在 logs/imgurl.log 中，使用 ```awk '{print $5}' imgurl.log > img.url``` 即可提取出来 img url

更多的博主链接可以参考 general_run.py 中列出来的
