## 模板

### 修改模板

在simpleui的基础上修改模板需要对django有一定了解

1. 先把simpleui克隆到静态目录下，参考[克隆静态文件到根目录](https://newpanjing.github.io/simpleui_docs/config.html#%E5%85%8B%E9%9A%86%E9%9D%99%E6%80%81%E6%96%87%E4%BB%B6%E5%88%B0%E6%A0%B9%E7%9B%AE%E5%BD%95)
1. 找到静态目录下的admin目录，里面就是simpleui的模板，直接修改相关html页面即可生效。

### 重写页面

例如重写首页，在templates目录中新建admin文件夹，然后添加index.html 如果选择继承方式，就只能采用block 代码如下：

html

```
{% extends 'admin/index.html' %}
    {% load static %}

    {% block head %}
        {{ block.super }}
        ..此处写你的代码
    {% endblock %}

    {% block script %}
        {{ block.super }}
        ..此处写你的代码
    {% endblock %}
```

如果是想全部重写：

html

```
<html>
    <head>
        <title>完全自定义</title>
    </head>
    <body>
        这里你是自定义的html代码
    </body>
</html>
```

#### 头部添加自定义代码

html

```
{% extends 'admin/index.html' %}
    {% load static %}

    {% block head %}
        {{ block.super }}
        ..此处写你的代码
    {% endblock %}
```

#### 底部添加自定义代码

html

```
{% extends 'admin/index.html' %}
    {% load static %}

    {% block script %}
        {{ block.super }}
        ..此处写你的代码
    {% endblock %}
```
