众所周知，import分为绝对导入和相对导入，两者的唯一区别就是是否使用了"." 
为一探究竟，构建以下项目目录：

```bash
imp_test
├── entrance1.py
├── pakg1
│   ├── __init__.py
│   ├── module1.py
│   ├── module2.py
│   └── pakg1_1
│       └── __init__.py
└── pakg2
    └── __init__.py
```

## 一、绝对导入
先明确下，python中modules的概念并不统一，官方文档中的modules有时候指的是package，有时候指的是py文件，为了避免歧义，本文中module特指py文件，modules指“py文件以及包”。
形式如`import XXX`或`from  XXX import a,b ` 都是绝对导入。比如在`module1.py`中导入`module2.py`中的内容：`from module2 import v2`。
当执行绝对导入时，解释器做了以下这些事情：

 1. 查找built-in modules（内置模块）。内置模块是python解释器的一部分，用C语言编写，常见的有`os time sys json`；
 2. 查找sys.path包含的目录，包括：
 - **启动文件**所在的目录
 - 当前项目的顶级目录
 -  当前解释器lib目录，主要是第三方包的安装目录

因此可以得出结论：绝对导入时，**启动文件**所在的目录下以及项目顶级目录下的包或py文件可以直接导入（此时IDE可以自动补全）。值得注意的是，当项目中涉及多个层级目录下的py文件或模块的互相导入，所有py文件的`sys.path`都是一样的，绝对导入的搜索目录针对的都是**启动文件**。
可以测试，当启动文件为`pakg1.module1.py`，在`pakg1.module1.py`中执行绝对导入，都没问题：

```python
#pakg1.module1.py

import pakg1_1 # 当前目录下的包
import pakg2 # 顶层目录下的包
import module2 # py文件
```
但是当启动文件为`entrance1.py`时，在`entrance1.py`执行绝对导入：

```python
#entrance1.py

import pakg1.module1
```
就会提示在`pakg1.module1.py`中`import module2`报错：

```bash
ModuleNotFoundError: No module named 'module2'
```
原因如上所述，启动文件为`entrance1.py`时，`module2`并未在其搜索目录中。
## 二、相对导入
带"."的导入是相对导入，如：`from  .XXX import a,b`，要理解相对导入，关键在于搞明白"."是什么含义。
在`pakg1.module1.py`执行相对导入：

```python
#module1.py

print('pakg1.module1 __name__ is:',__name__)

from .module2 import v2

print(v2)
```
并启动`pakg1.module1.py`，得到报错：

```bash
ImportError: attempted relative import with no known parent package
pakg1.module1 __name__ is: __main__
```
要理解"."的含义，关键在于理解python的`__name__`属性：事实上python所有对象都有该属性，包括包和py文件。对于py文件，这个属性不是一成不变的：

- 当其是启动文件时，该文件的`__name__ = "__main__"`；
- 当其不是启动文件时，`__name__ = pakg_name.module_name`，其中`pakg_name`从顶层目录的包开始算起，有多层则以此类推；


而相对导入中的"."则指的是，该文件的`__name__`属性去掉最后的文件名前面的部分，即该文件的“父包”，当该文件是启动文件时，由于`__name__ = "__main__"`，此时“父包”为空，故会报错`no known parent package`。
事实上，python的modules还有一个属性`__package__`，官方文档解释如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/2f8adc0443ee4548947f1a016af174c3.png)
从以上文字我们可以了解到：对于包来讲，`__package__ == __name__`，而对于py文件来讲，`__package__`则代表其父包，并且对于在项目顶层目录的py文件（对于启动文件，不管实际目录怎样，都认为它是顶层文件），该属性为空。因此我们可以认为某文件中相对导入的"."，指的就是该文件的`__package__`属性。
## 三、结论
弄明白原理后，在实际项目中涉及到import，可以总结以下几条原则：

- 如果项目层级不是特别深，而结构预计不会做很大调整，最保险的导入方式是：统统使用绝对导入，并且从项目顶层包开始引入；
- 反之，当项目层级很深，而结构可能面临调整时，可以使用相对导入，但需要保证该文件不是启动文件；
- 项目顶层文件中不要使用相对导入，因为顶层文件再上层是项目目录，没有父包了，即`__package__ = ''`。

## 四、关于__init__
为什么每个包要有一个`__init__`？首先是因为它可以标志这是一个包，可以被import；其次，在实际项目中，我们需要对外暴露的内容更多的是函数、类或变量，如果要导入这些对象，就需要`from pakg_name.module_name import a,b,c`，可能略显冗长，而如果提前在包的_`_init__`中将要暴露的对象导入，这些对象将属于“包的子集”，导入时只需要精确到包就行了，即`from pakg_name import a,b,c`，除此之外，使用`__all__`还可以约束该包要暴露的内容，有“白名单”效果。因此在`__init__`明确每个包要暴露的对象是很好的习惯。

个人理解，不免有错，如果疑问，欢迎交流。