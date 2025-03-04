# code2uml

将代码转为UML图

输入目录或者文件，输出UML图

根据antlr4完成目前的代码，实现功能：

1. 支持目录或者单个文件的输入，或者代码段(代码段时必须指定语言类型)
2. 根据文件名自动识别为C++或者java语言，或者可以通过参数指定语言类型
3. 根据文件内容自动识别为类、函数、变量、常量、方法等，将其转换成中间语言
4. 根据中间语言生成plantuml或者mermaid的UML类图
5. 对于代码段，必须在调用时指定语言类型

## 编译

```sh
pip install .
```

或者使用pypi 在官网进行下载

```sh
pip install code2uml
```

## 使用方法

```sh
code2uml --input path
```

## Features

v0.2.5

1. add relation between class
2. remove print debug log
3. add log when processing file

v0.2.0

1. add packages in java
2. add dot ouput


## 辅助工具安装

### plantuml的使用

plantuml是使用了java代码编写，所以需要安装jdk等工具，请自行安装

下载plantuml-mit-1.2025.0.jar 包

[https://plantuml.com/zh/download#google_vignette](https://plantuml.com/zh/download#google_vignette)

### graphviz的安装

**ubuntu**系统

```sh
sudo apt-get install graphviz
```

**centos**系统

```sh
sudo yun install graphviz
```

## problems

### 问题1 plantuml无法生成完整的图片

plantuml can't generate complete image

use command: 
`java -jar ~/下载/plantuml-mit-1.2025.0.jar code2uml_java.puml -v`

```sh
java -jar ~/下载/plantuml-mit-1.2025.0.jar code2uml_java.puml -v
(0.060 - 508 Mo) 499 Mo - SecurityProfile LEGACY
(0.066 - 508 Mo) 499 Mo - PlantUML Version 1.2025.0
(0.066 - 508 Mo) 499 Mo - GraphicsEnvironment.isHeadless() false
(0.066 - 508 Mo) 499 Mo - Forcing resource load on OpenJdk
(0.109 - 508 Mo) 497 Mo - Found 1 files
(0.110 - 508 Mo) 497 Mo - Working on code2uml_java.puml
(0.125 - 508 Mo) 496 Mo - Using default charset
(0.130 - 508 Mo) 496 Mo - Reading from code2uml_java.puml
(0.165 - 508 Mo) 480 Mo - ...text loaded...
(0.237 - 508 Mo) 497 Mo - Setting current dir: frameworks/base/services/core/java/com/android/server/am/.
(0.237 - 508 Mo) 497 Mo - Setting current dir: frameworks/base/services/core/java/com/android/server/am
(0.237 - 508 Mo) 497 Mo - Reading file: code2uml_java.puml
(0.257 - 508 Mo) 496 Mo - ..compiling diagram...
(0.389 - 508 Mo) 464 Mo - Trying to load style plantuml.skin
(0.389 - 508 Mo) 464 Mo - Current dir is frameworks/base/services/core/java/com/android/server/am so trying frameworks/base/services/core/java/com/android/server/am/plantuml.skin
(0.389 - 508 Mo) 464 Mo - File not found : 
(0.391 - 508 Mo) 464 Mo - ... but plantuml.skin found inside the .jar
(0.416 - 508 Mo) 454 Mo - ...parsing ok...
(0.416 - 508 Mo) 454 Mo - Compilation duration 159
(0.417 - 508 Mo) 454 Mo - Creating file: frameworks/base/services/core/java/com/android/server/am/code2uml_java.png
(0.424 - 508 Mo) 454 Mo - Using style root.element.classdiagram.package.title false
(0.519 - 508 Mo) 420 Mo - Using style root.element.statediagram.state.header false
(0.534 - 508 Mo) 416 Mo - Using style root.element.classdiagram.class false
(0.536 - 508 Mo) 416 Mo - Using style root.element.classdiagram.class.header false
(0.538 - 508 Mo) 416 Mo - Using style root.element.spot.spotclass false
(0.715 - 508 Mo) 284 Mo - Using style root.element.classdiagram.arrow false
(0.715 - 508 Mo) 284 Mo - Using style root.element.classdiagram.arrow.cardinality false
(0.754 - 508 Mo) 258 Mo - Using style root.element.classdiagram.group.package false
(0.954 - 508 Mo) 349 Mo - Starting Graphviz process [/usr/bin/dot, -Tsvg]
(0.954 - 508 Mo) 349 Mo - DotString size: 45002
(0.985 - 508 Mo) 347 Mo - Ending process ok
(0.985 - 508 Mo) 347 Mo - Ending Graphviz process
(1.554 - 612 Mo) 419 Mo - Using style root.document.classdiagram false
(1.554 - 612 Mo) 419 Mo - Using style root.document false
(2.004 - 612 Mo) 311 Mo - ...image drawing...
(2.004 - 612 Mo) 309 Mo - Width too large 21790. You should set PLANTUML_LIMIT_SIZE
(2.004 - 612 Mo) 309 Mo - Height too large 22766. You should set PLANTUML_LIMIT_SIZE
(2.005 - 612 Mo) 309 Mo - Creating image 4096x4096
(3.035 - 736 Mo) 253 Mo - Number of image(s): 1
```

important note:

```sh
(2.004 - 612 Mo) 311 Mo - ...image drawing...
(2.004 - 612 Mo) 309 Mo - Width too large 21790. You should set PLANTUML_LIMIT_SIZE
(2.004 - 612 Mo) 309 Mo - Height too large 22766. You should set PLANTUML_LIMIT_SIZE
(2.005 - 612 Mo) 309 Mo - Creating image 4096x4096
```

使用命令进行替换
`java -jar ~/下载/plantuml-mit-1.2025.0.jar code2uml_java.puml -v -DPLANTUML_LIMIT_SIZE=22766`

或者使用svg格式

![alt text](code2uml_java.svg)

### 问题2 dot无法生成图片

使用命令:

```sh
dot code2uml_java.dot -v
```

问题点:

```sh
dot - graphviz version 2.43.0 (0)
libdir = "/usr/lib/x86_64-linux-gnu/graphviz"
Activated plugin library: libgvplugin_dot_layout.so.6
Using layout: dot:dot_layout
Activated plugin library: libgvplugin_core.so.6
Using render: dot:core
Using device: dot:dot:core
The plugin configuration file:
        /usr/lib/x86_64-linux-gnu/graphviz/config6a
                was successfully loaded.
    render      :  cairo dot dot_json fig gd json json0 map mp pic pov ps svg tk visio vml vrml xdot xdot_json
    layout      :  circo dot fdp neato nop nop1 nop2 osage patchwork sfdp twopi
    textlayout  :  textlayout
    device      :  canon cmap cmapx cmapx_np dot dot_json eps fig gd gd2 gif gv imap imap_np ismap jpe jpeg jpg json json0 mp pdf pic plain plain-ext png pov ps ps2 svg svgz tk vdx vml vmlz vrml wbmp webp x11 xdot xdot1.2 xdot1.4 xdot_json xlib
    loadimage   :  (lib) eps gd gd2 gif jpe jpeg jpg png ps svg webp xbm
Error: code2uml_java.dot: syntax error in line 1281 scanning a quoted string (missing endquote? longer than 16384?)
String starting:"{ ActivityManagerService|+ mInstaller : Installer|+ mTaskSupervisor : ActivityTa
```

dot语言中，label的标签最大长度为16K, 超过16K就会报错，目前官方的版本暂时没有解决这个问题，需要自己修改源码。

### 问题3 cpp中类图存在问题

cpp目前在antlr4中暂时没有办法解决该问题，属于工具引入的bug，目前无法解决。

### 问题4 多个类中存在同名类

目前因为在plantuml中无法很好的表达内部类的关系，这个属于需求较小的问题，暂时不予解决.

实际案例：在类中存在多个builder，所有的builder的方法和字段都被放在一个类中

