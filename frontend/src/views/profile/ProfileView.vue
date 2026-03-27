<script setup lang="ts">
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { fetchAdminProfileApi } from '@/api/admin'
import { fetchStudentProfileApi, updateStudentProfileApi } from '@/api/student'
import { fetchTeacherProfileApi, updateTeacherProfileApi } from '@/api/teacher'
import EmptyState from '@/components/EmptyState.vue'
import PageHero from '@/components/PageHero.vue'
import { useAuthStore } from '@/store/auth'
import type { AdminProfile, StudentProfile, TeacherProfile } from '@/types'

const authStore = useAuthStore()
const role = computed(() => authStore.user?.role)
const loading = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

const studentForm = reactive<StudentProfile>({
  id: 0,
  user_id: 0,
  username: '',
  real_name: '',
  phone: '',
  email: '',
  student_no: '',
  gender: '',
  grade: '',
  class_name: '',
  admission_year: 0,
  department_id: 0,
  department_name: ''
})

const teacherForm = reactive<TeacherProfile>({
  id: 0,
  user_id: 0,
  username: '',
  real_name: '',
  phone: '',
  email: '',
  teacher_no: '',
  title: '',
  office: '',
  department_id: 0,
  department_name: ''
})

const adminProfile = ref<AdminProfile | null>(null)

const rules: FormRules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}

async function loadProfile() {
  loading.value = true
  try {
    if (role.value === 'student') {
      Object.assign(studentForm, await fetchStudentProfileApi())
    } else if (role.value === 'teacher') {
      Object.assign(teacherForm, await fetchTeacherProfileApi())
    } else if (role.value === 'admin') {
      adminProfile.value = await fetchAdminProfileApi()
    }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!formRef.value || role.value === 'admin') return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (role.value === 'student') {
      const data = await updateStudentProfileApi(studentForm)
      Object.assign(studentForm, data)
    } else if (role.value === 'teacher') {
      const data = await updateTeacherProfileApi(teacherForm)
      Object.assign(teacherForm, data)
    }
    await authStore.fetchCurrentUser()
    ElMessage.success('个人信息已更新')
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="page-view" v-loading="loading">
    <PageHero
      title="个人信息"
      description="支持维护当前账号基础资料，不同角色会显示不同的档案字段与权限。"
      tag="资料中心"
    >
      <el-button v-if="role !== 'admin'" type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
    </PageHero>

    <section v-if="role === 'student'" class="panel panel-inner">
      <el-form ref="formRef" :model="studentForm" :rules="rules" label-position="top">
        <el-row :gutter="18">
          <el-col :xs="24" :md="12">
            <el-form-item label="姓名" prop="real_name">
              <el-input v-model="studentForm.real_name" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="用户名">
              <el-input v-model="studentForm.username" disabled />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="学号">
              <el-input v-model="studentForm.student_no" disabled />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="所属院系">
              <el-input v-model="studentForm.department_name" disabled />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="年级">
              <el-input v-model="studentForm.grade" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="班级">
              <el-input v-model="studentForm.class_name" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="8">
            <el-form-item label="性别">
              <el-select v-model="studentForm.gender" placeholder="请选择">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="手机号">
              <el-input v-model="studentForm.phone" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="studentForm.email" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </section>

    <section v-else-if="role === 'teacher'" class="panel panel-inner">
      <el-form ref="formRef" :model="teacherForm" :rules="rules" label-position="top">
        <el-row :gutter="18">
          <el-col :xs="24" :md="12">
            <el-form-item label="姓名" prop="real_name">
              <el-input v-model="teacherForm.real_name" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="用户名">
              <el-input v-model="teacherForm.username" disabled />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="工号">
              <el-input v-model="teacherForm.teacher_no" disabled />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="所属院系">
              <el-input v-model="teacherForm.department_name" disabled />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="职称">
              <el-input v-model="teacherForm.title" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="办公室">
              <el-input v-model="teacherForm.office" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="手机号">
              <el-input v-model="teacherForm.phone" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="teacherForm.email" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </section>

    <section v-else-if="adminProfile" class="panel panel-inner">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="管理员姓名">{{ adminProfile.real_name }}</el-descriptions-item>
        <el-descriptions-item label="账号">{{ adminProfile.username }}</el-descriptions-item>
        <el-descriptions-item label="管理员编号">{{ adminProfile.admin_no }}</el-descriptions-item>
        <el-descriptions-item label="权限级别">{{ adminProfile.level }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ adminProfile.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ adminProfile.email || '-' }}</el-descriptions-item>
      </el-descriptions>
    </section>

    <EmptyState v-else-if="!loading" title="未获取到档案信息" description="请检查当前账号与后端接口状态。" />
  </div>
</template>
