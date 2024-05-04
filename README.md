# klinechart

#### 介绍
股票K线图表

#### 目标
1. 一组数据显示一个图形，如果增加了一组数据，直接增加对应的图形就好了

2. 不同的数据根据其类型显示成不同的形状，K线，线形，柱状图

3. 不同类型的图可以叠加，就像在不同图层上画图一样，可以一层一层叠罗汉

4. 数据结构松散化，没有就不画，数据通过外层类型控制，相同的数据表示类型是K线，则画K线，如果表示类型是柱状，则生成柱状，如果是线型，则生成曲线

#### 当前已实现功能
1. 完成了线形的基本功能，未来将线形与柱状图合并，成为指标逻辑
2. 不同的Chart可以叠加，不过要求时间需相同且价格边界需相同，比如均线与K线可叠加

#### 下一步目标
1. 增加数据即可增加图形（先简单化，增加数据然后通过main函数中增加几行代码，实现不同的图形组合。

#### 软件架构
1. BarManager：K线序列数据管理工具
2. ChartItem：基础图形类，继承实现后可以绘制K线、成交量、技术指标等
3. DatetimeAxis：针对K线时间戳设计的定制坐标轴
4. ChartCursor：十字光标控件，用于显示特定位置的数据细节
5. ChartWidget：包含以上所有部分，提供单一函数入口的绘图组件


#### 安装教程

1.  xxxx
2.  xxxx
3.  xxxx

#### 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
