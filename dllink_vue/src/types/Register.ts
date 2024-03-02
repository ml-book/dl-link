import { ElMessage } from 'element-plus'
import { Ref,ref } from 'vue';

interface RecvRemotePacket{
    from_addr: string
    to_addr: string
    type: string
    data: string
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
}
  
class ModuleSender{
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
  
export class CSManager{ //注册模块、维护两个字典、把属于客户端的模块都注册到这一边、判断消息的目标地址是server还是client，如果client则不用转发，如果是server则转发到后端是
  static _instance: CSManager
  client: MyClient
  onopenevents: OnOpenEvents
  onmessageevents: OnMessageEvents
  oncloseevents: OnCloseEvents
  onerrorevents: OnErrorEvents
  windowevents: WindowEvents

  functions: Map<string, [any, any]>
  showConnectInfoWindow: Ref<boolean>
  connectUrl: Ref<string>
  connectPort: Ref<string>

  param_config: string

  events: Events
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
    this.events = Events.get_instance()
    this.onopenevents = new OnOpenEvents()
    this.onmessageevents = new OnMessageEvents()
    this.oncloseevents = new OnCloseEvents()
    this.onerrorevents = new OnErrorEvents()
    this.windowevents = new WindowEvents()

    this.functions = new Map();
    
    this.showConnectInfoWindow = ref(true)

    this.param_config = ''
    this.connectUrl = ref('127.0.0.1')
    this.connectPort = ref('9876')
    this.ws = new WebSocket('ws://' + this.connectUrl.value + ':' + this.connectPort.value)
  }

  register(on_recv_func: Function, addr: string) {
    var sender = new ModuleSender(this, addr)
    this.functions.set(addr, [on_recv_func, sender])
    return sender
  }

  connect = () => {
    this.ws = new WebSocket('ws://' + this.connectUrl.value + ':' + this.connectPort.value)
    if (this.ws != null){
      this.ws.onopen = () => {
        for(let event of this.events.eventsList.get('onopenevents').function.values()){
          event(this.ws)
        }
        this.showConnectInfoWindow.value = false
      } 
    
      this.ws.onmessage = (evt) => {
        for(let event of this.events.eventsList.get('onmessageevents').function.values()){
          event(this.ws, evt)
        }
      }
    
      this.ws.onclose = () => {
        for(let event of this.events.eventsList.get('oncloseevents').function.values()){
          event(this.ws)
        }
      }
    
      this.ws.onerror = () => {
        for(let event of this.events.eventsList.get('onerrorevents').function.values()){
          event(this.ws)
        }
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
    else if (this.client.route_table.has(packet.to_addr.split("/")[0]) || this.client.route_table.has(packet.to_addr)) {

      to_ip = getdefault(this.client.route_table, packet.to_addr.split("/")[0])
      socket = getdefault(this.client.links, to_ip)

      socket.send(JSON.stringify(packet))

    }
    else {
      console.log("没有目标")
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
    // console.log("line 276: " + this.sender)//this.sender 是undefined
    var cs:CSManager = CSManager.get_instance()
    const elmessage = getdefault(cs.events.eventsList, 'windowevents').function
    getdefault(elmessage, 'sendSuccessEvent')()

    await this.sender.send(config, to_addr)// "server0/executer"
  }
  
}
  
class RecvServer {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.on_recv, cs.client.addr_prefix+"/recv-server")
  }

  on_recv(config: string){
    console.log("server发来的消息是: " + config)
  }
}
  
class Printer {
  sender: ModuleSender

  constructor(){
    var cs:CSManager = CSManager.get_instance()
    this.sender = cs.register(this.on_recv, cs.client.addr_prefix+"/printer")
  }

  on_recv(config: string){
    console.log("执行日志: " + config)
  }
}

class Events{
  static _instance: Events
  eventsList: Map<string, any>

  static get_instance(){
    if (Events._instance != null){
      return Events._instance
    }
    else {
      Events._instance = new Events()
      return Events._instance
    }
  }

  constructor() {
    this.eventsList = new Map()
  }

  registerEvents(sub_event: any){
    this.eventsList.set(sub_event.eventName, sub_event)
  }

  // 公共的部分，比如执行所有时间，大家都是遍历，除了onmessage其它的事件参数差不多，可以直接重写onmessage override

}

class WindowEvents{
  eventName: string
  function: Map<string, Function>
  events: Events

  constructor() {
    this.events = Events.get_instance()
    this.eventName = 'windowevents'
    this.function = new Map()
    this.events.registerEvents(this)
    
    this.registerInMap()
  }

  registerInMap(){
    this.function.set(this.windowErrorEvents.name, (content: string) => this.windowErrorEvents(content))
    this.function.set(this.windowSuccessEvent.name, () => this.windowSuccessEvent())
    this.function.set(this.sendSuccessEvent.name, () => this.sendSuccessEvent())
  }

  windowErrorEvents(content: string){
    ElMessage.error(content)
  }

  windowSuccessEvent(){
    ElMessage({
      message: '连接成功',
      type: 'success',
    })
  }

  sendSuccessEvent(){
    ElMessage({
      message: '发送成功',
      type: 'success',
    })
  }

}

class OnOpenEvents{
  eventName: string
  function: Map<string, Function>
  events: Events

