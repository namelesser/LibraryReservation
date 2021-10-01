# 齐齐哈尔大学图书馆预约
## 一 项目介绍

|    房间    |   房间编号  | 座位编号    |
| ----| ---- |----|
|东区图书馆自习室201室  | 1201 |001 - 104|
|东区图书馆自习室202室  | 1202 | 001 - 10  | 
| 东区图书馆自习室293室 | 1293 | 001 - 180 | 
| 东区图书馆自习室294室 | 1294 | 001 - 160 | 
| 东区图书馆自习室401室 | 1401 | 001 - 164 | 
| 东区图书馆自习室702室 | 1702 | 001 - 10  | 
| 中区图书馆自习室101室 | 2101 | 001 - 80  | 
| 中区图书馆自习室201室 | 2201 | 001 - 144 | 
| 中区图书馆自习室206室 | 2206 | 001 - 80  | 
| 中区图书馆自习室211室 | 2211 | 001 - 76  | 
| 西区图书馆自习室401室 | 3401 | 001 - 152 | 
|西区图书馆自习室408室  | 3408 | 001 - 199 | 

*斜体*  
_斜体_   
**出题**  
__粗体__  
~~删除线~~  
<u>下划线<u>  
[^AA].
[^AA]:啊实打实的 创建脚注格式类似这样 [^RUNOOB]。

[^RUNOOB]: 菜鸟教程 -- 学的不仅是技术，更是梦想！！！

+ 1
    * 1
    * 2
    * 3
        * 1
        * 2
        * 3
+ 2
+ 3
+ 4
+ 5

* 1
* 2
* 3
* 4
* 5

- a
- a
- a
- a
- asd
- asd

1. 1
2. 2
3. 3
4. 4
5. 5

> 最外层
>> 第一层
>>> * 阿斯顿
>>> * 深爱的

* 第一项
  > 菜鸟教程
  > 学的不仅是技术更是梦想
* 第二项

  <pritnf("123);

````java
pubulic static void main(String str[]){
    System.out.println("hello word~")
}
````

[百度一下你就知道](http:\\www.baidu.cin)

[百度一下你就知道][1]  
[1]: http:www.baidu.com  
![alt 图标](http://static.runoob.com/images/runoob-logo.png)

![RUNOOB 图标](http://static.runoob.com/images/runoob-logo.png "RUNOOB")

|  表头   | 表头  | 表头 |
|  :----  | ----:  | :----:|
| 单元格  | 单元格123123123 | dddddd
| ddd单元格  | 单元格 | asddwasd |

使用 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Del</kbd> 重启电脑

```mermaid
%% 语法示例
        gantt
        dateFormat  YYYY-MM-DD
        title 软件开发甘特图
        section 设计
        需求                      :done,    des1, 2014-01-06,2014-01-08
        原型                      :active,  des2, 2014-01-09, 3d
        UI设计                     :         des3, after des2, 5d
    未来任务                     :         des4, after des3, 5d
        section 开发
        学习准备理解需求                      :crit, done, 2014-01-06,24h
        设计框架                             :crit, done, after des2, 2d
        开发                                 :crit, active, 3d
        未来任务                              :crit, 5d
        耍                                   :2d
        section 测试
        功能测试                              :active, a1, after des3, 3d
        压力测试                               :after a1  , 20h
        测试报告                               : 48h
```