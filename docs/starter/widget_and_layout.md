# 组件和布局

## 组件

### 组件体系

django-echarts可以在同一个页面上显示多个图表和其他数据组件，并支持定制不同的布局方式。该功能涉及到的类如下表：

| 分组 | 组件                                      | 描述                        | 注册函数            | 数据容器          |
| ---- | ----------------------------------------- | --------------------------- | ------------------- | ----------------- |
| 容器 |                                           |                             |                     |                   |
|      | 合辑 ChartCollection                      | 可包含各种组件              | register_collection | collections       |
| 组件 |                                           |                             |                     |                   |
|      | 文章组件 ChartInfo                        | 图表信息数据实体类          | register_chart      | chart_info_manger |
|      | 单图表组件<sup>1</sup> pyecharts.charts.* | 可关联一个ChartInfo         | register_chart      | charts            |
|      | 多图表组件 NamedCharts                    | 多个图表关联同一个ChartInfo | register_chart      | charts            |
|      | HTML组件 ValuesPanel、Copyright           | 无法关联ChartInfo           | register_widget     | widgets           |
| 布局 | 布局配置 LayoutOpts                       | 布局配置实体                |                     |                   |

1. 目前 django-echarts不支持 Tab / BMap / Page 类型图表，Page 可以使用 `NamedCharts` 代替。

### 注册和使用组件

无论是collection还是具体的组件均使用 `register_*` 方法注册。

**方式一**：使用装饰器方式，此种情况下仅保存组件的创建器函数，并不会立即生成相应的对象。

```python
@site_obj.register_chart(name='mybar', title='bar示例')
def named_charts():
    bar = Bar()
    # ...
    return bar
```

**方式二**：向 `register_*` 传入一个具体的组件对象，此种情况下组件的数据总是固定不变的。

```python
bar = Bar()
# ...
site_obj.register_chart(bar, name='mybar', title='bar示例')
```

## 组件列表

### 数字仪盘(ValuesPanel)

```python
ValueItem(value: Any, description: str, unit: str = None, catalog: str = 'primary', trend: Literal['up', 'down', ''] = '')

ValuesPanel(data: List[ValueItem] = None, col_item_num: int = 1)
```

以突出方式显示数字数值。

| 参数            | 类型                      | 描述             |
| --------------- | ------------------------- | ---------------- |
| **ValueItem**   |                           |                  |
| value           | Any                       | 数值型数据       |
| description     | str                       | 描述性文字       |
| unit            | str                       | 单位文字         |
| catalog         | primary                   | 决定背景颜色     |
| arrow           | Literal['up', 'down', ''] | 数字后的箭头符号 |
| **ValuesPanel** |                           |                  |
| data            | List[ValueItem]           | 数字项列表       |
| col_item_num    | int                       | 每行多少个       |

例子：

```python
@site_obj.register_widget
def home1_panel():
    number_p = ValuesPanel(col_item_num=4)
    # 显示图表总个数
    number_p.add(ValueItem(str(site_obj.chart_info_manager.count()), '图表总数', '个', catalog='danger'))
    number_p.add(ValueItem('42142', '网站访问量', '人次'))
    return number_p
```

### 多图表(NamedCharts)

NamedCharts 和 Page 类似，能够同时显示多个图表，兼容内置的响应式布局。

```python
@site_obj.register_chart(name='named_charts', title='NamedCharts示例', description='使用NamedCharts')
def named_charts():
    page = NamedCharts(page_title='复合图表', col_num=2)
    pie = Pie()
    page.add_chart(pie, 'pie')
    
    bar = Bar()
    page.add_chart(bar, 'bar')
    return page
```

说明：

- col_num 表示每行的图表个数，推荐设置1-3即可。在小屏幕上将自动调整为每行一个。
- add_chart 函数将宽度设置为 100%。

## 图表合辑

### 图表布局

布局分为网格布局和行内布局两种。布局方式使用一个字母和一个数字组成的字符串。第1个字母表示图表的所在位置，第2个字母表示图表所占用的列数（总列数为12）。可使用的位置标识（使用首字母即可）如下：

| 标识 | left | right | top  | bottom | full           | stripped     | auto           |
| ---- | ---- | ----- | ---- | ------ | -------------- | ------------ | -------------- |
| 描述 | 左侧 | 右侧  | 顶部 | 底部   | 不显示信息Info | 左右交叉图表 | 按行内布局显示 |

使用规则：

- 其中 a和s仅合辑网格布局可使用。
- lrtbf布局网格布局和行内布局均可使用。
- l8表示 “图表8列 + 信息卡4列”； r8 表示“信息卡4列+图表8列”
- 响应式布局：所设置的列数仅在md以上有效，sm及其以下均会扩展到整行12列

下面是常见使用场景的布局定义：

| ChartCollection.layout | 描述                                                    |
| ---------------------- | ------------------------------------------------------- |
| l8                     | 每行显示1个图表，图表全部靠左显示                       |
| r8                     | 每行显示1个图表，图表全部靠右显示                       |
| s8                     | 每行显示1个图表，左右信息卡交叉显示                     |
| f6                     | 每行显示2个图表，不显示信息卡                           |
| f12                    | 每行显示1个图表，不显示信息卡                           |
| t6                     | 每行显示2个图表，信息卡显示在顶部。(信息卡包含少量文字) |
| b6                     | 每行显示2个图表，信息卡显示在低部。(信息卡包含大量文字) |

### 注册合辑

`ChartCollection`类表示一个图表合辑对象，可以通过 `add_collection` 方法构建一个图表合辑页面。

```python
site_obj = DJESite(site_title='DJE Demo')

@site_obj.register_chart(name='fj_fimily_type', title='示例图表1', layout='l8')
def fj_fimily_type():
    line = Line()
    # ...
    return line

@site_obj.register_chart(name='fj_area_bar', title='示例图表2', layout='l8')
def fj_fimily_type():
    bar = Bar()
    # ...
    return bar

site_obj.add_collection(
    name='collection1',
    charts=['fj_fimily_types', 'fj_area_bar'], layout='s8'
)
```

访问URL */collection/collection1/* 可以预览页面效果。

add_collection 函数参数及其意义：

| 参数            | 类型      | 说明                                   |
| --------------- | --------- | -------------------------------------- |
| name            | slug      | 合辑标识                               |
| charts          | List[str] | 包含的图表标识                         |
| layout          | str       | 合辑布局                               |
| title           | str       | 标题                                   |
| catalog         | str       | 如果设置，将添加合辑链接到该菜单项之下 |
| after_separator | bool      | 是否在菜单项前使用分隔符               |
