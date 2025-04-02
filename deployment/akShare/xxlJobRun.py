import sys
import os
from datetime import datetime

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from akShare.db.report.main_report import process_report_data
from akShare.db.pre.main_preReport import process_preReport_data
from akShare.log.logger import setup_logger
from akShare.analyse.date_utils import get_next_quarter_end, get_prev_quarter_end
from akShare.analyse.generate_report import main as generate_report_main

# 设置日志记录器
logger = setup_logger('xxlJobRun')

def process_daily_report(date=None):
    """
    处理每日业绩报告和业绩预告数据
    1. 如果指定了日期，则使用指定的日期
    2. 如果没有指定日期：
       - 业绩报告使用当期日期（如20250402应使用20250331）
       - 业绩预告使用下期日期（如20250402应使用20250630）
    
    返回:
        tuple: (bool, bool) 表示(业绩报告处理结果, 业绩预告处理结果)
    """
    try:
        # 获取日期参数并打印
        current_date = datetime.now()
        logger.info("=== 日期参数 ===")
        logger.info(f"当前日期: {current_date.strftime('%Y-%m-%d')}")
        
        # 如果指定了日期，则两种数据都使用指定的日期
        if date:
            report_date = date
            prereport_date = date
        else:
            # 否则业绩报告使用当期，业绩预告使用下期
            report_date = get_prev_quarter_end()  # 使用上一个季度末作为业绩报告日期
            prereport_date = get_next_quarter_end()  # 使用下一个季度末作为业绩预告日期
        
        logger.info(f"业绩报告处理日期: {report_date}")
        logger.info(f"业绩预告处理日期: {prereport_date}")
        
        report_result = False
        prereport_result = False
        
        try:
            # 处理业绩报告数据
            logger.info("=== 处理业绩报告数据 ===")
            report_result = process_report_data(date=report_date)
            # 如果只是没有获取到数据，认为是正常情况
            if report_result is False:
                logger.info("业绩报告：没有获取到数据")
                report_result = True
        except Exception as e:
            logger.error(f"业绩报告数据处理出错: {e}")
            report_result = False
        
        try:
            # 处理业绩预告数据
            logger.info("=== 处理业绩预告数据 ===")
            prereport_result = process_preReport_data(date=prereport_date)
            # 如果只是没有获取到数据，认为是正常情况
            if prereport_result is False:
                logger.info("业绩预告：没有获取到数据")
                prereport_result = True
        except Exception as e:
            logger.error(f"业绩预告数据处理出错: {e}")
            prereport_result = False
        
        # 生成分析报告
        logger.info("=== 生成分析报告 ===")
        generate_report_main()
        
        return report_result, prereport_result
        
    except KeyboardInterrupt:
        logger.warning("操作已取消")
        return False, False
    except Exception as e:
        logger.error(f"处理数据时发生错误: {e}")
        return False, False

if __name__ == "__main__":
    date_param = sys.argv[1] if len(sys.argv) > 1 else None
    report_result, prereport_result = process_daily_report(date_param)
    # 如果任一处理失败，返回非零退出码
    if not report_result or not prereport_result:
        logger.error("任务执行失败")
        sys.exit(1)
    logger.info("任务已执行")
    sys.exit(0)
