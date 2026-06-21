SIMPLEUI_CONFIG = {
    "system_keep": False,
    "menu_display": ["用户管理"],
    "dynamic": False,
    "menus": [
        {
            "app": "accounts",
            "name": "用户管理",
            "icon": "fas fa-users-cog",
            "models": [
                {
                    "name": "用户列表",
                    "icon": "fas fa-user-friends",
                    "url": "accounts/user/",
                },
                {
                    "name": "新增用户",
                    "icon": "fas fa-user-plus",
                    "url": "accounts/user/add/",
                },
                {
                    "name": "批量新增",
                    "icon": "fas fa-file-import",
                    "url": "accounts/user/bulk-add/",
                },
            ],
        }
    ],
}

SIMPLEUI_LOGIN_PARTICLES = False


# 首页标题
SIMPLEUI_HOME_TITLE = "首页"

SIMPLEUI_HOME_INFO = False

# 首页快捷入口由数据看板替代
SIMPLEUI_HOME_QUICK = False

# 最近动作
SIMPLEUI_HOME_ACTION = False

# 分析
SIMPLEUI_ANALYSIS = False

# 遮罩层
SIMPLEUI_LOADING = True

# 后台品牌信息
SIMPLEUI_LOGO = "/static/accounts/brand/logo.png"
SIMPLEUI_LOGIN_LOGO = SIMPLEUI_LOGO
SIMPLEUI_INDEX = "/"
