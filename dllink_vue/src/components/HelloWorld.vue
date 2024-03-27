<template>
  <div>
    <el-divider />
      <el-button @click="clickButton" type="primary">RunButton向Executer发包</el-button>
    <el-divider />
  </div>

  <el-dialog v-model="CSManager.get_instance().showConnectInfoWindow.value" title="连接地址" :show-close="false">
    <el-form label-width="40px">
      <el-form-item label="Url">
        <el-input v-model="CSManager.get_instance().connectUrl.value" />
      </el-form-item>
      <el-form-item label="Port">
        <el-input v-model="CSManager.get_instance().connectPort.value" />
      </el-form-item>
    </el-form>
    <el-button type="primary" @click="CSManager.get_instance().connect">连接</el-button>
  </el-dialog>
</template>

<script setup lang="ts">

import {RunButton, CSManager} from '../types/Client'

const clickButton = () => {
  let button = new RunButton()
  // 实际上应该传递前端选择的param_config。这里为了方便直接用后端传过来的param_config。
  if (CSManager.get_instance().param_config === null){
    console.error('"execute_config" is null')
  }
  else{
    button.run(CSManager.get_instance().param_config, "server0/executer")
  }
}

</script>

<style scoped>
.running-res {
  text-align: left;
  width: 100%;
  font-size: large;
}
</style>