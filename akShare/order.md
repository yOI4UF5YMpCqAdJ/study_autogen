preReport 调用ak.stock_yjyg_em，当返回有数据时，
根据返回数据的名字，创建mysql表，表名：stock_preReport。字段名不要中文

1. 我将这3个文件移动到了db文件夹，然后创建一个.env文件，数据库连接相关信息写入这个配置文件
2. 创建一个数据库管理类，任何打开数据库，关闭数据的操作都由这个类控制，这个文件使用刚创建的配置文件进行数据库连接
3. 修改任何使用数据库操作的地方，使用数据库管理类

1. 另外写一个临时脚本，创建一个头表，stock_prereport_header,记录当前查询的时间,有一个批次号字段，字段内容是年月日时分秒
2. 修改stock_prereport表,添加对应的批次号字段,这个字段是stock_prereport_header的外键

1. 修改下 main_preReport 写入数据前，需要头判断是否存在相同的查询时间，如果存在，则不用再次创建头表数据，此时需要将关联的子表数据全部删除后再次写入新的数据。如果不存在则写入逻辑不变

1. 将stock_prereport和stock_prereport_header两个表中的batch_no字段修改为report_date。
2. 将report_date设置为process_preReport_data 入参data 的值
3. 修改相应的代码

1. 根据origApi 文件的getReport 写一套类似pre文件夹下main_preReport.py的功能。大概也是通过stock_yjbb_em_df = ak.stock_yjbb_em(date="20220331") 获取数据,写入数据库表，也是头表和数据表，逻辑和main_preReport类似，创建的文件放在report文件夹下
    
    <!-- stock_prereport，stock_prereport_header，stock_report_header，stock_report， -->
帮我单独创建一个文件位于db文件夹下，名字叫initDb. 检查数据库中是否存在db_report和db_preReport 中涉及的几张表，没有的话就调用这两个文件的创建函数创建表

1. initData.py  写一段代码帮我生成一组数据列表。数据的格式是年月日。要求是年从2014年到2100年。月日是每年的3月31日,6月30日,9月30日,12月31日。根据这个规则生成数据。然后导入到数据表stock_period的period字段中。使用db_manager访问数据库

1. 我有个xxljob,我想把main_preReport和main_report 每天去运行一下，怎么做？

1. 调用