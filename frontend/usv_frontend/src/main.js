import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import BaiduMap from 'vue-baidu-map-3x'

const app = createApp(App)

app.use(ElementPlus)
app.use(BaiduMap, {
  ak: 'HdEfQivILyrLYWzwWNeWrzRjAE91tvPY'
})
app.mount('#app')
