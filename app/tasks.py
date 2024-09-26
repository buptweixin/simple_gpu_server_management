from app import db
from app.models import Server, gpu_info, gpu_usage_history
from app.utils import update_server_gpu_info
from flask import current_app
from datetime import datetime
import pytz

def update_all_servers_gpu_info():
    with current_app.app_context():
        servers = Server.query.all()
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(shanghai_tz)
        
        for server in servers:
            gpu_info_list = update_server_gpu_info(server)
            if gpu_info_list:
                # 清理旧的 gpu_info 记录
                gpu_info.query.filter_by(server_id=server.id).delete()
                
                # 更新 gpu_info 表
                for gpu in gpu_info_list:
                    new_gpu_info = gpu_info(
                        server_id=server.id,
                        gpu_index=gpu['index'],
                        memory_usage=gpu['memory_usage'],
                        utilization=gpu['utilization'],
                        process_name=gpu['process_name'],
                        process_id=gpu['process_id']
                    )
                    db.session.add(new_gpu_info)
                
                # 更新 gpu_usage_history 表
                avg_usage = sum(gpu['utilization'] for gpu in gpu_info_list) / len(gpu_info_list)
                new_usage_history = gpu_usage_history(
                    server_id=server.id,
                    timestamp=current_time,
                    usage=avg_usage
                )
                db.session.add(new_usage_history)
        
        try:
            db.session.commit()
            print(f"GPU information updated successfully at {current_time.strftime('%Y-%m-%d %H:%M:%S')}.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating GPU information: {str(e)}")