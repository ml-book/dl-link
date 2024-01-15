<template>
  <div>
    <div v-for="(value, key) in configDict" :key="key">
      <h2>{{ key }}</h2>
      <div v-if="value.length === 0">没有 {{ key }}</div>
      <el-radio-group v-model="configValue[key]">
        <el-radio v-for="(name, idx) in value" :key="idx" :label="name">{{ name }}</el-radio>
      </el-radio-group>
    </div>

    <el-divider />

    <el-button @click="clickButton1()" type="primary">RunButton向Executer发包</el-button>
    <el-button @click="clickButton2()" type="primary">RunButton向test_local发包</el-button>

    <el-divider />

    <div>
      <h2>运行结果</h2>
      <div class="running-res">
        <div v-for="(content, idx) in runningOutput" :key="idx">
          <p v-if="content.type == 'string'">{{ content.content }}</p>
          <img v-if="content.type == 'image'" :src="'data:image/jpeg;base64,'+content.content" />
        </div>
      </div>
    </div>
  </div>

  <el-dialog v-model="showConnectInfoWindow" title="连接地址" :show-close="false">
    <el-form label-width="40px">
      <el-form-item label="Url">
        <el-input v-model="connectUrl" />
      </el-form-item>
      <el-form-item label="Port">
        <el-input v-model="connectPort" />
      </el-form-item>
    </el-form>
    <el-button type="primary" @click="onClickConnect">连接</el-button>
  </el-dialog>
</template>

<script setup lang="ts">
import { SpawnSyncOptionsWithStringEncoding } from 'child_process';
import { ADDRCONFIG } from 'dns';
import { ElMessage } from 'element-plus'
import { link } from 'fs';
import { ref } from 'vue'

const connectUrl = ref('localhost')
const connectPort = ref('9876')
const showConnectInfoWindow = ref(false)

interface DlFrameConfigInterface {
  [key: string]: string;
}
interface DlFrameInspectionInterface {
  [key: string]: Array<string>;
}
interface RunningOutputInterface {
  [key: string]: string;
}
const runningOutput = ref<Array<RunningOutputInterface>>([])

function getdefault(map: Map<any, any>, key: string){
  if (map.has(key)){
    return map.get(key)
  }
  else {
    console.log("键不存在")
  }
}

let ws: WebSocket | null = null
const connect = () => {
  ws = new WebSocket('ws://' + connectUrl.value + ':' + connectPort.value) //一对多->并行化
  
  ws.onopen = () => {
    isConnectedToServer.value = true
    showConnectInfoWindow.value = false
    ElMessage({
      message: '连接成功',
      type: 'success',
    })

    // setup link info
    client.links.set(
      [connectUrl.value, connectPort.value],
      ws
    )

    ws?.send(JSON.stringify({
      'from_addr': 'client0', // 这里先直接填入，应该考虑起名的问题
      'to_addr': '',
      'type': 'connection',
      'data': 'Hello'
    }))
  }
  ws.onmessage = (evt) => {
    // json的格式必须是内部双引号
    var received_msg = JSON.parse(evt.data.replaceAll("'",'"'));
    console.log(received_msg);
    
    if (ws?.CONNECTING === 0) {
      const received_msg_data = received_msg.data
      if (received_msg.type === 'connection') {
        runningOutput.value = received_msg.data
        // setup link info
        client.route_table.set(
          received_msg.from_addr,
          [connectUrl.value, connectPort.value]
        )

      }

      else if (received_msg.type === 'string') {
        cs.forward(received_msg)
        console.log(received_msg.data)
      }

      else if (received_msg.type === 'has_link'){
        let to_ip, socket
        const received_msg_addr = received_msg.to_addr

        if (client.route_table.has(received_msg_addr.spilt("/")[0]) || client.route_table.has(received_msg_addr)){
          to_ip = getdefault(client.route_table, received_msg_data("/")[0])
          socket = getdefault(client.links, to_ip)
          socket?.send(evt.data)
        }
        else {
          console.log("没有目标地址")
        }
      }

      else if (received_msg.type === 'imshow') {
        runningOutput.value.push({
          'type': 'image', 
          'content': received_msg_data.content
        })
      }
    } else {
      console.error(received_msg.data);
    }
  }
  ws.onclose = () => {
    isConnectedToServer.value = false
    showConnectInfoWindow.value = true
    ElMessage.error('连接已断开')
  }
  ws.onerror = () => {
    ElMessage.error('连接失败(地址错误 / 协议错误 / 服务器错误)')
    showConnectInfoWindow.value = true
  }
}

