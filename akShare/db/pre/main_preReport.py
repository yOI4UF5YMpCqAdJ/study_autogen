import akshare as ak
from ..db_manager import db_manager
from create_preReport_header_table import create_preReport_header_table, update_header_status
from create_preReport_table import create_stock_preReport_table
from insert_preReport_data import insert_preReport_data

def check_and_create_tables(force_recreate=False, date="20250331"):
    """
    检查头表和数据表是否存在，根据需要创建或重建表
    
    参数:
        force_recreate: bool, 是否强制重建表，默认为False
        date: str, 查询参数日期，格式为YYYYMMDD，默认为20250331
    
    返回:
        tuple: (tables_exist, header_table_exists, detail_table_exists, batch_no)
            tables_exist: bool, 表示所需的表是否已经存在
            header_table_exists: bool, 头表是否存在
            detail_table_exists: bool, 数据表是否存在
            batch_no: str, 批次号（如果创建了新批次）
    """
    try:
        # 连接到数据库
        if not db_manager.connect():
            print("数据库连接失败")
            return False, False, False, None
            
        # 检查表是否存在
        print("\n检查表是否存在...")
        db_manager.execute("SHOW TABLES LIKE 'stock_prereport_header'")
        header_table_exists = db_manager.fetchone() is not None
        
        db_manager.execute("SHOW TABLES LIKE 'stock_preReport'")
        detail_table_exists = db_manager.fetchone() is not None
        
        print(f"头表存在: {header_table_exists}, 数据表存在: {detail_table_exists}")
        
        # 如果强制重建或表不存在，则创建表
        batch_no = None
        if force_recreate or not (header_table_exists and detail_table_exists):
            print("\n需要创建或重建表...")
            
            # 先删除数据表（如果存在），因为它依赖于头表
            if detail_table_exists:
                print("删除现有数据表...")
                db_manager.execute("DROP TABLE IF EXISTS stock_preReport")
                detail_table_exists = False
            
            # 然后处理头表
            if force_recreate and header_table_exists:
                print("删除现有头表...")
                db_manager.execute("DROP TABLE IF EXISTS stock_prereport_header")
                header_table_exists = False
            
            # 创建头表并获取批次号
            if not header_table_exists:
                print("创建新头表...")
                header_success, batch_no = create_preReport_header_table(True, date)
                if not header_success:
                    print("创建头表失败")
                    return False, False, False, None
                header_table_exists = True
            else:
                # 如果头表存在但数据表不存在，创建新批次
                print("头表已存在，创建新批次...")
                header_success, batch_no = create_preReport_header_table(False, date)
                if not header_success:
                    print("创建新批次失败")
                    return False, header_table_exists, detail_table_exists, None
        else:
            # 如果两个表都存在且不强制重建，则创建新批次
            print("\n表已存在，只创建新批次...")
            header_success, batch_no = create_preReport_header_table(False, date)
            if not header_success:
                print("创建新批次失败")
                return False, header_table_exists, detail_table_exists, None
        
        return True, header_table_exists, detail_table_exists, batch_no
        
    except Exception as e:
        print(f"检查和创建表时发生错误: {e}")
        return False, False, False, None

def process_preReport_data(date="20250331", force_recreate=False):
    """
    主函数：调用ak.stock_yjyg_em函数，当返回有数据时：
    1. 检查表是否存在，不存在则创建
    2. 创建头表记录，生成批次号
    3. 将数据插入到表中
    4. 更新头表状态
    
    参数:
        date: str, 业绩预告日期，格式为"YYYYMMDD"
        force_recreate: bool, 是否强制重新创建表，默认为False
        
    返回:
        bool: 表示操作是否成功
    """
    try:
        print("开始处理股票业绩预告数据...")
        
        # 调用akshare函数获取数据
        stock_yjyg_em_df = ak.stock_yjyg_em(date=date)
        
        # 检查是否有数据返回
        if stock_yjyg_em_df.empty:
            print("没有获取到数据，请检查日期参数或稍后再试")
            return False
        
        print(f"成功获取到{len(stock_yjyg_em_df)}条业绩预告数据")
        
        # 检查是否存在相同查询参数的记录
        has_existing_query = create_preReport_header_table.check_existing_query(date)
        
        if has_existing_query:
            print("\n发现相同日期参数的记录，将删除对应的子表数据")
            if not create_preReport_header_table.delete_preReport_detail_by_date(date):
                print("删除子表数据失败，终止数据处理")
                return False
        
        # 步骤1: 检查并创建必要的表
        print("\n步骤1: 检查并创建必要的表")
        tables_ready, header_exists, detail_exists, batch_no = check_and_create_tables(force_recreate, date)
        
        if not tables_ready or not batch_no:
            print("表准备失败，终止数据处理")
            return False
            
        print(f"生成批次号: {batch_no}")
        
        # 步骤2: 如果数据表不存在，则创建
        if not detail_exists:
            print("\n步骤2: 创建数据表")
            table_created = create_stock_preReport_table(stock_yjyg_em_df, batch_no, True)
            if not table_created:
                print("创建数据表失败，终止数据处理")
                update_header_status(batch_no, 0, "FAILED", "创建数据表失败")
                return False
        
        # 步骤3: 插入数据
        print("\n步骤3: 插入数据")
        success, insert_count = insert_preReport_data(stock_yjyg_em_df, batch_no)
        if not success:
            print("插入数据失败，终止数据处理")
            # 更新头表状态为失败
            update_header_status(batch_no, 0, "FAILED", "插入数据失败")
            return False
            
        # 更新头表状态
        print("\n步骤5: 更新头表状态")
        status_updated = update_header_status(batch_no, insert_count, "COMPLETED", "处理成功")
        if not status_updated:
            print("警告: 更新头表状态失败，但数据处理已完成")
        
        # 展示表结构
        print("\n表 stock_preReport 的结构：")
        db_manager.connect()
        db_manager.execute("DESCRIBE stock_preReport")
        for field in db_manager.fetchall():
            print(field)
        
        db_manager.close()
        
        print("\n数据处理完成！")
        return True
        
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        db_manager.close()
        return False

if __name__ == "__main__":
    process_preReport_data(force_recreate=True)
