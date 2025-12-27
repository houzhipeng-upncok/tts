<template>
  <div class="app-container">
    <!-- 认证组件或主应用 -->
    <AuthComponent 
      v-if="!isAuthenticated" 
      @auth-success="handleAuthSuccess"
    />
    
    <div v-else class="main-app">
      <!-- 头部导航 -->
      <header class="app-header">
        <div class="header-content">
          <div class="header-left">
            <h1 class="app-title">地摊叫卖录音生成器</h1>
            <div class="app-description">免费微软 Edge-TTS + 内置BGM + 自动混音 + 可设置循环间隔</div>
          </div>
          <div class="header-right">
            <div class="user-info">
              <span>欢迎，{{ currentUser?.username }}</span>
              <button @click="handleLogout" class="logout-btn">登出</button>
            </div>
          </div>
        </div>
      </header>
      
      <div class="form-container">
        <!-- 文本输入区域 -->
        <div class="form-item">
          <label class="form-label">输入叫卖文案</label>
          <textarea 
            v-model="formData.text"
            class="text-input"
            placeholder="请输入您的叫卖文案，例如：全场 5 元，5 元任选！"
            rows="4"
          ></textarea>
        </div>
        
        <!-- 声音类型选择 -->
        <div class="form-item">
          <label class="form-label">选择声音类型</label>
          <select v-model="formData.voice" class="select-input">
            <option value="zh-CN-YunxiNeural">男声（激情）</option>
            <option value="zh-CN-YunhaoNeural">男声（沉稳）</option>
            <option value="zh-CN-XiaoxiaoNeural">女声（清晰）</option>
            <option value="zh-CN-YunyangNeural">女声（沉稳）</option>
            <option value="zh-CN-Shandong">方言（山东）</option>
            <option value="zh-CN-Sichuan">方言（四川）</option>
            <option value="zh-CN-Northeast">方言（东北）</option>
            <option value="zh-CN-Cantonese">方言（广东）</option>
            <option value="zh-CN-Taiwan">方言（台湾）</option>
          </select>
        </div>
        
        <!-- 背景音乐选择 -->
        <div class="form-item">
          <label class="form-label">选择背景音乐</label>
          <div class="bgm-selector">
            <select v-model="formData.bgmCategory" class="category-select">
              <option value="clearance">清仓甩卖</option>
              <option value="food">美食叫卖</option>
              <option value="fruits">水果蔬菜</option>
              <option value="clothing">服装日用品</option>
              <option value="supermarket">超市促销</option>
            </select>
            
            <div class="bgm-list">
              <button 
                v-for="(bgm, index) in currentBgmList" 
                :key="index"
                :class="['bgm-item', { active: formData.bgm === bgm.file }]"
                @click="formData.bgm = bgm.file"
              >
                {{ bgm.name }}
                <audio :src="bgm.file" :ref="el => audioRefs[index] = el" preload="none"></audio>
                <button 
                  class="preview-btn" 
                  @click.stop="togglePreview(audioRefs[index])"
                  :class="{ playing: playingAudio === audioRefs[index] }"
                >
                  {{ playingAudio === audioRefs[index] ? '⏸️' : '▶️' }}
                </button>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 循环间隔设置 -->
        <div class="form-item">
          <label class="form-label">循环间隔（秒）: {{ formData.interval }}</label>
          <input 
            type="range"
            v-model.number="formData.interval"
            min="0"
            max="15"
            class="range-input"
          >
          <div class="interval-hint">自动在音频尾部增加 {{ formData.interval }} 秒静默</div>
        </div>
        
        <!-- 生成按钮 -->
        <button 
          class="generate-btn"
          @click="generateAudio"
          :disabled="isGenerating"
        >
          {{ isGenerating ? '生成中...' : '生成音频' }}
        </button>
      </div>
      
      <!-- 音频播放器 -->
      <div v-if="audioUrl" class="player-container">
        <h3>生成结果</h3>
        <audio :src="audioUrl" controls class="audio-player"></audio>
        <button @click="downloadAudio" class="download-btn">下载 MP3</button>
      </div>
    </div>
  </div>