connect()

const configDict = ref<DlFrameInspectionInterface>({})
const configValue = ref<DlFrameConfigInterface>({})

interface RecvRemotePacket{
  from_addr: string
  to_addr: string
  type: string
  data: string
}

class MyClient{
  static _instance: MyClient
  addr_prefix: string
  links: Map<[string, string], any>
  route_table: Map<string, [string, string]>

  static get_instance(){
    if (MyClient._instance != null){
      return MyClient._instance
    }
    else {
      MyClient._instance = new MyClient()
      return MyClient._instance
    }
  }

  constructor(){
    this.links = new Map();
    this.route_table = new Map()
    this.addr_prefix = 'client0'
  }
}

class ModuleSender{// 目前好像没用
  module_addr: string
  manager: any

  constructor(manager:any, module_addr: string) {
    this.manager = manager
    this.module_addr = module_addr
  }

  async send(data: string, addr:string){
    // 构造RecvRemotePacket
    var packet: RecvRemotePacket = {
      from_addr: this.module_addr,
      to_addr: addr,
      type: 'string',
      data: data
    }

    await this.manager.forward(packet)
  }

}

class CSManager{ //注册模块、维护两个字典、把属于客户端的模块都注册到这一边、判断消息的目标地址是server还是client，如果是client则不用转发，如果是server则转发到后端
  functions: Map<string, [any, any]>
  static _instance: CSManager
  client: MyClient
  
  static get_instance(){
    if (CSManager._instance != null){
      return CSManager._instance
    }
    else {
      CSManager._instance = new CSManager()
      return CSManager._instance
    }
  }

  constructor() {
    this.client = MyClient.get_instance()!
    this.functions = new Map();
  }

  register(on_recv_func: Function, addr: string) {
    var sender = new ModuleSender(this, addr)
    this.functions.set(addr, [on_recv_func, sender])
    return sender
  }

  async forward(packet: RecvRemotePacket): Promise<void> {
    const addr = packet.to_addr;
    var to_ip, socket;

    // 如果目标在本机
    if (this.functions.has(addr)) {
      const on_recv = getdefault(this.functions, addr)![0]
      on_recv(packet.data)
    } 

    // 如果目标不在本机，发给后端server
    else {
      if (packet.from_addr.split("/")[0] == cs.client.addr_prefix){ //由前端发给后端的，直接发就行
        client_send(packet)
      }
      else if(client.route_table.has(packet.to_addr.split("/")[0]) // 需要转发给其它client和server的
          || client.route_table.has(packet.to_addr)){
        to_ip = getdefault(client.route_table, packet.to_addr.split("/")[0])
        socket = getdefault(client.links, to_ip)
        socket?.send(packet)
      }
      else{
        console.log("没有目标")
      }
    }
  }
}

class RunButton {
  sender: ModuleSender

  constructor(){
    var cs = CSManager.get_instance()
    this.sender = cs?.register(this.run, cs?.client.addr_prefix+"/run-button")
  }

  async run(config: string, to_addr: string): Promise<void>{
    var cs = CSManager.get_instance()
    // console.log("line 276: " + this.sender)//this.sender 是undefined
    await this.sender?.send(config, to_addr)// "server0/executer"
  }
}

class Test_local {
  sender: ModuleSender

  constructor(){
    var cs = CSManager.get_instance()
    this.sender = cs?.register(this.on_recv, cs?.client.addr_prefix+"/test-local")
  }

  on_recv(config: string){
    console.log("test_local_on_recv: " + config)
  }
}

const isConnectedToServer = ref(false)
const onClickConnect = () => {
  connect()
}

function client_send(packet: RecvRemotePacket){
  ws?.send(JSON.stringify(packet))
}

const clickButton1 = () => {
  button.run("runbutton -> executer", "server0/executer")
}

const clickButton2 = () => {
  button.run("runbutton -> test_local", "client0/test-local")
}

var client = MyClient.get_instance()
var cs = CSManager.get_instance()

var button = new RunButton()
var local = new Test_local()

</script>

<style scoped>
.running-res {
  text-align: left;
  width: 100%;
  font-size: large;
}
</style>
