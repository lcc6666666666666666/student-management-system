<script setup lang="ts">
import { Lock, User } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: 'student01',
  password: '123456'
})

const quickAccounts = [
  { label: '学生演示', username: 'student01', password: '123456', desc: '选课 / 退课 / 查看成绩' },
  { label: '教师演示', username: 'teacher01', password: '123456', desc: '授课 / 录入成绩 / 统计分析' },
  { label: '管理员演示', username: 'admin01', password: '123456', desc: '课程管理 / 容量状态维护' }
]

const rules: FormRules<typeof form> = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

function fillAccount(username: string, password: string) {
  form.username = username
  form.password = password
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(form)
    ElMessage.success('登录成功')
    router.replace(authStore.homePath)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-page__glow login-page__glow--left" />
    <div class="login-page__glow login-page__glow--right" />

    <section class="login-hero">
      <div class="login-hero__badge">课程设计演示项目</div>
      <h1>教学管理系统</h1>
      <p>
        面向数据库课程设计场景构建，完整覆盖学生选课、教师录入成绩、管理员课程维护和 SQL 应用展示。
      </p>

      <div class="hero-feature-list">
        <div class="hero-feature">
          <strong>前后端分离</strong>
          <span>Vue 3 + FastAPI + MySQL 8.0</span>
        </div>
        <div class="hero-feature">
          <strong>三角色权限</strong>
          <span>学生、教师、管理员分角色菜单与接口控制</span>
        </div>
        <div class="hero-feature">
          <strong>可演示闭环</strong>
          <span>真实接口联调、初始化数据、统计看板与反馈提示</span>
        </div>
      </div>
    </section>

    <section class="login-panel panel">
      <div class="login-panel__head">
        <h2>欢迎登录</h2>
        <p>使用测试账号即可直接进入演示环境</p>
      </div>

      <div class="quick-entry">
        <button
          v-for="account in quickAccounts"
          :key="account.username"
          class="quick-entry__item"
          @click="fillAccount(account.username, account.password)"
        >
          <strong>{{ account.label }}</strong>
          <span>{{ account.desc }}</span>
        </button>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="login-form">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" size="large" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password placeholder="请输入密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-button type="primary" size="large" class="login-submit" :loading="loading" @click="handleLogin">
          进入系统
        </el-button>
      </el-form>

      <div class="login-tip">默认测试密码统一为 <strong>123456</strong></div>
    </section>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  min-height: 100vh;
  padding: 42px;
  gap: 28px;
  overflow: hidden;
}

.login-page__glow {
  position: absolute;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.35;
}

.login-page__glow--left {
  top: -80px;
  left: -120px;
  background: rgba(37, 99, 235, 0.46);
}

.login-page__glow--right {
  right: -120px;
  bottom: -80px;
  background: rgba(15, 159, 110, 0.32);
}

.login-hero,
.login-panel {
  position: relative;
  z-index: 1;
}

.login-hero {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px 18px;
}

.login-hero__badge {
  display: inline-flex;
  width: fit-content;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
  box-shadow: var(--shadow-card);
}

.login-hero h1 {
  margin: 22px 0 14px;
  font-size: 64px;
  line-height: 1.02;
  letter-spacing: -2px;
}

.login-hero p {
  max-width: 640px;
  color: var(--color-subtitle);
  font-size: 16px;
  line-height: 1.9;
}

.hero-feature-list {
  display: grid;
  gap: 16px;
  max-width: 640px;
  margin-top: 34px;
}

.hero-feature {
  padding: 20px 22px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.74);
  box-shadow: var(--shadow-card);
}

.hero-feature strong {
  display: block;
  margin-bottom: 8px;
  font-size: 18px;
}

.hero-feature span {
  color: var(--color-subtitle);
  line-height: 1.7;
}

.login-panel {
  align-self: center;
  padding: 30px;
}

.login-panel__head h2 {
  margin: 0;
  font-size: 30px;
}

.login-panel__head p {
  margin: 10px 0 0;
  color: var(--color-subtitle);
}

.quick-entry {
  display: grid;
  gap: 12px;
  margin: 26px 0;
}

.quick-entry__item {
  padding: 16px 18px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(248, 251, 255, 0.98), rgba(239, 246, 255, 0.86));
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.quick-entry__item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card);
}

.quick-entry__item strong {
  display: block;
  margin-bottom: 6px;
}

.quick-entry__item span {
  color: var(--color-subtitle);
  font-size: 13px;
}

.login-form {
  margin-top: 12px;
}

.login-submit {
  width: 100%;
  margin-top: 10px;
}

.login-tip {
  margin-top: 18px;
  color: var(--color-subtitle);
  font-size: 13px;
  text-align: center;
}

@media (max-width: 1100px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 22px;
  }

  .login-hero h1 {
    font-size: 48px;
  }
}
</style>
