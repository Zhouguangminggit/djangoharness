## 菜单

### system_keep 保留系统菜单

该字段用于告诉simpleui，是否需要保留系统默认的菜单，默认为False，不保留。 如果改为True，自定义和系统菜单将会并存

### menu_display 过滤显示菜单和排序功能

该字段用于告诉simpleui，是否需要开启过滤显示菜单和排序功能。
默认可以不用填写，缺省配置为默认排序，不对菜单进行过滤和排序。
开启认为传一个列表，如果列表为空，则什么也不显示。列表中的每个元素要对应到menus里面的name字段

### dynamic 开启动态菜单功能

该字段用于告诉simpleui，是否需要开启动态菜单功能。
默认可以不用填写，缺省配置为False，不开启动态菜单功能。
开启为True，开启后，每次用户登陆都会刷新左侧菜单配置。
需要注意的是：开启后每次访问admin都会重读配置文件，所以会带来额外的消耗。

### menus说明

| 字段 | 说明 |
| :----- | :----------------------------------------------------------- |
| name | 菜单名 |
| icon | 图标，参考element-ui和fontawesome图标 |
| url | 链接地址，绝对或者相对,如果存在models字段，将忽略url |
| models | 子菜单，自2021.02.01+版本 支持最多3级菜单，使用方法可以看下方例子 |
| newTab | boolean,default:False,浏览器新标签中打开，自2022.6.13开始支持 |

### 例子

python

```
import time
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['Simpleui', '测试', '权限认证', '动态菜单测试'],      # 开启排序和过滤功能, 不填此字段为默认排序和全部显示, 空列表[] 为全部不显示.
    'dynamic': True,    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [{
        'name': 'Simpleui',
        'icon': 'fas fa-code',
        'url': 'https://gitee.com/tompeppa/simpleui',
        # 浏览器新标签中打开
        'newTab': True,
    }, {
        'app': 'auth',
        'name': '权限认证',
        'icon': 'fas fa-user-shield',
        'models': [{
            'name': '用户',
            'icon': 'fa fa-user',
            'url': 'auth/user/'
        }]
    }, {
        # 自2021.02.01+ 支持多级菜单，models 为子菜单名
        'name': '多级菜单测试',
        'icon': 'fa fa-file',
      	# 二级菜单
        'models': [{
            'name': 'Baidu',
            'icon': 'far fa-surprise',
            # 第三级菜单 ，
            'models': [
                {
                  'name': '爱奇艺',
                  'url': 'https://www.iqiyi.com/dianshiju/'
                  # 第四级就不支持了，element只支持了3级
                }, {
                    'name': '百度问答',
                    'icon': 'far fa-surprise',
                    'url': 'https://zhidao.baidu.com/'
                }
            ]
        }, {
            'name': '内网穿透',
            'url': 'https://www.wezoz.com',
            'icon': 'fab fa-github'
        }]
    }, {
        'name': '动态菜单测试' ,
        'icon': 'fa fa-desktop',
        'models': [{
            'name': time.time(),
            'url': 'http://baidu.com',
            'icon': 'far fa-surprise'
        }]
    }]
}
```

如果SIMPLEUI_CONFIG中存在menus字段，将会覆盖系统默认菜单。并且menus中输出的菜单不会受权限控制。
