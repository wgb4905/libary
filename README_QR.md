# 图书管理程序 - 二维码功能

## 功能已成功添加

已为您的图书管理程序成功添加了完整的二维码功能系统。

## 新增功能清单

### 1. 核心功能
- ✅ 每本图书副本生成唯一二维码
- ✅ 扫描二维码查询借阅状态
- ✅ 通过二维码一键借阅/归还图书
- ✅ 移动端自适应扫描界面
- ✅ 二维码打印功能

### 2. 管理功能
- ✅ 管理后台二维码预览
- ✅ 批量生成二维码
- ✅ 单个副本二维码管理
- ✅ 二维码状态监控

### 3. 技术实现
- ✅ 数据库模型扩展（BookCopy新增qr_code字段）
- ✅ 5个新增视图函数
- ✅ 4个新增HTML模板
- ✅ 6个新增URL路由
- ✅ 管理命令支持
- ✅ API接口

## 文件变更

### 修改的文件
1. `library/models.py` - 新增qr_code字段和生成方法
2. `library/views.py` - 新增5个视图函数
3. `library/urls.py` - 新增6个URL路由
4. `library/admin.py` - 增强管理后台

### 新增的文件
1. `library/templates/library/qr_scan.html` - 标准扫描页面
2. `library/templates/library/qr_mobile_scan.html` - 移动端扫描页面
3. `library/templates/library/qr_display.html` - 打印页面
4. `library/templates/library/qr_management.html` - 管理页面
5. `library/management/commands/generate_qr_codes.py` - 管理命令
6. `test_qr_functionality.py` - 测试脚本
7. `setup_qr_functionality.py` - 部署脚本
8. `QR_CODE_USAGE.md` - 使用说明
9. `README_QR.md` - 本文件

## 快速开始

### 第一步：安装依赖
```bash
pip install qrcode
```

### 第二步：数据库迁移
```bash
cd library
python manage.py makemigrations
python manage.py migrate
```

### 第三步：生成二维码
```bash
# 为所有图书副本生成二维码
python manage.py generate_qr_codes
```

### 第四步：测试功能
```bash
# 运行测试脚本
python test_qr_functionality.py

# 或使用部署脚本
python setup_qr_functionality.py
```

## 使用方式

### 1. 扫描二维码
- 访问：`/scan/<bookcopy_id>/`
- 或直接扫描图书上的二维码

### 2. 管理二维码
- 访问：`/book/<book_id>/qr-management/`
- 或通过Django管理后台

### 3. 打印二维码
- 访问：`/qr/print/<bookcopy_id>/`
- 点击打印按钮

## 移动端支持

系统自动检测设备类型：
- 📱 移动设备：显示优化界面
- 💻 桌面设备：显示标准界面

## API接口

获取图书副本信息：
```
GET /api/qr-info/<bookcopy_id>/
```

返回JSON格式：
```json
{
  "id": 1,
  "book_title": "图书名称",
  "is_available": true,
  "scan_url": "http://..."
}
```

## 管理命令

```bash
# 基本使用
python manage.py generate_qr_codes

# 为指定图书生成
python manage.py generate_qr_codes --book-id 1

# 强制重新生成
python manage.py generate_qr_codes --force
```

## 技术特点

1. **自动生成**：保存BookCopy时自动生成二维码
2. **唯一标识**：每个副本有唯一二维码
3. **响应式设计**：适配各种设备
4. **安全验证**：借阅/归还需要登录
5. **批量操作**：支持批量生成和管理
6. **打印优化**：专业打印布局

## 故障排除

### 二维码不显示
1. 检查`media/qr_codes`目录权限
2. 运行`python manage.py collectstatic`
3. 检查MEDIA_URL设置

### 扫描功能异常
1. 检查用户登录状态
2. 查看浏览器控制台
3. 检查CSRF令牌

### 移动端问题
1. 测试不同设备
2. 检查CSS响应式
3. 验证设备检测逻辑

## 扩展建议

未来可考虑添加：
1. 📊 扫描统计功能
2. 🎨 二维码美化定制
3. 📱 微信小程序集成
4. 🔔 到期提醒功能
5. 📄 批量打印优化

## 支持

详细使用说明请查看：
- `QR_CODE_USAGE.md` - 完整使用指南
- 运行测试脚本验证功能
- 查看Django错误日志

---

**二维码功能已成功集成到您的图书管理程序中！**

现在每本图书都有唯一的二维码，用户可以通过扫描二维码快速查询借阅状态并进行借阅/归还操作。管理员可以在后台管理所有二维码，并支持批量生成和打印功能。