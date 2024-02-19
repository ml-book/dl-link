<template>
  <div>
    <el-divider />
      <el-button @click="CommunicationService.Button" type="primary">RunButton向Executer发包</el-button>
    <el-divider />
  </div>

  <el-dialog v-model="CommunicationService.showConnectInfoWindow" title="连接地址" :show-close="false">
    <el-form label-width="40px">
      <el-form-item label="Url">
        <el-input v-model="CommunicationService.connectUrl" />
      </el-form-item>
      <el-form-item label="Port">
        <el-input v-model="CommunicationService.connectPort" />
      </el-form-item>
    </el-form>
    <el-button type="primary" @click="CommunicationService.Connect">连接</el-button>
  </el-dialog>
</template>

<script setup lang="ts">

import {CommunicationService} from '../types/CommunicationService';

</script>

<style scoped>
.running-res {
  text-align: left;
  width: 100%;
  font-size: large;
}
</style>
