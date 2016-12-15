#!/bin/bash    #设定解释器为bash

echo "## usage: ./checkpoint {args}, args: times of spark process which has been started. ##" #输出 用法：./checkpoint {参数}, 参数为第几次执行spark进程
echo "## This script must be runned at checkpoint directory. ##" #输出 这个脚本必须在检查点目录下运行

if test -z "$1" # 如果参数不存在
then
echo "arg is null, please restart script like this: ./checkpoint 1" # 输出 参数为空，请按照下面方式重新运行脚本：./checkpoint 1
exit 2 # 错误退出
fi

sleep 2 # 睡眠2秒
echo "checking..." # 输出 检查中...

while [ 1 ] # 无限循环
do
counter=`ls -l | grep "^d" | wc -l` # 获取目录数
counter=`expr $counter + 0` # counter转整形
cpnum=`expr $1 + 1` # cpnum为参数+1
if [[ ("$counter" = "$cpnum") ]];then # 如果counter和cpnum相等
sleep 1 # 睡眠1秒
    else
echo "WARNING: checkpoint maybe has been hacked!" # 输出 警告：检查点可能被黑
    fi

sleep 2 # 睡眠2秒
done;
