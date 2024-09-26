import subprocess
import re

def get_gpu_info(ip):
    try:
        cmd = f"ssh {ip} nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu,compute_mode --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        
        gpu_info = []
        for line in output.strip().split('\n'):
            index, memory_used, memory_total, utilization, compute_mode = line.split(', ')
            memory_usage = (float(memory_used) / float(memory_total)) * 100
            gpu_info.append({
                'index': int(index),
                'memory_usage': memory_usage,
                'utilization': float(utilization),
                'process_name': None,
                'process_id': None
            })
        
        # 获取进程信息
        cmd = f"ssh {ip} nvidia-smi --query-compute-apps=gpu_uuid,pid,name --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        
        # 创建 GPU UUID 到索引的映射
        uuid_to_index = {}
        cmd = f"ssh {ip} nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits"
        uuid_output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        for line in uuid_output.strip().split('\n'):
            index, uuid = line.split(', ')
            uuid_to_index[uuid] = int(index)
        
        for line in output.strip().split('\n'):
            if line:
                gpu_uuid, pid, name = line.split(', ')
                if gpu_uuid in uuid_to_index:
                    gpu_index = uuid_to_index[gpu_uuid]
                    for gpu in gpu_info:
                        if gpu['index'] == gpu_index:
                            gpu['process_name'] = name
                            gpu['process_id'] = int(pid)
                            break
        
        return gpu_info
    except Exception as e:
        print(f"Error getting GPU info for {ip}: {str(e)}")
        return None

def update_server_gpu_info(server):
    gpu_info = get_gpu_info(server.ip)
    if gpu_info:
        server.gpu_count = len(gpu_info)
        server.gpu_usage = sum(gpu['utilization'] for gpu in gpu_info) / len(gpu_info)
        return gpu_info
    return None