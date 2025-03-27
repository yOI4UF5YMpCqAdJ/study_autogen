import sys
import os
from datetime import datetime
# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from akShare.db.report.main_report import process_report_data
from akShare.db.pre.main_preReport import process_preReport_data
from akShare.log.logger import setup_logger

# 设置日志记录器
logger = setup_logger('xxlJobRun')

def get_next_quarter_end():
    """
    获取下一个最近的季度末日期
    季度末日期为：3月31日、6月30日、9月30日、12月31日
    
    返回:
        str: 格式为YYYYMMDD的日期字符串
    """
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day
    
    # 定义季度末月份
    quarter_months = [3, 6, 9, 12]
    
    # 找到下一个季度末
    for quarter_month in quarter_months:
        # 如果当前月小于季度月，或者当前月等于季度月但天数小于月末
        if (month < quarter_month) or (month == quarter_month and day <= 31):
            # 构建目标日期字符串
            if quarter_month in [3, 12]:  # 3月和12月是31日
                return f"{year}{quarter_month:02d}31"
            else:  # 6月和9月是30日
                return f"{year}{quarter_month:02d}30"
    
    # 如果所有季度都已过，返回下一年的第一个季度末
    return f"{year + 1}0331"

def process_daily_report(date=None):
    """
    处理每日业绩报告和业绩预告数据
    1. 获取最近的季度末日期
    2. 分别调用业绩报告和业绩预告的处理函数
    
    返回:
        tuple: (bool, bool) 表示(业绩报告处理结果, 业绩预告处理结果)
    """
    try:
        # 获取日期参数并打印
        current_date = datetime.now()
        target_date = date if date else get_next_quarter_end()
        logger.info("=== 日期参数 ===")
        logger.info(f"当前日期: {current_date.strftime('%Y-%m-%d')}")
        logger.info(f"目标处理日期: {target_date}")
        
        report_result = False
        prereport_result = False
        
        try:
            # 处理业绩报告数据
            logger.info("=== 处理业绩报告数据 ===")
            report_result = process_report_data(date=target_date)
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
            prereport_result = process_preReport_data(date=target_date)
            # 如果只是没有获取到数据，认为是正常情况
            if prereport_result is False:
                logger.info("业绩预告：没有获取到数据")
                prereport_result = True
        except Exception as e:
            logger.error(f"业绩预告数据处理出错: {e}")
            prereport_result = False
        
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
