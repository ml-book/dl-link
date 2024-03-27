import { Ref,ref } from 'vue';
import { ElMessage } from 'element-plus';
import {EventsManager, SubOnOpenConnect, SubOnOpenMessage, SubOnMessageConnect, SubOnMessageParam,
        SubOnMessageData, SubOnCloseClose, SubOnErrorError} from './KeyEvents'

interface RecvRemotePacket{
    from_addr: string
    to_addr: string
    type: string
    data: string|Map<string,string>
}

function getdefault(map: Map<any, any>, key: any|string){
    if (map.has(key)){
      return map.get(key)
    }
    else { 
      console.error(key + " does not exist as a key")
    }
}

class MyClient{
    static _instance: MyClient
    addr_prefix: string
    links: Map<string, any>
    route_table: Map<string, string>
  
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

    has_link(packet: RecvRemotePacket): boolean{
      let cs: CSManager = CSManager.get_instance()
      if(cs.client.route_table.has(packet.to_addr.split("/")[0]) || cs.client.route_table.has(packet.to_addr)){
        return true
      }
      else{
        return false
      }
    }
}
  
class ModuleSender{
  module_addr: string
  manager: any

  constructor(manager:any, module_addr: string) {
    this.manager = manager
    this.module_addr = module_addr
  }

  async send(data: string, addr:string){
    // 构造packet
    var packet: RecvRemotePacket = {
      from_addr: this.module_addr,
      to_addr: addr,
      type: 'string',
      data: data
    }

    await this.manager.forward(packet)
  }
}
  
export class CSManager{
  static _instance: CSManager|null = null
  client: MyClient
  events: EventsManager

  subonopen_connect: SubOnOpenConnect 
  subonopen_message: SubOnOpenMessage
  subonmessage_connect: SubOnMessageConnect
  subonmessage_param: SubOnMessageParam
  subonmessage_data: SubOnMessageData
  subonclose_close: SubOnCloseClose
  subonerror_error: SubOnErrorError

  functions: Map<string, [any, any]>
  showConnectInfoWindow: Ref<boolean>
  connectUrl: Ref<string>
  connectPort: Ref<string>
  param_config: string

  ws: WebSocket|null

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
    this.client = MyClient.get_instance()
    this.events = EventsManager.get_instance()

    this.subonopen_connect = new SubOnOpenConnect()
    this.subonopen_message = new SubOnOpenMessage()
    this.subonmessage_connect = new SubOnMessageConnect()
    this.subonmessage_param = new SubOnMessageParam()
    this.subonmessage_data = new SubOnMessageData()
    this.subonclose_close = new SubOnCloseClose()
    this.subonerror_error = new SubOnErrorError()

    this.functions = new Map();
    this.showConnectInfoWindow = ref(true)
    this.param_config = ''
    this.connectUrl = ref('127.0.0.1')
    this.connectPort = ref('9876')
    this.ws = null
  }

  register(on_recv_func: Function, addr: string) {
    var sender = new ModuleSender(this, addr)
    this.functions.set(addr, [on_recv_func, sender])
    return sender
  }

  connect = () => { 
    try{
      this.ws = new WebSocket('ws://' + this.connectUrl.value + ':' + this.connectPort.value)
    }
    catch{
      this.events.run(this.events.onerror_events, 'SubOnErrorError', this.ws, '')
      console.error('WebSocket building failed.')
    }
    if (this.ws != null){
      this.ws.onopen = (evt) => {
        this.events.run(this.events.onopen_events, 'SubOnOpenConnect', this.ws, evt)
        this.events.run(this.events.onopen_events, 'SubOnOpenMessage', this.ws, evt)
        this.showConnectInfoWindow.value = false
      } 
    
      this.ws.onmessage = (evt) => {
        let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
        if (received_msg.type === 'connection'){
          this.events.run(this.events.onmessage_events, 'SubOnMessageConnect', this.ws, received_msg)  
        }
        else if(received_msg.type === 'param'){
          this.events.run(this.events.onmessage_events, 'SubOnMessageParam', this.ws, received_msg)
        }
        else if(received_msg.type === 'string'){
          this.events.run(this.events.onmessage_events, 'SubOnMessageData', this.ws, received_msg)
        }
      }
    
      this.ws.onclose = (evt) => {
        this.events.run(this.events.onclose_events, 'SubOnCloseClose', this.ws, evt)
      }
    
      this.ws.onerror = (evt) => {
        this.events.run(this.events.onerror_events, 'SubOnErrorError', this.ws, evt)
      }
    }
    else{
      console.error("ws is possibly 'null'")
    }
  }

  async forward(packet: RecvRemotePacket): Promise<void> {
    const addr = packet.to_addr;
    var to_ip, socket;
    
    // 如果目标在本机
    if (this.functions.has(addr)) {
      const on_recv = getdefault(this.functions, addr)[0]
      on_recv(packet.data)
    } 

    // 如果目标不在本机，发给后端server
    else if (this.client.has_link(packet)) {

      to_ip = getdefault(this.client.route_table, packet.to_addr.split("/")[0])
      socket = getdefault(this.client.links, to_ip)

      socket.send(JSON.stringify(packet))

    }
    else {
      console.error("没有目标")
    }
  }
}
  
export class RunButton {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.run, cs.client.addr_prefix+"/run-button")
  }

  async run(config: string, to_addr: string): Promise<void>{
    ElMessage({
      message: '发送成功',
      type: 'success',
    })
    await this.sender.send(config, to_addr)// "server0/executer"
  }
  
}
  
class SimulatePrinter {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.on_recv, cs.client.addr_prefix+"/printer")
  }

  on_recv(config: string){
    console.log("执行日志: " + config)
  }
}
