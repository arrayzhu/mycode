#!/bin/bash # 设置解释器为bash
eval $(stat -s $1) # 获取文件状态
echo "当前checkpoint文件:"$1 "属主uid为:"$st_uid # 输出st_uid字段 即属主uid

# 建议： 用法： cron没2秒调用一次 watch运行