  constructor() {
    this.events = Events.get_instance()
    this.eventName = 'onopenevents'
    this.function = new Map()
    this.events.registerEvents(this)

    this.registerInMap()
  }

  registerInMap(){
    this.function.set(this.connectEvent.name, (ws: WebSocket) => this.connectEvent(ws))
    this.function.set(this.connectMessageSendEvent.name, (ws: WebSocket) => this.connectMessageSendEvent(ws))
  }

  connectEvent(ws: WebSocket){
    let cs = CSManager.get_instance()
    const elmessage = getdefault(this.events.eventsList, 'windowevents').function
    getdefault(elmessage, 'windowSuccessEvent')()

    // setup link info
    cs.client.links.set(
        cs.connectUrl + ':' + cs.connectPort,
        ws
    )
  }

  connectMessageSendEvent(ws: WebSocket){
    ws.send(JSON.stringify({
        from_addr: 'client0', // 这里先直接填入，应该考虑起名的问题
        to_addr: '',
        type: 'connection',
        data: 'Hello!'
    }))
  }

}

class OnMessageEvents{
  eventName: string
  function: Map<string, Function>
  events: Events

  constructor() {
    this.events = Events.get_instance()
    this.eventName = 'onmessageevents'
    this.function = new Map()
    this.events.registerEvents(this)

    this.registerInMap()
  }

  registerInMap(){
    this.function.set(this.connectMessageRecvEvent.name, (ws: WebSocket, evt: any) => this.connectMessageRecvEvent(ws, evt))
    this.function.set(this.paramMessageEvent.name, (ws: WebSocket, evt: any) => this.paramMessageEvent(ws, evt))
    this.function.set(this.dataMessageEvent.name, (ws: WebSocket, evt: any) => this.dataMessageEvent(ws, evt))
  }

  connectMessageRecvEvent(ws: WebSocket, evt: any){
    let cs = CSManager.get_instance()
    let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
    if (ws.CONNECTING === 0){
        // 整个连接过程中只有两个方向完全相反的connection包，它传递后端虚拟地址
        if (received_msg.type === 'connection') {
            // setup link info
            cs.client.route_table.set(
                received_msg.from_addr,
                cs.connectUrl + ':' + cs.connectPort
            )

            // 收到之后在返回ack，让服务器发参数
            ws.send(JSON.stringify({
                from_addr: 'client0', // 这里先直接填入，应该考虑起名的问题
                to_addr: '',
                type: 'pre-param',
                data: 'ACK'
            }))

        }
    }
    else {
        console.error(received_msg.data);
    }
  }

  paramMessageEvent(ws: WebSocket, evt: any){
    let cs = CSManager.get_instance()
    let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
    if (ws.CONNECTING === 0){
        if (received_msg.type === 'param'){
            // 接收后端传过来的参数
            console.log(received_msg.data)
            cs.param_config = received_msg.data
        }
    }
    else {
        console.error(received_msg.data);
    }
  }

  dataMessageEvent(ws: WebSocket, evt: any){
    let cs = CSManager.get_instance()
    // json的格式必须是内部双引号
    // console.log(evt.data.replaceAll("'", '"'))
    let received_msg = JSON.parse(evt.data.replaceAll("'", '"'));
    // console.log(received_msg)
    
    if (ws.CONNECTING === 0) {
        const received_msg_data = received_msg.data

        if (received_msg.type === 'string') {
            cs.forward(received_msg)
        }

        else if (received_msg.type === 'has_link'){ // 目前没用
            let to_ip, socket
            const received_msg_addr = received_msg.to_addr

            if (cs.client.route_table.has(received_msg_addr.spilt("/")[0]) || cs.client.route_table.has(received_msg_addr)){
                to_ip = getdefault(cs.client.route_table, received_msg_data("/")[0])
                socket = getdefault(cs.client.links, to_ip)
                socket.send(evt.data)
            }
            else {
                console.log("没有目标地址")
            }
        }
    } 

    else {
        console.error(received_msg.data);
    }
  }

}

class OnCloseEvents{
  eventName: string
  function: Map<string, Function>
  events: Events

  constructor() {
    this.events = Events.get_instance()
    this.eventName = 'oncloseevents'
    this.function = new Map()
    this.events.registerEvents(this)

    this.registerInMap()
  }

  registerInMap(){
    this.function.set(this.closeEvent.name, () => this.closeEvent())
  }

  closeEvent(){
    let cs = CSManager.get_instance()
    cs.showConnectInfoWindow.value = true
    const elmessage = getdefault(this.events.eventsList, 'windowevents').function
    getdefault(elmessage, 'windowErrorEvents')('连接断开')
  }

}

class OnErrorEvents{
  eventName: string
  function: Map<string, Function>
  events: Events

  constructor() {
    this.events = Events.get_instance()
    this.eventName = 'onerrorevents'
    this.function = new Map()
    this.events.registerEvents(this)

    this.registerInMap()
  }

  registerInMap(){
    this.function.set(this.errorEvent.name, () => this.errorEvent())
  }

  errorEvent(){
    let cs = CSManager.get_instance()
    cs.showConnectInfoWindow.value = true
    const elmessage = getdefault(this.events.eventsList, 'windowevents').function
    getdefault(elmessage, 'windowErrorEvents')('连接失败(地址错误 / 协议错误 / 服务器错误)')
  }
}
