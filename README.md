# 介绍

一些会在NSCSCC2023中使用的通用工具仓库。

## 获取仓库

```shell
git clone git@github.com:BJTU-NSCSCC-2023/pi_tool.git
```



## 初始化

### 设置指向本仓库根的环境变量

需要保证：`NSCSCC2023_BJTU_PI_TOOL_HOME`已经被设置为本仓库根的路径，具体来说，在Shell执行下述指令输出`YES`而不是`NO`：

```shell
[ "$(cat ${NSCSCC2023_BJTU_PI_TOOL_HOME}/spear.txt)" = "nscscc2023_bjtu_pi_tool" ] && echo "YES" || echo "NO"
```



### 设置环境

本仓库会检查以下程序：

* `conda`
* `sbt`
* `conan`

在确定上述程序都存在后，执行：

```shell
conda env update -n nscscc2023-bjtu-pyenv -f "${NSCSCC2023_BJTU_PI_TOOL_HOME}/nscscc2023-bjtu-pyenv.yaml" 
```

来新建`conda`的python环境。

在之后的开发过程中，可以执行`upd_env.sh`来更新`conda`的python环境。



## 引入本仓库的方法

所有使用本仓库的代码都建议插入检查代码，用来保证已经正确引入本仓库，以避免奇怪的错误。下面是各个语言做这个检查的实现：

* shell

  ```shell
  test "$(cat ${NSCSCC2023_BJTU_PI_TOOL_HOME}/spear.txt)" = "nscscc2023_bjtu_pi_tool" || echo -e "\033[31mCannot find spear. Check if NSCSCC2023_BJTU_PI_TOOL_HOME set properly.\033[m" || exit 1
  ```



---

下面以仓库结构为脉络介绍本仓库。

# sh_lib

一个用于Shell脚本的库，包含：

* `decorator.sh`：定义了一系列与输出染色相关变量。

* `check_before_run.sh`：建议在检查完`NSCSCC2023_BJTU_PI_TOOL_HOME`之后就`source "${NSCSCC2023_BJTU_PI_TOOL_HOME}/sh_lib/check_before_run.sh"`，这样可以：

  * `source`上面提到的所有Shell脚本库。

  * 设置环境变量`piRoot`为`${NSCSCC2023_BJTU_PI_TOOL_HOME}`，避免每次写那么长的环境变量名。**强烈建议不要在你的脚本中更改`piRoot`的信息，比如`unset`或者重新`export`**！

  * 完成运行环境的检查，包括：

    * 检查`conda`是否安装。
    * 检查`conda`环境`nscscc2023-bjtu-pyenv`是否存在（**但是出于效率考虑不会检查是否为最新的环境。请手动执行`upd_env.sh`以更新环境**）。
    * 检查几个工具是否存在：``

    如果任何一个检查不通过，就会输出错误信息并终止运行，退出码为1。

  * 设置环境变量`py`为`conda run -n nscscc2023-bjtu-pyenv python3`，这样可以保证所有的python代码运行于我们定义的环境下。

  此外，`check_before_run.sh`也会检查`NSCSCC2023_BJTU_PI_TOOL_HOME`是否存在。



# mips-converter.py

用来做MIPS指令和其二进制形式转换的工具。

详细使用请参考help：

```shell
source ${NSCSCC2023_BJTU_PI_TOOL_HOME}/sh_lib/check_before_run.sh && ${SHELL} -c "${py} mips-converter.py -h"
```

由于`${py}`的内容特殊（有空格），所以需要使用这种特殊方式执行命令。



# .template

这里有一些模板，它们提供了使用本仓库的环境，你可以直接使用`cp`命令来使用这些模板。

* `.sh`：

  Shell脚本模板。



# 其他

## 关于环境

前面已经提到，为了统一环境，我们使用`conda`管理python环境。如果需要变更环境信息（比如使用了新的python库），请执行`export_env.sh`。

> 理论上可以用`git`的hook来自动化这个过程，但是个人觉得这会让这个库的开发非常别扭，就没有这么做。如果你有成熟的想法请提pr、issue。

如果需要更新本地的环境（比如本仓库的其他开发者变更了python环境，你这里需要更新到本地），请执行`upd_env.sh`。

