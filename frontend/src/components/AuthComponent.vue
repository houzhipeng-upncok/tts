<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>{{ isLogin ? '用户登录' : '用户注册' }}</h2>
        <div class="auth-tabs">
          <button 
            :class="['tab-btn', { active: isLogin }]"
            @click="switchToLogin"
          >
            登录
          </button>
          <button 
            :class="['tab-btn', { active: !isLogin }]"
            @click="switchToRegister"
          >
            注册
          </button>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            :disabled="loading"
            placeholder="请输入用户名"
            :class="{ error: errors.username }"
          >
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            :disabled="loading"
            :placeholder="isLogin ? '请输入密码' : '密码至少8位'"
            :class="{ error: errors.password }"
          >
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          <div v-if="!isLogin" class="password-hint">
            密码长度至少8位，建议包含字母和数字
          </div>
        </div>

        <div v-if="!isLogin" class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            required
            :disabled="loading"
            placeholder="请再次输入密码"
            :class="{ error: errors.confirmPassword }"
          >
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <div v-if="errors.general" class="general-error">
          {{ errors.general }}
        </div>

        <button 
          type="submit" 
          class="submit-btn"
          :disabled="loading"
        >
          {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <div v-if="isLogin" class="auth-footer">
        <p>还没有账号？<a href="#" @click.prevent="switchToRegister">立即注册</a></p>
      </div>
      <div v-else class="auth-footer">
        <p>已有账号？<a href="#" @click.prevent="switchToLogin">立即登录</a></p>
      </div>
    </div>

    <!-- 成功消息 -->
    <div v-if="successMessage" class="success-overlay">
      <div class="success-card">
        <div class="success-icon">✓</div>
        <h3>{{ successMessage }}</h3>
        <p v-if="isLogin">正在跳转到主页面...</p>
        <p v-else>注册成功！正在登录...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthComponent',
  data() {
    return {
      isLogin: true,
      loading: false,
      successMessage: '',
      form: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      errors: {
        username: '',
        password: '',
        confirmPassword: '',
        general: ''
      }
    }
  },
  methods: {
    switchToLogin() {
      this.isLogin = true
      this.clearForm()
      this.clearErrors()
    },

    switchToRegister() {
      this.isLogin = false
      this.clearForm()
      this.clearErrors()
    },

    clearForm() {
      this.form = {
        username: '',
        password: '',
        confirmPassword: ''
      }
    },

    clearErrors() {
      this.errors = {
        username: '',
        password: '',
        confirmPassword: '',
        general: ''
      }
    },

    validateForm() {
      this.clearErrors()
      let isValid = true

      // 验证用户名
      if (!this.form.username.trim()) {
        this.errors.username = '请输入用户名'
        isValid = false
      } else if (this.form.username.length < 1 || this.form.username.length > 13) {
        this.errors.username = '用户名长度必须在1-13个字符之间'
        isValid = false
      }

      // 验证密码
      if (!this.form.password) {
        this.errors.password = '请输入密码'
        isValid = false
      } else if (!this.isLogin && this.form.password.length < 8) {
        this.errors.password = '密码长度至少8位'
        isValid = false
      }

      // 验证确认密码（仅注册时）
      if (!this.isLogin) {
        if (!this.form.confirmPassword) {
          this.errors.confirmPassword = '请确认密码'
          isValid = false
        } else if (this.form.password !== this.form.confirmPassword) {
          this.errors.confirmPassword = '两次输入的密码不一致'
          isValid = false
        }
      }

      return isValid
    },

    async handleSubmit() {
      if (!this.validateForm()) {
        return
      }

      this.loading = true
      this.clearErrors()

      try {
        const endpoint = this.isLogin ? '/api/auth/login' : '/api/auth/register'
        const payload = {
          username: this.form.username,
          password: this.form.password
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        const data = await response.json()

        if (!response.ok) {
          if (response.status === 400) {
            this.errors.general = data.detail || '用户名已存在'
          } else if (response.status === 401) {
            this.errors.general = data.detail || '用户名或密码错误'
          } else {
            this.errors.general = '网络错误，请稍后重试'
          }
          return
        }

        // 成功处理
        this.successMessage = data.message
        if (data.token && data.token.access_token) {
          localStorage.setItem('auth_token', data.token.access_token)
          localStorage.setItem('current_user', JSON.stringify(data.user))
        }

        // 显示成功消息，然后跳转到主页面
        setTimeout(() => {
          this.$emit('auth-success', data.user)
        }, 2000)

      } catch (error) {
        console.error('认证错误:', error)
        this.errors.general = '网络错误，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 15px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 24px;
}

.auth-tabs {
  display: flex;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.tab-btn.active {
  background: #e74c3c;
  color: white;
}

.tab-btn:not(.active):hover {
  background: #e8e8e8;
}

.auth-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #e74c3c;
}

.form-group input.error {
  border-color: #e74c3c;
}

.password-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

.error-message {
  display: block;
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
}

.general-error {
  background: #ffe6e6;
  color: #e74c3c;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px;
  text-align: center;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 15px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background: #c0392b;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  color: #666;
}

.auth-footer a {
  color: #e74c3c;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.success-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.success-card {
  background: white;
  border-radius: 15px;
  padding: 40px;
  text-align: center;
  max-width: 300px;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: #27ae60;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  margin: 0 auto 20px;
}

.success-card h3 {
  color: #333;
  margin-bottom: 10px;
}

.success-card p {
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .auth-card {
    padding: 30px 20px;
  }
  
  .auth-header h2 {
    font-size: 20px;
  }
}
</style>