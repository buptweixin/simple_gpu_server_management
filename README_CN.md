# GPU 服务器管理系统

一个基于 Web 的 GPU 服务器管理和监控系统。

## 简介

GPU 服务器管理系统是一个基于 Flask 的 Web 应用程序，旨在帮助组织管理和监控他们的 GPU 服务器。它提供了服务器占用、实时 GPU 使用率监控和用户管理等功能。

## 功能特性

- 用户认证和授权
- GPU 服务器管理（添加、删除、更新）
- 实时 GPU 使用率监控
- 服务器占用和释放
- 用户管理（管理员功能）
- 带有服务器统计和 GPU 使用历史的仪表板

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/simple_gpu_server_management.git
   cd gpu-server-management
   ```

2. 创建并激活虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # 在 Windows 上，使用 `venv\Scripts\activate`
   ```

3. 安装所需的包：
   ```
   pip install -r requirements.txt
   ```

4. 设置数据库：
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. 在项目根目录创建 `.env` 文件并添加以下内容：
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///site.db
   ```

## 使用方法

1. 启动应用程序：
   ```
   flask run
   ```

2. 打开网页浏览器并访问 `http://localhost:5000`

3. 使用默认管理员账户登录：
   - 用户名：admin
   - 密码：admin

4. 首次登录后请更改管理员密码

5. 开始添加服务器和管理用户

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

该项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。