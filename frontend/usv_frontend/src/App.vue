<script setup>
import TopBar from './components/TopBar.vue'
import LeftSidebar from './components/LeftSidebar.vue'
import RightSidebar from './components/RightSidebar.vue'
</script>

<template>
  <!--顶部信息栏-->
  <TopBar/>

  <!--底部信息栏-->
  <div style="display: flex;">
    <!--底部左侧栏-->
    <LeftSidebar/>
    <!--底部右侧栏-->
    <RightSidebar/>
  </div>
</template>

<style scoped></style>
