from datetime import datetime

def get_quarter_dates():
    """获取所有季度末日期"""
    return [
        (3, 31),
        (6, 30),
        (9, 30),
        (12, 31)
    ]

def get_next_quarter_end():
    """获取下一个最近的季度末日期（用于业绩预告）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day

    quarter_dates = get_quarter_dates()

    for q_month, q_day in quarter_dates:
        if month < q_month or (month == q_month and day <= q_day):
            return f"{year}{q_month:02d}{q_day:02d}"
    
    return f"{year + 1}0331"

def get_prev_quarter_end():
    """获取上一个最近的季度末日期（用于业绩报告）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    quarter_dates = get_quarter_dates()
    
    # 获取当前季度的索引
    current_quarter_idx = (month - 1) // 3
    
    # 计算上一个季度的年份和月份
    if current_quarter_idx == 0:  # 如果是第一季度
        prev_year = year - 1
        prev_month, prev_day = quarter_dates[3]  # 返回上一年第四季度
    else:
        prev_year = year
        prev_month, prev_day = quarter_dates[current_quarter_idx - 1]
    
    return f"{prev_year}{prev_month:02d}{prev_day:02d}"
