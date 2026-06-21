## 自定义按钮

### 介绍

> 需要在2.1.2以上版本生效

django admin 默认提供了自定义按钮的支持，但是样式、图标均不可自定义，simpleui在django admin 自定义action的基础上增加了样式、图标、按钮类型自定义。

### 例子

python

```
@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender', 'idCard', 'phone', 'birthday', 'department', 'enable', 'create_time')
   
    # 增加自定义按钮
    actions = ['make_copy', 'custom_button']

    def custom_button(self, request, queryset):
        pass

    # 显示的文本，与django admin一致
    custom_button.short_description = '测试按钮'
    # icon，参考element-ui icon与https://fontawesome.com
    custom_button.icon = 'fas fa-audio-description'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    custom_button.type = 'danger'

    # 给按钮追加自定义的颜色
    custom_button.style = 'color:black;'

    def make_copy(self, request, queryset):
        pass
    make_copy.short_description = '复制员工'
```

该配置与原生admin兼容。

### 字段参数

| 字段 | 说明 |
| :------ | :----------------------------------------------------------- |
| icon | 按钮图标，参考https://element.eleme.cn/#/zh-CN/component/icon与https://fontawesome.com，把class 复制进来即可 |
| type | 按钮类型，参考：https://element.eleme.cn/#/zh-CN/component/button |
| style | 自定义css样式 |
| confirm | 弹出确认框，在3.4或以上版本中生效 |

### confirm 例子

python

```
def message_test(self, request, queryset):
        messages.add_message(request, messages.SUCCESS, '操作成功123123123123')
        
    # 给按钮增加确认
    message_test.confirm = '你是否执意要点击这个按钮？'
```

### 链接按钮

>

| 字段 | 说明 |
| :---------- | :--------------------------------------------------------- |
| action_type | 按钮动作类型，0=当前页内打开，1=新tab打开，2=浏览器tab打开 |
| action_url | 按钮访问链接 |

demo：

python

```
# 增加自定义按钮
    actions = ['custom_button']

    def custom_button(self, request, queryset):
        pass

    # 显示的文本，与django admin一致
    custom_button.short_description = '测试按钮'
    # icon，参考element-ui icon与https://fontawesome.com
    custom_button.icon = 'fas fa-audio-description'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    custom_button.type = 'danger'

    # 给按钮追加自定义的颜色
    custom_button.style = 'color:black;'

    # 链接按钮，设置之后直接访问该链接
    # 3中打开方式
    # action_type 0=当前页内打开，1=新tab打开，2=浏览器tab打开
    # 设置了action_type，不设置url，页面内将报错
    # 设置成链接类型的按钮后，custom_button方法将不会执行。

    custom_button.action_type = 0
    custom_button.action_url = 'http://www.baidu.com'
```

#### 字段说明

下列字段是指`action`的`layer`属性

| 字段 | 说明 |
| :------------- | :---------------------------- |
| title | 对话框标题 |
| tips | 对话框提示 |
| confirm_button | 确认按钮文本 |
| cancel_button | 取消按钮文本 |
| width | 对话框宽度，百分比，例如：50% |
| labelWidth | 表格的label宽度，例如：80px |
| params | 对话框表格中的字段，array |

##### params字段

| 字段 | 说明 |
| :------ | :----------------------------------------------------------- |
| type | 类型，取值为：input原生属性，和elementui的：select、date、datetime、rate、color、slider、switch、input_number、checkbox、radio |
| key | 参数名，post参数中获取的名称 |
| value | 默认值，数组或文本 |
| label | 字段在表格中显示的名称 |
| size | 组件的大小，取值为：medium / small / mini |
| require | 是否必选，取值为：True/False |
| width | 输入框宽度，例如：200px |
| options | 选项，数组，type为select、checkbox、radio的时候可用 |

#### options字段

| 字段 | 说明 |
| :---- | :------- |
| key | 值 |
| label | 显示文本 |

#### 例子

python

```
class RecordAdmin(ImportExportActionModelAdmin, AjaxAdmin):
    resource_class = ProxyResource

    list_display = ('id', 'name', 'type', 'money', 'create_date')
    list_per_page = 10

    actions = ('layer_input',)

    def layer_input(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据

        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    layer_input.short_description = '弹出对话框输入'
    layer_input.type = 'success'
    layer_input.icon = 'el-icon-s-promotion'

    # 指定一个输入参数，应该是一个数组

    # 指定为弹出层，这个参数最关键
    layer_input.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '弹出层输入框',
        # 提示信息
        'tips': '这个弹出对话框是需要在admin中进行定义，数据新增编辑等功能，需要自己来实现。',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'name',
            # 显示的文本
            'label': '名称',
            # 为空校验，默认为False
            'require': True
        }, {
            'type': 'select',
            'key': 'type',
            'label': '类型',
            'width': '200px',
            # size对应elementui的size，取值为：medium / small / mini
            'size': 'small',
            # value字段可以指定默认值
            'value': '0',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }]
        }, {
            'type': 'number',
            'key': 'money',
            'label': '金额',
            # 设置默认值
            'value': 1000
        }, {
            'type': 'date',
            'key': 'date',
            'label': '日期',
        }, {
            'type': 'datetime',
            'key': 'datetime',
            'label': '时间',
        }, {
            'type': 'rate',
            'key': 'star',
            'label': '评价等级'
        }, {
            'type': 'color',
            'key': 'color',
            'label': '颜色'
        }, {
            'type': 'slider',
            'key': 'slider',
            'label': '滑块'
        }, {
            'type': 'switch',
            'key': 'switch',
            'label': 'switch开关'
        }, {
            'type': 'input_number',
            'key': 'input_number',
            'label': 'input number'
        }, {
            'type': 'checkbox',
            'key': 'checkbox',
            # 必须指定默认值
            'value': [],
            'label': '复选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }, {
            'type': 'radio',
            'key': 'radio',
            'label': '单选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }]
    }
```

#### action 返回结果

json

```
{
    'status': 'error',
    'msg': '请先选中数据！'
}
```

> status = success/error

> msg = 自定义

#### 对话框按钮说明

1. 如果需要作为增加和编辑 需要自己实现业务逻辑，编辑的时候将数据填充到value字段即可。
1. 限制选中后才能提交数据，可以在后台进行限制
1. 2020.1.0 及以上版本生效，需要继承`AjaxAdmin` 在`from simpleui.admin import AjaxAdmin`包中。 不继承提交数据会500或者404 例如：

python

```
if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
```

### layer 文件上传

> 自2021.4.2+版本开始，支持layer中上传文件

例子：

python

```
@admin.register(Layer)
class LayerAdmin(AjaxAdmin):
    actions = ('upload_file',)

    def upload_file(self, request, queryset):
        # 这里的upload 就是和params中配置的key一样
        upload= request.FILES['upload']
        print(upload)
        pass

    upload_file.short_description = '文件上传对话框'
    upload_file.type = 'success'
    upload_file.icon = 'el-icon-upload'
    upload_file.enable = True

    upload_file.layer = {
        'params': [{
            'type': 'file',
            'key': 'upload',
            'label': '文件'
        }]
    }
```