</template>

<script>
import AuthComponent from './components/AuthComponent.vue'

export default {
  name: 'App',
  components: {
    AuthComponent
  },
  data() {
    return {
      isAuthenticated: false,
      currentUser: null,
      formData: {
        text: '',
        voice: 'zh-CN-YunxiNeural',
        bgmCategory: 'clearance',
        bgm: '/bgm/clearance_01.mp3',
        interval: 5
      },
      audioUrl: '',
      isGenerating: false,
      playingAudio: null,
      audioRefs: [],
      bgmData: {
        clearance: [
          { name: '清仓01', file: '/bgm/clearance_01.mp3' },
          { name: '清仓02', file: '/bgm/clearance_02.mp3' },
          { name: '清仓03', file: '/bgm/clearance_03.mp3' },
          { name: '清仓04', file: '/bgm/clearance_04.mp3' },
          { name: '清仓05', file: '/bgm/clearance_05.mp3' },
          { name: '清仓06', file: '/bgm/clearance_06.mp3' },
          { name: '清仓07', file: '/bgm/clearance_07.mp3' },
          { name: '清仓08', file: '/bgm/clearance_08.mp3' }
        ],
        food: [
          { name: '美食01', file: '/bgm/food_01.mp3' },
          { name: '美食02', file: '/bgm/food_02.mp3' },
          { name: '美食03', file: '/bgm/food_03.mp3' },
          { name: '美食04', file: '/bgm/food_04.mp3' },
          { name: '美食05', file: '/bgm/food_05.mp3' },
          { name: '美食06', file: '/bgm/food_06.mp3' },
          { name: '美食07', file: '/bgm/food_07.mp3' },
          { name: '美食08', file: '/bgm/food_08.mp3' }
        ],
        fruits: [
          { name: '水果01', file: '/bgm/fruits_01.mp3' },
          { name: '水果02', file: '/bgm/fruits_02.mp3' },
          { name: '水果03', file: '/bgm/fruits_03.mp3' },
          { name: '水果04', file: '/bgm/fruits_04.mp3' },
          { name: '水果05', file: '/bgm/fruits_05.mp3' },
          { name: '水果06', file: '/bgm/fruits_06.mp3' },
          { name: '水果07', file: '/bgm/fruits_07.mp3' },
          { name: '水果08', file: '/bgm/fruits_08.mp3' }
        ],
        clothing: [
          { name: '服装01', file: '/bgm/clothing_01.mp3' },
          { name: '服装02', file: '/bgm/clothing_02.mp3' },
          { name: '服装03', file: '/bgm/clothing_03.mp3' },
          { name: '服装04', file: '/bgm/clothing_04.mp3' },
          { name: '服装05', file: '/bgm/clothing_05.mp3' },
          { name: '服装06', file: '/bgm/clothing_06.mp3' },
          { name: '服装07', file: '/bgm/clothing_07.mp3' },
          { name: '服装08', file: '/bgm/clothing_08.mp3' }
        ],
        supermarket: [
          { name: '超市01', file: '/bgm/supermarket_01.mp3' },
          { name: '超市02', file: '/bgm/supermarket_02.mp3' },
          { name: '超市03', file: '/bgm/supermarket_03.mp3' },
          { name: '超市04', file: '/bgm/supermarket_04.mp3' },
          { name: '超市05', file: '/bgm/supermarket_05.mp3' },
          { name: '超市06', file: '/bgm/supermarket_06.mp3' },
          { name: '超市07', file: '/bgm/supermarket_07.mp3' },
          { name: '超市08', file: '/bgm/supermarket_08.mp3' }
        ]
      }
    }
  },
  computed: {
    currentBgmList() {
      return this.bgmData[this.formData.bgmCategory] || []
    }
  },
  watch: {
    'formData.bgmCategory': function(newCategory) {
      // 切换分类时，默认选择第一个背景音乐
      if (this.bgmData[newCategory] && this.bgmData[newCategory].length > 0) {
        this.formData.bgm = this.bgmData[newCategory][0].file
      }
    }
  },
  mounted() {
    // 检查本地存储中的认证状态
    this.checkAuthStatus()
  },
  methods: {
    checkAuthStatus() {
      const token = localStorage.getItem('auth_token')
      const user = localStorage.getItem('current_user')
      
      if (token && user) {
        this.isAuthenticated = true
        this.currentUser = JSON.parse(user)
      }
    },
    
    handleAuthSuccess(user) {
      this.isAuthenticated = true
      this.currentUser = user
    },
    
    handleLogout() {
      // 清除本地存储
      localStorage.removeItem('auth_token')
      localStorage.removeItem('current_user')
      
      // 重置状态
      this.isAuthenticated = false
      this.currentUser = null
    },

    togglePreview(audio) {
      if (!audio) return
      
      // 停止之前播放的音频
      if (this.playingAudio && this.playingAudio !== audio) {
        this.playingAudio.pause()
      }
      
      if (audio.paused) {
        audio.play()
        this.playingAudio = audio
      } else {
        audio.pause()
        this.playingAudio = null
      }
      
      // 监听播放结束事件
      audio.onended = () => {
        this.playingAudio = null
      }
    },
    
    async downloadAudio() {
      if (!this.audioUrl) {
        alert('请先生成音频')
        return
      }
      
      try {
        const response = await fetch(this.audioUrl)
        if (!response.ok) {
          throw new Error('下载失败')
        }
        
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = '叫卖录音.mp3'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('下载失败:', error)
        alert('下载失败，请重试')
      }
    },
    
    async generateAudio() {
      if (!this.formData.text.trim()) {
        alert('请输入叫卖文案')
        return
      }
      
      this.isGenerating = true
      try {
        // 获取认证token
        const token = localStorage.getItem('token')
        const headers = {
          'Content-Type': 'application/json'
        }
        
        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }
        
        // 调用后端API
        const response = await fetch('http://localhost:8000/api/generate', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(this.formData)
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            alert('认证过期，请重新登录')
            this.handleLogout()
            return
          }
          throw new Error('服务器响应错误')
        }
        
        const data = await response.json()
        // 使用正确的API路径获取音频文件
        this.audioUrl = `http://localhost:8000/api${data.url}`
      } catch (error) {
        console.error('生成音频失败:', error)
        alert('生成音频失败，请重试')
      } finally {
        this.isGenerating = false
      }
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-app {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.app-header {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  color: #e74c3c;
  margin-bottom: 5px;
  font-size: 24px;
}

.header-left .app-description {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #333;
  font-weight: 500;
}

.logout-btn {
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background: #c0392b;
}

.form-container {
  background-color: white;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: #333;
}

.text-input,
.select-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.text-input:focus,
.select-input:focus {
  outline: none;
  border-color: #e74c3c;
}

.bgm-selector {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-select {
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.bgm-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 6px;
}

.bgm-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  cursor: pointer;
  transition: all 0.3s;
}

.bgm-item:hover {
  background-color: #f0f0f0;
}

.bgm-item.active {
  border-color: #e74c3c;
  background-color: #fff5f5;
}

.preview-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 2px;
}

.range-input {
  width: 100%;
  margin: 10px 0;
}

.interval-hint {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.generate-btn {
  width: 100%;
  padding: 15px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.generate-btn:hover:not(:disabled) {
  background-color: #c0392b;
}

.generate-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.player-container {
  margin-top: 30px;
  background-color: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.player-container h3 {
  margin-bottom: 15px;
  color: #333;
}

.audio-player {
  width: 100%;
  margin-bottom: 15px;
}

.download-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: #2980b9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-app {
    padding: 10px;
  }
  
  .form-container {
    padding: 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .bgm-list {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}

@media (max-width: 480px) {
  .header-left h1 {
    font-size: 20px;
  }
  
  .form-container {
    padding: 15px;
  }
}
</style>