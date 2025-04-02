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

1. 修改main_preReport逻辑,每次根据入参搜索数据，如果已经存在，不要删除，而是直接取出来，和要写入的数据进行比较，如果写入的数据中在取出的数据中包含，则删除这条写入的数据。全部比较好后，如果写入数据还有剩余，则把这些数据写入到数据库中。

xxljobRun中有一个函数，这个函数做以下任务。
1. 根据当前时间格式化为年月日%Y%m%d,作为参数。先打印给我看下是否正确，我确认后正确后，再分别调用process_report_data和process_preReport_data 生成数据。
2. 日期参数修改下，获取当前日期后，需要和3月31日,6月30日,9月30日,12月31日 这几个日期作比较，获取离最近但还没有达到的那个日期


执行main_report 报错cannot access local variable 'big_df' where it is not associated with a value
我调用了F:\miniconda3\envs\autogen\Lib\site-packages\akshare\stock_feature\stock_yjbb_em.py 这个文件里的stock_yjbb_em 这个方法

服务器上创建了虚拟环境kksStock 在虚拟环境中运行xxlJobRun.py，帮我写个Windows脚本来运行这个python.之后我需要在xxljob中去使用


1. 了解initDb.py的数据结构。
2. 我接下来说的每一期是指每年的3月31日,6月30日,9月30日,12月31日。最新一次就是和当前日期作比较后得到最新的一期。
3. 从stock_prereport搜索report_date最新一期，并且业绩变动在2倍以上的数据。前5个就可以了
4. 从stock_report搜索report_date最新一期，然后根据相同stock_code获取对应数据，然后比较这只股票业绩是否超预期，获取5个就可以了。
5.所有分析生成的文件请放到analyse文件夹中。
6. 生成一份报表，包含业绩变动2倍以上股票详细信息，和超期股票的相信信息，以静态html作为生成对象，尽量美化下。


在analyse 文件夹下需要有个配置文件，
1，设置queryNum,取出多少数据按照这个值来决定,现在是5.
2. 设置multiple-low,multiple-high,业绩变动取multiple-low这个值的倍数以上的数据，之前是2倍,同时限定下倍数在multiple-high 这个之下，如果multiple-high设置为-1，则无限大


1. 修改下，配置文件添加查询日期，如果查询日期有值，则根据这个日期生成数据。如果没有，则还是按照原来的逻辑生成。
2. 原来逻辑中，如果找不到当期的数据，不要早最近的，而是作为没找到数据处理，比如现在应该是20250331，如果没找到20250331的数据则不生产

业绩超预期分析期: 不应该是 20241231，而是20250331，然后在他的程序内容，应该去取当期是20241231的stock_prereport数据做比较

相同的股票代码显示时应该去重，现在5个数据有2个股票代码是重复的。应该只取一条就可以了


日期查询的逻辑还是要修改下。预报业绩变动的日期往后取，超预期报告的日期往前取。比如现在20250328，预报业绩往后取查询的日期是20250331，超预期报告日期应该是20241231，周期一共4个，每一期是指每年的3月31日,6月30日,9月30日,12月31日，如果今天是20240506，那么预报业绩变动的日期20240630，超预期报告日期20240331

1. .env添加一个变量超预期倍数。数值范围在（0-100）
2. 业绩超预期报表分析有问题。应该取当期业绩报告的净利润，和上期预报（stock_prereport）的预测数值作比较，如果百分比高出新增超预期倍数变量的倍数，则显示。显示字段也稍微调整下，需要显示上期预报预测数值，本期净利润，净利润对于预测数值的倍数，预告类型，股票代码，股票名称

1. 我觉得直接通过一句sql,来分析业绩超预期似乎有难度。可以把逻辑拆开，先取出当期业绩报告的净利润，和上期预报（stock_prereport）的预测数值（预测数值可能有多条，取值最大的）。然后开始遍历这些数据。遍历中如果本期净利润是预测数值的N倍，则需要最终显示到html中。显示的字段不变。
2. N倍中的N 值取.env中的EXCEED_MULTIPLE


业绩超预期 有问题，比较的是当期的业绩报告(stock_report）和上一期的预测报告（stock_prereport），一期的定义是指每年的3月31日,6月30日,9月30日,12月31日

查询数据 是要根据配置QUERY_NUM获取相应的条数，但超预期分析报表是需要先获取全部数据后，对超预期倍数进行排序后，再获取前N条，现在好像只是获取到了5条就结束了，没有对整个查询的数据集进行排序后获取

1. 修改配置文件,EXCEED_MULTIPLE 改为2个值，最小超预期倍数，和最大超预期倍数。
2. generate_report get_exceed_area_stocks中和EXCEED_MULTIPLE相应的逻辑也调整，值再最小倍数和最大倍数之间

1. 修改generate_report.py，当获取到查询high_change_stocks和exceed_area_stocks 后，再帮我获取每只股票的资金流入情况。参考origApi文件的 singleAmountFlow,传入参数stock_code就是当前股票号码，market股则是这样的：300开头传入'bj','6'开头传入'sh','001,002,003,004'开头传入'sz'，每只股票只需要获取最近5天的数据（和singleAmountFlow例子一样）。单独使用一个函数做现金流信息查询

2. 获取了每只股票的资金流入情况后，再打印报表时，可以显示出来，显示的方式为：原有股票信息行作为头行，现金流的信息作为子行列出

1. 最近5日资金流向（万元）右对齐，点击这行，可以关闭资金流数据信息。默认关闭状态
2. 资金流数据字体稍微小点，并也加上对应的header标题， 
3. 原来股票信息背景色稍微高亮，和资金流数据信息有明显的区分

1.把生成html和查询计算逻辑分离开来，生成html的代码文件为createHtml.py放在当前目录下，然后现在的文件引用这个模块生成html

generate_report中get_target_report_dates有问题。如果query_date不是是auto,则prereport_date取指定日期，exceed_date取prereport_date所在期间的上一期，，每一期是指每年的3月31日,6月30日,9月30日,12月31日，参考get_next_quarter_end和get_prev_quarter_end这两个函数

修改xxlJobRun。如果没有指定日期，那么根据当前日期，业绩报告取当期的，业绩预告取下期的，比如现在20250402 ，当期应该是20250331，下期应该是20250630.每一期是指每年的3月31日,6月30日,9月30日,12月31日

1. 把generate_report中关于期间，当期，前期等所有日期计算的独立写道一个文件中,dateManager.然后让generate_report来引用，同时让xxljobRun也来引用

1. 修改generate_report文件中get_exceed_area_stocks函数。 获取当期业绩报告数据SQL不变。
2. 当获取好业绩报告后,获取当期的预报数据。放在两个变量中。遍历每一个业绩报告，使用stock_code找到对应的预报数据。比较所有股票并计算超预期倍数（就是现在的比较逻辑）
3. 如果某一个stock_code 没有找到对应的预报数据，则到数据库请求上一期的预报数据，放到另一个变量，然后再去寻找。再找不到就算了


然后就开始遍历数据，获取每一条数据后，到数据库的预报表中找到对应的最近的预报数据，然后的逻辑就是之前比较并计算超预期倍数。如果对应的最近的预报数据