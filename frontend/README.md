# 地摊叫卖录音生成器 - 前端项目

## 项目简介
一个用于生成地摊叫卖/促销广告语录音的Web工具。

## 技术栈
- Vue.js 3
- Vite
- HTML5 Audio API

## 功能特性
- 文本输入：支持任意叫卖文案
- 多声音选择：男声、女声、童声、方言等
- 背景音乐：5大分类，每类8-12首，支持试听
- 循环间隔设置：0-15秒可调整
- 音频生成与下载：支持MP3格式下载

## 项目结构
```
frontend/
├── public/
│   └── bgm/          # 背景音乐文件目录
├── src/
│   ├── App.vue       # 主组件
│   ├── main.js       # 入口文件
│   └── style.css     # 全局样式
├── index.html        # HTML模板
├── package.json      # 项目配置
└── vite.config.js    # Vite配置
```

## 安装与运行

### 安装依赖
```bash
npm install
```

### 开发环境运行（端口8080，支持热加载）
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## BGM文件准备
请在`public/bgm/`目录下准备背景音乐文件，命名规则：
- 清仓甩卖：clearance_01.mp3, clearance_02.mp3, ...
- 美食叫卖：food_01.mp3, food_02.mp3, ...
- 水果蔬菜：fruits_01.mp3, fruits_02.mp3, ...
- 服装日用品：clothing_01.mp3, clothing_02.mp3, ...
- 超市促销：supermarket_01.mp3, supermarket_02.mp3, ...

## 后端API对接
当前前端代码中，API调用部分使用了模拟数据。实际部署时，需要修改`App.vue`中的`generateAudio`方法，对接真实的后端API：

```javascript
async generateAudio() {
  // ...
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(this.formData)
  })
  const data = await response.json()
  this.audioUrl = data.url
  // ...
}
```

## 注意事项
- 为了获得最佳体验，请确保浏览器支持HTML5 Audio API
- 背景音乐文件需要自行准备并放置在正确的目录中