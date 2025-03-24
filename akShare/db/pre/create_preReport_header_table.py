import pymysql
from datetime import datetime
from ..db_manager import db_manager

def create_preReport_header_table(force_recreate=True, date="20250331"):
    """
    创建业绩预告头表 stock_prereport_header，记录查询批次信息
    
    参数:
        force_recreate: bool, 是否强制重新创建表，默认为True
        date: str, 查询参数日期，格式为YYYYMMDD，默认为20250331
    
    返回:
        bool: 表示操作是否成功
        str: 当前生成的批次号
    """
    try:
        # 生成批次号 - 年月日时分秒格式
        batch_no = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 连接到数据库
        if not db_manager.connect():
            print("数据库连接失败")
            return False, None
        
        # 判断是否需要重新创建表
        if force_recreate:
            print("删除头表（如果存在）...")
            db_manager.execute("DROP TABLE IF EXISTS stock_prereport_header")
            
        # 检查表是否存在
        db_manager.execute("SHOW TABLES LIKE 'stock_prereport_header'")
        table_exists = db_manager.fetchone()
        
        # 如果表不存在，则创建
        if not table_exists or force_recreate:
            print("创建头表 stock_prereport_header...")
            
            # 创建表SQL语句
            create_table_sql = """
            CREATE TABLE stock_prereport_header (
                id INT AUTO_INCREMENT PRIMARY KEY,
                batch_no VARCHAR(20) NOT NULL COMMENT '批次号(年月日时分秒)',
                query_param VARCHAR(50) COMMENT '查询参数',
                record_count INT DEFAULT 0 COMMENT '记录数量',
                status VARCHAR(20) DEFAULT 'PENDING' COMMENT '处理状态',
                remark TEXT COMMENT '备注信息',
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                UNIQUE KEY uk_batch_no (batch_no)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票业绩预告批次信息';
            """
            
            db_manager.execute(create_table_sql)
            print("头表 stock_prereport_header 创建成功！")
        
        # 插入新的批次记录
        print(f"创建新批次: {batch_no}")
        insert_sql = """
        INSERT INTO stock_prereport_header 
        (batch_no, query_param, status) 
        VALUES (%s, %s, %s)
        """
        
        query_param = f"date={date}"  # 使用传入的date参数
        status = "PENDING"
        
        db_manager.execute(insert_sql, (batch_no, query_param, status))
        db_manager.commit()
        
        print("头表记录创建成功！")
        
        return True, batch_no
        
    except Exception as e:
        print(f"创建头表时发生错误: {e}")
        return False, None
        
    finally:
        db_manager.close()

def check_existing_query(date_str):
    """
    检查是否存在相同查询参数的记录
    
    参数:
        date_str: str, 查询参数中的日期，格式为YYYYMMDD
        
    返回:
        bool: 表示是否存在相同查询参数的记录
    """
    try:
        if not db_manager.connect():
            print("数据库连接失败")
            return False
            
        check_sql = """
        SELECT COUNT(*) 
        FROM stock_prereport_header 
        WHERE query_param = %s
        """
        query_param = f"date={date_str}"
        db_manager.execute(check_sql, (query_param,))
        count = db_manager.fetchone()[0]
        
        return count > 0
        
    except Exception as e:
        print(f"检查查询时间时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

def delete_preReport_detail_by_date(date_str):
    """
    根据查询参数删除子表中的数据
    
    参数:
        date_str: str, 查询参数中的日期，格式为YYYYMMDD
        
    返回:
        bool: 表示操作是否成功
    """
    try:
        if not db_manager.connect():
            print("数据库连接失败")
            return False
            
        # 先找到对应query_param的batch_no
        select_sql = """
        SELECT batch_no 
        FROM stock_prereport_header 
        WHERE query_param = %s
        """
        query_param = f"date={date_str}"
        db_manager.execute(select_sql, (query_param,))
        batch_nos = db_manager.fetchall()
        
        if not batch_nos:
            print("未找到对应日期的批次号")
            return True
            
        # 删除这些batch_no对应的子表数据
        for batch_no in batch_nos:
            delete_sql = """
            DELETE FROM stock_preReport 
            WHERE batch_no = %s
            """
            db_manager.execute(delete_sql, (batch_no[0],))
        
        db_manager.commit()
        print(f"成功删除日期参数 {date_str} 的子表数据")
        return True
        
    except Exception as e:
        print(f"删除子表数据时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

def update_header_status(batch_no, record_count, status="COMPLETED", remark=None):
    """
    更新头表状态
    
    参数:
        batch_no: str, 批次号
        record_count: int, 记录数量
        status: str, 状态 (PENDING, PROCESSING, COMPLETED, FAILED)
        remark: str, 备注信息
        
    返回:
        bool: 表示操作是否成功
    """
    try:
        if not db_manager.connect():
            print("数据库连接失败")
            return False
            
        update_sql = """
        UPDATE stock_prereport_header 
        SET record_count = %s, status = %s, remark = %s 
        WHERE batch_no = %s
        """
        
        db_manager.execute(update_sql, (record_count, status, remark, batch_no))
        db_manager.commit()
        
        print(f"头表状态更新成功！批次: {batch_no}, 状态: {status}, 记录数: {record_count}")
        return True
        
    except Exception as e:
        print(f"更新头表状态时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

if __name__ == "__main__":
    # 测试创建头表和插入批次记录
    success, batch_no = create_preReport_header_table()
    if success and batch_no:
        print(f"成功创建头表和批次记录，批次号: {batch_no}")
        
        # 测试更新状态
        update_success = update_header_status(batch_no, 100, "COMPLETED", "测试完成")
        if update_success:
            print("成功更新头表状态")
