import { ElMessage } from 'element-plus'
import {CSManager} from './Client'

function getdefault(map: Map<any, any>, key: any|string){
    if (map.has(key)){
      return map.get(key)
    }
    else { 
      console.error(key + " does not exist as a key")
    }
}

export class EventsManager{
  static _instance: EventsManager
  onopen_events: OnOpenEvents
  onmessage_events: OnMessageEvents
  onclose_events: OnCloseEvents
  onerror_events: OnErrorEvents

  static get_instance(){
    if (EventsManager._instance != null){
      return EventsManager._instance
    }
    else {
      EventsManager._instance = new EventsManager()
      return EventsManager._instance
    }
  }

  constructor() {
    this.onopen_events = new OnOpenEvents()
    this.onmessage_events = new OnMessageEvents()
    this.onclose_events = new OnCloseEvents()
    this.onerror_events = new OnErrorEvents()
  }

  run(event_type: any, event_name: string, ws: any, evt: any) {
    getdefault(event_type.function, event_name)(ws, evt)
  }

}

class OnOpenEvents{
  function: Map<string, Function>

  constructor() {
    this.function = new Map()
  }

  register(name: string, func: Function) {
    this.function.set(name, func)
  }

}

class OnMessageEvents{
  function: Map<string, Function>

  constructor() {
    this.function = new Map()
  }

  register(name: string, func: Function) {
    this.function.set(name, func)
  }

}

class OnCloseEvents{
  function: Map<string, Function>

  constructor() {
    this.function = new Map()
  }

  register(name: string, func: Function) {
    this.function.set(name, func)
  }

}

class OnErrorEvents{
  function: Map<string, Function>

  constructor() {
    this.function = new Map()
  }

  register(name: string, func: Function) {
    this.function.set(name, func)
  }

}

///////////////////////////////

export class SubOnOpenConnect{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onopen_events.register(this.constructor.name, this.on_run) // register(this)
  }

  on_run(ws: WebSocket, received_msg: any){
    let cs = CSManager.get_instance()
    // setup link info
    cs.client.links.set(
        cs.connectUrl + ':' + cs.connectPort,
        ws
    )
    // windows events
    ElMessage({
      message: '连接成功',
      type: 'success',
    })

  }
}

export class SubOnOpenMessage{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onopen_events.register(this.constructor.name, this.on_run)
  }

  on_run(ws: WebSocket, received_msg: any){
    console.log(ws)
    ws.send(JSON.stringify({
        from_addr: 'client0', // 这里先直接填入，应该考虑起名的问题
        to_addr: '',
        type: 'connection',
        data: 'Hello!'
    }))
  }
}

export class SubOnMessageConnect{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onmessage_events.register(this.constructor.name, this.on_run)
  }

  on_run(ws: WebSocket, received_msg: any){
    let cs = CSManager.get_instance()
    if (ws.CONNECTING === 0){
        // 整个连接过程中只有两个方向完全相反的connection包，它传递后端虚拟地址
          console.log(received_msg.data)
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
    else {
        console.error(received_msg.data);
    }
  }
}

export class SubOnMessageParam{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onmessage_events.register(this.constructor.name, this.on_run)
  }

  on_run(ws: WebSocket, received_msg: any){
    let cs = CSManager.get_instance()
    if (ws.CONNECTING === 0){
        // 接收后端传过来的参数
        console.log(received_msg.data)
        cs.param_config = received_msg.data
    }
    else {
        console.error(received_msg.data);
    }
  }

}

export class SubOnMessageData{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onmessage_events.register(this.constructor.name, this.on_run)
  }

  on_run(ws: WebSocket, received_msg: any){
    let cs = CSManager.get_instance()
    if (ws.CONNECTING === 0) {
        console.log(received_msg.data)
        cs.forward(received_msg)
    } 

    else {
        console.error(received_msg.data);
    }
  }
}

export class SubOnCloseClose{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onclose_events.register(this.constructor.name, this.on_run)
  }

  on_run(ws: WebSocket, received_msg: any) {
    let cs = CSManager.get_instance()
    cs.showConnectInfoWindow.value = true
    // const elmessage = getdefault(this.events.eventsList, 'windowevents').function
    // getdefault(elmessage, 'windowErrorEvents')('连接断开')
    ElMessage.error('连接断开')
  }
}

export class SubOnErrorError{
  constructor() {
    let es: EventsManager = EventsManager.get_instance()
    // 注册事件功能函数到父类中 (类名string，功能函数Function)
    es.onclose_events.register(this.constructor.name, this.on_run)
  }

  on_run(ws: WebSocket, received_msg: any){
    let cs = CSManager.get_instance()
    cs.showConnectInfoWindow.value = true
    ElMessage.error('连接失败(地址错误 / 协议错误 / 服务器错误)')
  }
}