<script setup lang="ts">
import '../assets/RightSidebarCss.css'
import '../assets/RightSidebarCss.css'
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

// -------------------- GPS --------------------
// 默认中心点（北京）
let mapInstance: any = null
let BMapGLRef: any = null
let timer: number | undefined
const gpsData = ref<any>(null)

const center = ref({ lng: 116.404, lat: 39.915 })
const marker = ref(center.value)
const zoom = ref(15)

function fetchGPS() {
  axios.get('/api/gps/last')
    .then(res => {
      const data = res.data
      gpsData.value = res.data
      console.log('获取到的 GPS 数据：', data)
      if (data && data.latitude && data.longitude) {
        const newPos = { lng: data.longitude, lat: data.latitude }
        marker.value = newPos
        center.value = newPos
        if (mapInstance && BMapGLRef) {
          mapInstance.panTo(new BMapGLRef.Point(newPos.lng, newPos.lat))
        }
      }

    })
    .catch(err => {
      console.error('获取 GPS 数据失败：', err)
    })
}

function mapReady({ map, BMap }: any) {
  map.enableScrollWheelZoom(true)
  mapInstance = map
  BMapGLRef = BMap

  // 地图加载完成后启动定时刷新
  fetchGPS()
  timer = window.setInterval(fetchGPS, 5000)
}

// -------------------- Radar --------------------
const canvasRef = ref<HTMLCanvasElement | null>(null)
const radarPoints = ref<RadarPoint[]>([])
let radarTimer: number | undefined

interface RadarPoint {
  angle: number
  distance_mm: number
  intensity: number
}
const RadarData = ref<any>(null)

function fetchRadar() {
  axios.get('/api/radar/latest')
    .then(res => {
      const data = res.data
      RadarData.value = res.data
      console.log('获取到的 radar 数据：', data)
      if (data && data.points) {
        radarPoints.value = data.points
        drawRadarGrid(data.points)
      }
    })
    .catch(err => {
      console.error('获取雷达数据失败：', err)
    })
}

function drawRadarGrid(points: RadarPoint[]) {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const size = 250
  const dpr = window.devicePixelRatio || 1

  // 设置高分屏画布大小
  canvas.width = size * dpr
  canvas.height = size * dpr
  canvas.style.width = size + 'px'
  canvas.style.height = size + 'px'

  ctx.setTransform(1, 0, 0, 1, 0, 0) // 重置缩放
  ctx.scale(dpr, dpr)                // 按 devicePixelRatio 缩放

  const centerX = size / 2
  const centerY = size / 2
  const gridSize = 25
  const maxDistance = Math.max(...points.map(p => p.distance_mm))
  const scale = (size/2) / maxDistance

  // 清空画布
  ctx.clearRect(0, 0, size, size)

  // 绘制网格
  ctx.strokeStyle = '#ccc'
  ctx.lineWidth = 0.5
  for (let x = 0; x <= size; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, size)
    ctx.stroke()
  }
  for (let y = 0; y <= size; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(size, y)
    ctx.stroke()
  }

  // 绘制中心点
  ctx.fillStyle = 'black'
  ctx.fillRect(centerX - 3, centerY - 3, 6, 6)

  // 绘制雷达点云
  points.forEach(p => {
    const angleRad = (p.angle - points[0].angle) * Math.PI / 180
    const distance = p.distance_mm * scale
    const x = centerX + distance * Math.cos(angleRad)
    const y = centerY - distance * Math.sin(angleRad)

    ctx.fillStyle = 'red'
    ctx.fillRect(x - 1, y - 1, 2, 2)
  })
}

// 页面加载后初始化
onMounted(() => {
  fetchRadar()
  radarTimer = window.setInterval(fetchRadar, 5000)
})


onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (radarTimer) clearInterval(radarTimer)
})

</script>

<template>
  <div id="RightSidebar_box">
    <!--地图盒子-->
    <div class="Map_box" id="map_container">
      <!-- 引入百度地图 -->
      <baidu-map
        class="bm-view"
        :center="center"
        :zoom="15"
        @ready="mapReady"
      >
        <!-- 添加标记点 -->
        <bm-marker :position="center"/>
      </baidu-map>
    </div>
    <!--传感器信息盒子-->
    <div class="sensor_information_box" >
      <!--GPS信息盒子-->
      <div class="gps_information_box">
        <div style="width: 100%;height: 10%;display: flex;font-size: 20px;font-weight: 550;margin-top: 10px">
          <div class="state_Box" style="margin-top: 12px;margin-left: 10px"></div>
          当前 GPS 数据：
        </div>
        <div style="width: 300px;height: 80%;margin-left: 90px;">
          <p>纬度: {{ gpsData?.latitude }}</p>
          <p>经度: {{ gpsData?.longitude }}</p>
          <p>高度: {{ gpsData?.altitude }}</p>
          <p>卫星数量: {{ gpsData?.satellites }}</p>
          <p>UTC 时间: {{ gpsData?.utc_time }}</p>
        </div>
      </div>
      <!--激光雷达信息盒子-->
      <div class="lidar_information_box">
        <div style="width: 100%;height: 10%;display: flex;font-size: 20px;font-weight: 550;margin-top: 10px;">
          <div class="state_Box" style="margin-top: 12px;margin-left: 10px"></div>
          当前 lidar 数据：
        </div>
        <div style="width:100%;display: flex">
          <div style="width: 250px; height: 80%; margin-left: 90px;">
            <p>点数量: {{ RadarData?.point_count ?? 0 }}</p>
            <p>起始角度: {{ RadarData?.start_angle }}</p>
            <p>结束角度: {{ RadarData?.end_angle }}</p>
            <p>RPM: {{ RadarData?.rpm }}</p>
            <p>时间戳: {{ RadarData?.timestamp }}</p>
          </div>
          <canvas ref="canvasRef" width="250" height="250"></canvas>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>

</style>