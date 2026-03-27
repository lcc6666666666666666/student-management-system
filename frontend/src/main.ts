import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import { router } from './router'
import { pinia } from './store'
import './styles/index.css'
import './styles/element.css'

createApp(App).use(pinia).use(router).use(ElementPlus).mount('#app')
