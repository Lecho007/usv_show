<script setup lang="ts">
import '../assets/LeftSidebarCss.css'
import axios from 'axios'
import { ref, onMounted, onUnmounted } from 'vue'

const AllRadarData = ref<any>(null)
const AllGpsData = ref<any>(null)
let timer: number | undefined = undefined

// 获取所有的激光雷达数据
function fetchAllRadarFrames() {
  axios.get('/api/radar/all')
    .then(res => {
      AllRadarData.value = res.data
    })
    .catch(err => {
      console.error('获取雷达帧失败：', err)
    })
}
// 获取所有的gps数据
function fetchAllGpsData() {
  axios.get('/api/gps/all')
    .then(res => {
      AllGpsData.value = res.data
    })
    .catch(err => {
      console.error('获取 GPS 数据失败:', err)
    })
}

// 保存 JSON 数据到本地
function saveToFile(data: any, filename: string) {
  if (!data) {
    alert('暂无数据，请先获取！')
    return
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// 定时任务启动
onMounted(() => {
  // 初始化立即拉取一次
  fetchAllRadarFrames()
  fetchAllGpsData()

  // 每隔 5 秒自动刷新
  timer = window.setInterval(() => {
    fetchAllRadarFrames()
    fetchAllGpsData()
  }, 5000)
})

// 页面卸载时清理定时器
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

</script>

<template>
  <div id="LeftSidebar_box">
    <!--无人船信息盒子-->
    <div class="usv_name_box">
      <div class="state_Box" style="margin-top: 47px"></div>
      <div class="font_box">
        USV
      </div>
      <el-tag type="danger" style="margin-top: 40px">状态信息</el-tag>
    </div>
    <!--GPS传感器信息盒子-->
    <div class="sensor_box">
      <div class="sensor_font_box">
        GPS传感器信息
        <!--问号弹出框-->
        <el-popover content="用户可以在此处查看GPS传感器的状态，下载USV的GPS信息" placement="bottom">
          <template #reference><el-button size="small" circle style="width: 15px;height: 15px">?</el-button></template>
        </el-popover>
      </div>
      <div class="sensor_font_box">
        型号：维特智能WTRTK-960模块
      </div>
      <!--下载按钮-->
      <el-button type="primary" style="width: 100%;height: 40px;background-color: #0066FFFF;margin-top: 10px" @click="saveToFile(AllGpsData, 'gps_data.json')">下载GPS数据</el-button>
    </div>
    <!--GPS传感器信息盒子-->
    <div class="sensor_box">
      <div class="sensor_font_box">
        激光雷达信息
        <!--问号弹出框-->
        <el-popover content="用户可以在此处查看激光雷达传感器的状态，下载USV的激光雷达的信息" placement="bottom">
          <template #reference><el-button size="small" circle style="width: 15px;height: 15px">?</el-button></template>
        </el-popover>
      </div>
      <div class="sensor_font_box">
        型号：MS200p
      </div>
      <!--下载按钮-->
      <el-button type="primary" style="width: 100%;height: 40px;background-color: #0066FFFF;margin-top: 10px" @click="saveToFile(AllRadarData, 'radar_data.json')">下载LiDAR数据</el-button>
    </div>
  </div>

</template>

<style scoped>

</style>