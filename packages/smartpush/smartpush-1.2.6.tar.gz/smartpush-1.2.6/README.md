# SmartPush_AutoTest



## Getting started

## 打包/上传的依赖
```
pip install wheel
pip install twine
```


## 打包-打包前记得修改版本号
```
python setup.py sdist bdist_wheel
```


## 上传到pipy的命令
```
twine upload dist/*
```

# 平台调用demo
```
import json # import 请置于行首
from smartpush.export.basic import ExcelExportChecker
from smartpush.export.basic import GetOssUrl
oss=GetOssUrl.get_oss_address_with_retry(vars['queryOssId'], "${em_host}", json.loads(requestHeaders))
result = ExcelExportChecker.check_excel_all(expected_oss=oss,actual_oss=vars['exportedOss'],ignore_sort =True)
assert result
```
## check_excel_all() 支持拓展参数
### check_type = "including"   如果需要预期结果包含可传  eg.联系人导出场景可用
### ignore_sort = 0   如果需要忽略内部的行排序问题可传，eg.email热点点击数据导出无排序可用，传指定第几列，0是第一列
### skiprows = 1   传1可忽略第一行，   eg.如flow的导出可用，动态表头不固定时可以跳过读取第一行
